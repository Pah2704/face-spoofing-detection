"""Torch dataset for the locked OULU-NPU Protocol 1 face-frame manifest.

The module intentionally keeps the CNN input contract small and explicit:
only successfully detected face crops from one requested split are exposed,
all images become 224x224 RGB tensors with ImageNet normalization, and the
only training augmentation is a horizontal flip.  No pandas dependency is
used.

``torch`` and ``torchvision`` are optional project dependencies, so this
module is not imported from :mod:`face_spoofing.data` at package import time.
Import it directly after installing the project's ``deep`` extra.
"""

from __future__ import annotations

from collections import Counter
import csv
from dataclasses import asdict, dataclass
import hashlib
import math
import os
from pathlib import Path
from typing import Any, TypedDict

from PIL import Image, UnidentifiedImageError
import torch
from torch.utils.data import Dataset, get_worker_info
from torchvision.transforms import InterpolationMode
from torchvision.transforms import functional as vision_functional


IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
CNN_IMAGE_SIZE = 224
CNN_TRANSFORM_VERSION = 1
VALID_SPLITS = frozenset({"train", "dev", "test"})

_REQUIRED_FIELDS = frozenset(
    {
        "frame_id",
        "video_id",
        "sample_index",
        "frame_index",
        "split",
        "label",
        "face_path",
        "face_detected",
        "preprocess_fingerprint",
    }
)


class CnnDatasetError(RuntimeError):
    """Raised when the locked frame manifest or a face crop is invalid."""


class CnnFrameItem(TypedDict):
    """One item returned by :class:`CnnFrameDataset`."""

    image: torch.Tensor
    label: torch.Tensor
    frame_id: str
    video_id: str


@dataclass(frozen=True, slots=True)
class CnnTransformConfig:
    """Versioned, texture-preserving transform settings for E02/E03."""

    version: int = CNN_TRANSFORM_VERSION
    image_size: int = CNN_IMAGE_SIZE
    mean: tuple[float, float, float] = IMAGENET_MEAN
    std: tuple[float, float, float] = IMAGENET_STD
    horizontal_flip_probability: float = 0.5
    interpolation: str = "bilinear"
    antialias: bool = True

    def validate(self) -> None:
        if isinstance(self.version, bool) or not isinstance(self.version, int):
            raise TypeError("version must be an integer")
        if self.version != CNN_TRANSFORM_VERSION:
            raise ValueError(
                f"unsupported CNN transform version {self.version}; "
                f"expected {CNN_TRANSFORM_VERSION}"
            )
        if isinstance(self.image_size, bool) or not isinstance(self.image_size, int):
            raise TypeError("image_size must be an integer")
        if self.image_size != CNN_IMAGE_SIZE:
            raise ValueError(f"image_size must be {CNN_IMAGE_SIZE}")
        if len(self.mean) != 3 or len(self.std) != 3:
            raise ValueError("mean and std must contain exactly three values")
        for name, values in (("mean", self.mean), ("std", self.std)):
            for value in values:
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise TypeError(f"{name} values must be numbers")
                if not math.isfinite(float(value)):
                    raise ValueError(f"{name} values must be finite")
        if any(float(value) <= 0.0 for value in self.std):
            raise ValueError("std values must be positive")
        if tuple(float(value) for value in self.mean) != IMAGENET_MEAN:
            raise ValueError(f"mean must be the ImageNet mean {IMAGENET_MEAN}")
        if tuple(float(value) for value in self.std) != IMAGENET_STD:
            raise ValueError(f"std must be the ImageNet std {IMAGENET_STD}")
        probability = self.horizontal_flip_probability
        if isinstance(probability, bool) or not isinstance(probability, (int, float)):
            raise TypeError("horizontal_flip_probability must be a number")
        if not math.isfinite(float(probability)) or not 0.0 <= probability <= 1.0:
            raise ValueError("horizontal_flip_probability must be between 0 and 1")
        if self.interpolation != "bilinear":
            raise ValueError("interpolation must be 'bilinear'")
        if not isinstance(self.antialias, bool):
            raise TypeError("antialias must be a boolean")


class CnnFrameTransform:
    """Resize, tensorize, and normalize a face crop.

    A caller-owned ``torch.Generator`` supplies randomness.  Keeping random
    state outside torchvision's global RNG makes two datasets constructed
    with the same seed reproducible, including in DataLoader workers.
    """

    def __init__(
        self,
        *,
        training: bool,
        config: CnnTransformConfig | None = None,
    ) -> None:
        if not isinstance(training, bool):
            raise TypeError("training must be a boolean")
        self.training = training
        self.config = config or CnnTransformConfig()
        self.config.validate()

    def __call__(
        self,
        image: Image.Image,
        *,
        generator: torch.Generator | None = None,
    ) -> torch.Tensor:
        if not isinstance(image, Image.Image):
            raise TypeError("image must be a PIL image")

        probability = float(self.config.horizontal_flip_probability)
        if self.training and probability > 0.0:
            if generator is None:
                raise ValueError("training transform requires a torch.Generator")
            should_flip = probability >= 1.0 or bool(
                torch.rand((), generator=generator).item() < probability
            )
            if should_flip:
                image = vision_functional.hflip(image)

        image = vision_functional.resize(
            image,
            [self.config.image_size, self.config.image_size],
            interpolation=InterpolationMode.BILINEAR,
            antialias=self.config.antialias,
        )
        tensor = vision_functional.to_tensor(image)
        tensor = vision_functional.normalize(
            tensor,
            mean=list(self.config.mean),
            std=list(self.config.std),
        )
        return tensor.contiguous()


@dataclass(frozen=True, slots=True)
class CnnFrameRecord:
    """Validated manifest fields needed by the CNN training pipeline."""

    manifest_row: int
    frame_id: str
    video_id: str
    sample_index: int
    frame_index: int
    split: str
    label: int
    face_path: Path
    relative_face_path: str


@dataclass(frozen=True, slots=True)
class CnnDatasetCoverage:
    """Auditable coverage for the selected split."""

    manifest_path: str
    manifest_sha256: str
    preprocess_fingerprint: str
    split: str
    manifest_rows: int
    split_rows: int
    included_rows: int
    excluded_no_face_rows: int
    unique_videos: int
    live_frames: int
    spoof_frames: int
    detection_rate: float

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""

        return asdict(self)


def _parse_int(value: object, *, field: str, row_number: int) -> int:
    text = "" if value is None else str(value).strip()
    digits = text[1:] if text[:1] in {"+", "-"} else text
    if not text or not digits.isdigit():
        raise CnnDatasetError(
            f"manifest row {row_number}: {field} must be an integer, got {value!r}"
        )
    return int(text)


def _parse_bool(value: object, *, field: str, row_number: int) -> bool:
    normalized = "" if value is None else str(value).strip().lower()
    if normalized in {"true", "1"}:
        return True
    if normalized in {"false", "0"}:
        return False
    raise CnnDatasetError(
        f"manifest row {row_number}: {field} must be true or false, got {value!r}"
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_within_project(
    raw_path: os.PathLike[str] | str,
    *,
    project_root: Path,
    field: str,
) -> Path:
    path = Path(raw_path).expanduser()
    resolved = path.resolve(strict=False) if path.is_absolute() else (
        project_root / path
    ).resolve(strict=False)
    try:
        resolved.relative_to(project_root)
    except ValueError as exc:
        raise CnnDatasetError(f"{field} escapes project_root: {raw_path}") from exc
    return resolved


def _worker_seed(base_seed: int, epoch: int, worker_id: int) -> int:
    """Mix stable dataset state into a valid torch generator seed."""

    payload = f"{base_seed}:{epoch}:{worker_id}".encode("ascii")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") & (
        (1 << 63) - 1
    )


class CnnFrameDataset(Dataset[CnnFrameItem]):
    """Frame-level CNN dataset backed by ``frames_protocol1.csv``.

    Parameters
    ----------
    manifest_path:
        Absolute path inside ``project_root`` or a path relative to it.
    split:
        Exactly one of ``train``, ``dev``, or ``test``.
    project_root:
        Root against which the manifest and every ``face_path`` are resolved.
        It defaults to the current working directory.
    training:
        Enables horizontal flips.  It is deliberately allowed only for the
        train split, protecting dev/test evaluation from augmentation.
    seed:
        Base transform seed.  Each DataLoader worker receives a deterministic,
        independent generator derived from this value.
    transform_config:
        Explicit resize, normalization, and flip settings.

    Call :meth:`set_epoch` before constructing each epoch's DataLoader iterator
    when a different but repeatable flip sequence is desired.  With worker
    processes, use the default ``persistent_workers=False`` so the updated
    epoch reaches newly spawned workers.
    """

    def __init__(
        self,
        manifest_path: os.PathLike[str] | str,
        split: str,
        *,
        project_root: os.PathLike[str] | str | None = None,
        training: bool = False,
        seed: int = 42,
        transform_config: CnnTransformConfig | None = None,
    ) -> None:
        if not isinstance(split, str) or split not in VALID_SPLITS:
            raise ValueError("split must be one of: train, dev, test")
        if not isinstance(training, bool):
            raise TypeError("training must be a boolean")
        if training and split != "train":
            raise ValueError("training augmentation is allowed only for split='train'")
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise TypeError("seed must be an integer")
        if seed < 0 or seed >= (1 << 63):
            raise ValueError("seed must be between 0 and 2**63 - 1")

        root = Path.cwd() if project_root is None else Path(project_root).expanduser()
        self.project_root = root.resolve(strict=False)
        if not self.project_root.is_dir():
            raise CnnDatasetError(f"project_root is not a directory: {root}")
        self.manifest_path = _resolve_within_project(
            manifest_path,
            project_root=self.project_root,
            field="manifest_path",
        )
        if not self.manifest_path.is_file():
            raise CnnDatasetError(
                f"frame manifest does not exist: {self.manifest_path}"
            )

        self.split = split
        self.training = training
        self.seed = seed
        self.transform = CnnFrameTransform(
            training=training,
            config=transform_config,
        )
        self._epoch = 0
        self._generators: dict[int, torch.Generator] = {}

        records, coverage = self._load_records()
        self.records = tuple(records)
        self.coverage = coverage

    def _load_records(self) -> tuple[list[CnnFrameRecord], CnnDatasetCoverage]:
        seen_frame_ids: set[str] = set()
        detected_paths: set[Path] = set()
        video_contract: dict[str, tuple[str, int]] = {}
        video_sample_indices: dict[str, set[int]] = {}
        preprocess_fingerprints: set[str] = set()
        selected_records: list[CnnFrameRecord] = []
        selected_video_ids: set[str] = set()
        label_counts: Counter[int] = Counter()
        manifest_rows = 0
        split_rows = 0
        excluded_no_face_rows = 0

        try:
            with self.manifest_path.open(
                "r", encoding="utf-8-sig", newline=""
            ) as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames is None:
                    raise CnnDatasetError("frame manifest has no CSV header")
                duplicates = sorted(
                    field
                    for field, count in Counter(reader.fieldnames).items()
                    if count > 1
                )
                if duplicates:
                    raise CnnDatasetError(
                        "frame manifest contains duplicate columns: "
                        + ", ".join(duplicates)
                    )
                missing = sorted(_REQUIRED_FIELDS - set(reader.fieldnames))
                if missing:
                    raise CnnDatasetError(
                        "frame manifest is missing required columns: "
                        + ", ".join(missing)
                    )

                for row_number, row in enumerate(reader, start=2):
                    manifest_rows += 1
                    if None in row or any(value is None for value in row.values()):
                        raise CnnDatasetError(
                            f"manifest row {row_number}: malformed CSV column count"
                        )

                    frame_id = str(row["frame_id"]).strip()
                    video_id = str(row["video_id"]).strip()
                    row_split = str(row["split"]).strip()
                    fingerprint = str(row["preprocess_fingerprint"]).strip()
                    if not frame_id:
                        raise CnnDatasetError(
                            f"manifest row {row_number}: frame_id is empty"
                        )
                    if not video_id:
                        raise CnnDatasetError(
                            f"manifest row {row_number}: video_id is empty"
                        )
                    if frame_id in seen_frame_ids:
                        raise CnnDatasetError(f"duplicate frame_id: {frame_id}")
                    seen_frame_ids.add(frame_id)
                    if row_split not in VALID_SPLITS:
                        raise CnnDatasetError(
                            f"manifest row {row_number}: invalid split {row_split!r}"
                        )
                    if not fingerprint:
                        raise CnnDatasetError(
                            f"manifest row {row_number}: "
                            "preprocess_fingerprint is empty"
                        )
                    preprocess_fingerprints.add(fingerprint)

                    label = _parse_int(
                        row["label"], field="label", row_number=row_number
                    )
                    if label not in {0, 1}:
                        raise CnnDatasetError(
                            f"manifest row {row_number}: label must be 0 or 1"
                        )
                    sample_index = _parse_int(
                        row["sample_index"],
                        field="sample_index",
                        row_number=row_number,
                    )
                    frame_index = _parse_int(
                        row["frame_index"],
                        field="frame_index",
                        row_number=row_number,
                    )
                    if sample_index < 0 or frame_index < 0:
                        raise CnnDatasetError(
                            f"manifest row {row_number}: frame indices must be "
                            "non-negative"
                        )

                    previous_contract = video_contract.setdefault(
                        video_id, (row_split, label)
                    )
                    if previous_contract != (row_split, label):
                        raise CnnDatasetError(
                            f"video {video_id!r} has inconsistent split or label"
                        )
                    samples = video_sample_indices.setdefault(video_id, set())
                    if sample_index in samples:
                        raise CnnDatasetError(
                            f"video {video_id!r} has duplicate sample_index "
                            f"{sample_index}"
                        )
                    samples.add(sample_index)

                    face_detected = _parse_bool(
                        row["face_detected"],
                        field="face_detected",
                        row_number=row_number,
                    )
                    raw_face_path = str(row["face_path"]).strip()
                    if row_split != self.split:
                        # Parse the global manifest contract above, but do not
                        # touch crop paths from another split. In particular,
                        # train/dev dataset construction must not stat or open
                        # test images before model selection is frozen.
                        continue

                    split_rows += 1
                    resolved_face_path: Path | None = None
                    if face_detected:
                        if not raw_face_path:
                            raise CnnDatasetError(
                                f"manifest row {row_number}: detected face has empty "
                                "face_path"
                            )
                        if Path(raw_face_path).is_absolute():
                            raise CnnDatasetError(
                                f"manifest row {row_number}: face_path must be "
                                "relative "
                                "to project_root"
                            )
                        resolved_face_path = _resolve_within_project(
                            raw_face_path,
                            project_root=self.project_root,
                            field=f"manifest row {row_number} face_path",
                        )
                        if resolved_face_path in detected_paths:
                            raise CnnDatasetError(
                                f"duplicate detected face_path: {raw_face_path}"
                            )
                        detected_paths.add(resolved_face_path)
                        if not resolved_face_path.is_file():
                            raise CnnDatasetError(
                                f"manifest row {row_number}: face crop does not exist: "
                                f"{resolved_face_path}"
                            )
                    elif raw_face_path:
                        raise CnnDatasetError(
                            f"manifest row {row_number}: undetected face must have "
                            "empty face_path"
                        )

                    if not face_detected:
                        excluded_no_face_rows += 1
                        continue

                    assert resolved_face_path is not None
                    selected_records.append(
                        CnnFrameRecord(
                            manifest_row=row_number,
                            frame_id=frame_id,
                            video_id=video_id,
                            sample_index=sample_index,
                            frame_index=frame_index,
                            split=row_split,
                            label=label,
                            face_path=resolved_face_path,
                            relative_face_path=raw_face_path,
                        )
                    )
                    selected_video_ids.add(video_id)
                    label_counts[label] += 1
        except CnnDatasetError:
            raise
        except (OSError, csv.Error, UnicodeError) as exc:
            raise CnnDatasetError(
                f"cannot read frame manifest {self.manifest_path}: {exc}"
            ) from exc

        if manifest_rows == 0:
            raise CnnDatasetError("frame manifest contains no data rows")
        if len(preprocess_fingerprints) != 1:
            raise CnnDatasetError(
                "frame manifest must contain exactly one preprocess_fingerprint"
            )
        if split_rows == 0:
            raise CnnDatasetError(
                f"frame manifest contains no rows for split {self.split!r}"
            )
        if not selected_records:
            raise CnnDatasetError(
                f"split {self.split!r} contains no successfully detected face crops"
            )

        coverage = CnnDatasetCoverage(
            manifest_path=self.manifest_path.relative_to(self.project_root).as_posix(),
            manifest_sha256=_sha256_file(self.manifest_path),
            preprocess_fingerprint=next(iter(preprocess_fingerprints)),
            split=self.split,
            manifest_rows=manifest_rows,
            split_rows=split_rows,
            included_rows=len(selected_records),
            excluded_no_face_rows=excluded_no_face_rows,
            unique_videos=len(selected_video_ids),
            live_frames=label_counts[0],
            spoof_frames=label_counts[1],
            detection_rate=len(selected_records) / split_rows,
        )
        return selected_records, coverage

    @property
    def coverage_metadata(self) -> dict[str, Any]:
        """JSON-serializable coverage and manifest provenance."""

        return self.coverage.to_dict()

    def set_epoch(self, epoch: int) -> None:
        """Select a deterministic transform stream for a training epoch."""

        if isinstance(epoch, bool) or not isinstance(epoch, int):
            raise TypeError("epoch must be an integer")
        if epoch < 0:
            raise ValueError("epoch must be non-negative")
        self._epoch = epoch
        self._generators.clear()

    def _generator(self) -> torch.Generator:
        worker = get_worker_info()
        worker_id = -1 if worker is None else worker.id
        generator = self._generators.get(worker_id)
        if generator is None:
            generator = torch.Generator()
            generator.manual_seed(_worker_seed(self.seed, self._epoch, worker_id))
            self._generators[worker_id] = generator
        return generator

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> CnnFrameItem:
        record = self.records[index]
        try:
            with Image.open(record.face_path) as source:
                image = source.convert("RGB")
        except (OSError, UnidentifiedImageError) as exc:
            raise CnnDatasetError(
                f"cannot decode face crop for frame {record.frame_id!r}: "
                f"{record.face_path}"
            ) from exc

        generator = self._generator() if self.training else None
        tensor = self.transform(image, generator=generator)
        expected_shape = (
            3,
            self.transform.config.image_size,
            self.transform.config.image_size,
        )
        if tensor.dtype != torch.float32 or tuple(tensor.shape) != expected_shape:
            raise CnnDatasetError(
                f"transform contract violation for frame {record.frame_id!r}: "
                f"dtype={tensor.dtype}, shape={tuple(tensor.shape)}"
            )
        return {
            "image": tensor,
            "label": torch.tensor(record.label, dtype=torch.long),
            "frame_id": record.frame_id,
            "video_id": record.video_id,
        }


def make_dataloader_generator(seed: int) -> torch.Generator:
    """Return a seeded generator for reproducible DataLoader shuffling."""

    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    if seed < 0 or seed >= (1 << 63):
        raise ValueError("seed must be between 0 and 2**63 - 1")
    generator = torch.Generator()
    generator.manual_seed(seed)
    return generator


__all__ = [
    "CNN_IMAGE_SIZE",
    "CNN_TRANSFORM_VERSION",
    "IMAGENET_MEAN",
    "IMAGENET_STD",
    "CnnDatasetCoverage",
    "CnnDatasetError",
    "CnnFrameDataset",
    "CnnFrameItem",
    "CnnFrameRecord",
    "CnnFrameTransform",
    "CnnTransformConfig",
    "make_dataloader_generator",
]
