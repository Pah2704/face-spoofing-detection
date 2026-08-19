"""Content-addressed cache for spatial-LBP features.

The cache is deliberately independent from pandas and scikit-learn.  Building
requires OpenCV, imported lazily inside worker threads, while loading an
already-built cache only requires NumPy.  A cache directory is immutable and
is addressed by the SHA-256 digest of its extraction configuration, the exact
frame-manifest bytes, and the manifest's preprocessing fingerprint.
"""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import csv
import hashlib
import json
from numbers import Integral
import os
from pathlib import Path
import shutil
import tempfile
import time
from typing import Any, Mapping, Sequence
import uuid

import numpy as np
from numpy.typing import NDArray

from .lbp import extract_lbp, extract_rgb_lbp


LBP_CACHE_VERSION = 1
_INDEX_FIELDS = (
    "feature_index",
    "manifest_row",
    "frame_id",
    "video_id",
    "sample_index",
    "frame_index",
    "split",
    "label",
    "face_path",
    "preprocess_fingerprint",
)
_REQUIRED_MANIFEST_FIELDS = frozenset(
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
_ARTIFACT_NAMES = ("index.csv", "features.npz", "excluded.csv")


class LbpCacheError(RuntimeError):
    """Raised when an LBP cache or its source manifest violates the contract."""


@dataclass(frozen=True, slots=True)
class LbpCacheConfig:
    """Versioned LBP feature-extraction configuration.

    The defaults resize each face crop to 128x128 grayscale with OpenCV
    ``INTER_AREA`` and concatenate an 8x8 grid of ten-bin uniform-LBP
    histograms.  The resulting descriptor has 640 float32 values.  Setting
    ``color_mode='rgb'`` applies the same descriptor independently in R, G,
    and B order for a 1920-value E05 descriptor.
    """

    version: int = LBP_CACHE_VERSION
    color_mode: str = "grayscale"
    image_size: int = 128
    resize_interpolation: str = "INTER_AREA"
    radius: int = 1
    points: int = 8
    grid_rows: int = 8
    grid_cols: int = 8

    def validate(self) -> None:
        integer_fields = (
            "version",
            "image_size",
            "radius",
            "points",
            "grid_rows",
            "grid_cols",
        )
        for name in integer_fields:
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Integral):
                raise TypeError(f"{name} must be an integer, got {value!r}")
        if self.version != LBP_CACHE_VERSION:
            raise ValueError(
                f"unsupported LBP cache version {self.version}; "
                f"expected {LBP_CACHE_VERSION}"
            )
        if self.color_mode not in {"grayscale", "rgb"}:
            raise ValueError("color_mode must be 'grayscale' or 'rgb'")
        if self.image_size <= 0:
            raise ValueError("image_size must be positive")
        if self.resize_interpolation != "INTER_AREA":
            raise ValueError("resize_interpolation must be 'INTER_AREA'")
        if self.radius != 1 or self.points != 8:
            raise ValueError("only radius=1 and points=8 are supported")
        if self.grid_rows <= 0 or self.grid_cols <= 0:
            raise ValueError("grid_rows and grid_cols must be positive")
        if self.grid_rows > self.image_size or self.grid_cols > self.image_size:
            raise ValueError("grid dimensions must not exceed image_size")

    @property
    def feature_dim(self) -> int:
        """Number of float32 values in one descriptor."""

        channels = 1 if self.color_mode == "grayscale" else 3
        return channels * self.grid_rows * self.grid_cols * 10

    def canonical_dict(self) -> dict[str, object]:
        """Return the JSON-serialisable configuration used for addressing."""

        self.validate()
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LbpDataset:
    """Validated in-memory view of an LBP feature cache."""

    features: NDArray[np.float32]
    frame_ids: NDArray[np.str_]
    video_ids: NDArray[np.str_]
    sample_indices: NDArray[np.int64]
    frame_indices: NDArray[np.int64]
    splits: NDArray[np.str_]
    labels: NDArray[np.int64]
    face_paths: NDArray[np.str_]
    excluded_rows: tuple[dict[str, str], ...]
    metadata: dict[str, Any]
    cache_dir: Path

    def select_split(self, split: str) -> NDArray[np.int64]:
        """Return feature-row indices belonging to ``split`` in cache order."""

        if not isinstance(split, str) or not split:
            raise ValueError("split must be a non-empty string")
        return np.flatnonzero(self.splits == split).astype(np.int64, copy=False)


def _canonical_json(payload: object) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _cache_fingerprint(
    config: LbpCacheConfig,
    manifest_sha256: str,
    preprocess_fingerprint: str,
) -> str:
    payload = {
        "config": config.canonical_dict(),
        "manifest_sha256": manifest_sha256,
        "preprocess_fingerprint": preprocess_fingerprint,
    }
    return _sha256_bytes(_canonical_json(payload))


def _require_cv2():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is required to build the LBP cache. Activate the Python "
            "3.10 ML environment with the preprocess dependencies."
        ) from exc
    return cv2


def _extract_one(path: Path, config: LbpCacheConfig) -> NDArray[np.float32]:
    """Read, resize, and describe one crop (kept separate for test isolation)."""

    cv2 = _require_cv2()
    cv2.setNumThreads(1)
    read_mode = (
        cv2.IMREAD_GRAYSCALE
        if config.color_mode == "grayscale"
        else cv2.IMREAD_COLOR
    )
    image = cv2.imread(str(path), read_mode)
    if image is None:
        raise LbpCacheError(f"OpenCV could not read face crop: {path}")
    resized = cv2.resize(
        image,
        (config.image_size, config.image_size),
        interpolation=cv2.INTER_AREA,
    )
    if config.color_mode == "grayscale":
        feature = extract_lbp(
            resized,
            radius=config.radius,
            points=config.points,
            grid_rows=config.grid_rows,
            grid_cols=config.grid_cols,
        )
    else:
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        feature = extract_rgb_lbp(
            rgb,
            radius=config.radius,
            points=config.points,
            grid_rows=config.grid_rows,
            grid_cols=config.grid_cols,
        )
    return np.asarray(feature, dtype=np.float32)


def _parse_bool(value: object, *, field: str, row_number: int) -> bool:
    normalised = str(value).strip().lower()
    if normalised in {"true", "1", "yes"}:
        return True
    if normalised in {"false", "0", "no"}:
        return False
    raise LbpCacheError(
        f"manifest row {row_number}: {field} must be true or false, got {value!r}"
    )


def _parse_int(value: object, *, field: str, row_number: int) -> int:
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise LbpCacheError(
            f"manifest row {row_number}: {field} must be an integer"
        ) from exc
    return parsed


def _read_manifest(
    manifest_path: Path,
) -> tuple[list[dict[str, str]], tuple[str, ...]]:
    try:
        with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise LbpCacheError("frame manifest has no CSV header")
            if len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise LbpCacheError("frame manifest contains duplicate columns")
            missing = sorted(_REQUIRED_MANIFEST_FIELDS - set(reader.fieldnames))
            if missing:
                raise LbpCacheError(
                    "frame manifest is missing required columns: " + ", ".join(missing)
                )
            fields = tuple(reader.fieldnames)
            rows: list[dict[str, str]] = []
            for row_number, source_row in enumerate(reader, start=2):
                row = dict(source_row)
                if None in row or any(row.get(field) is None for field in fields):
                    raise LbpCacheError(
                        f"frame manifest row {row_number} does not match its CSV header"
                    )
                rows.append(row)  # type: ignore[arg-type]
    except (OSError, UnicodeError, csv.Error) as exc:
        if isinstance(exc, LbpCacheError):
            raise
        raise LbpCacheError(
            f"could not read frame manifest {manifest_path}: {exc}"
        ) from exc

    if not rows:
        raise LbpCacheError("frame manifest must contain at least one row")
    frame_ids = [row["frame_id"].strip() for row in rows]
    if any(not frame_id for frame_id in frame_ids):
        raise LbpCacheError("every manifest row must have a non-empty frame_id")
    if len(frame_ids) != len(set(frame_ids)):
        raise LbpCacheError("frame manifest contains duplicate frame_id values")
    fingerprints = {
        row["preprocess_fingerprint"].strip()
        for row in rows
        if row["preprocess_fingerprint"].strip()
    }
    if len(fingerprints) != 1 or any(
        not row["preprocess_fingerprint"].strip() for row in rows
    ):
        raise LbpCacheError(
            "frame manifest must contain exactly one non-empty "
            "preprocess_fingerprint"
        )
    return rows, fields


def _discover_project_root(
    manifest_path: Path,
    rows: Sequence[Mapping[str, str]],
) -> Path:
    relative_paths = [
        Path(row["face_path"])
        for row in rows
        if row["face_path"].strip() and not Path(row["face_path"]).is_absolute()
    ]
    candidates: list[Path] = [Path.cwd().resolve()]
    candidates.extend(parent.resolve() for parent in manifest_path.resolve().parents)
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if relative_paths and (candidate / relative_paths[0]).is_file():
            return candidate
    return Path.cwd().resolve()


def _portable_path(path: Path, project_root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def _normalise_rows(
    rows: Sequence[dict[str, str]],
    project_root: Path,
) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    valid: list[dict[str, object]] = []
    excluded: list[dict[str, str]] = []
    for offset, source_row in enumerate(rows, start=2):
        row = dict(source_row)
        detected = _parse_bool(
            row["face_detected"], field="face_detected", row_number=offset
        )
        # Validate the fields consumed by downstream training even for no-face
        # rows, so excluded.csv remains trustworthy provenance.
        sample_index = _parse_int(
            row["sample_index"], field="sample_index", row_number=offset
        )
        frame_index = _parse_int(
            row["frame_index"], field="frame_index", row_number=offset
        )
        label = _parse_int(row["label"], field="label", row_number=offset)
        if label not in {0, 1}:
            raise LbpCacheError(
                f"manifest row {offset}: label must be 0 or 1, got {label}"
            )
        if not row["video_id"].strip() or not row["split"].strip():
            raise LbpCacheError(
                f"manifest row {offset}: video_id and split must be non-empty"
            )
        if not detected:
            row["exclusion_reason"] = "no_face"
            excluded.append(row)
            continue
        raw_path = row["face_path"].strip()
        if not raw_path:
            raise LbpCacheError(
                f"manifest row {offset}: detected face has an empty face_path"
            )
        path = Path(raw_path)
        if not path.is_absolute():
            path = project_root / path
        path = path.resolve()
        if not path.is_file():
            raise LbpCacheError(
                f"manifest row {offset}: face crop does not exist: {path}"
            )
        portable_face_path = _portable_path(path, project_root)
        if Path(portable_face_path).is_absolute():
            raise LbpCacheError(
                f"manifest row {offset}: face crop is outside project_root: {path}"
            )
        valid.append(
            {
                "manifest_row": offset,
                "frame_id": row["frame_id"].strip(),
                "video_id": row["video_id"].strip(),
                "sample_index": sample_index,
                "frame_index": frame_index,
                "split": row["split"].strip(),
                "label": label,
                "face_path": portable_face_path,
                "resolved_face_path": path,
                "preprocess_fingerprint": row["preprocess_fingerprint"].strip(),
            }
        )
    if not valid:
        raise LbpCacheError("frame manifest contains no detected face crops")
    return valid, excluded


def _write_csv(
    path: Path,
    fieldnames: Sequence[str],
    rows: Sequence[Mapping[str, object]],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    path.chmod(0o644)


def _artifact_metadata(path: Path, *, rows: int) -> dict[str, object]:
    return {
        "path": path.name,
        "sha256": _sha256_file(path),
        "size_bytes": path.stat().st_size,
        "rows": rows,
    }


def _extract_matrix(
    rows: Sequence[Mapping[str, object]],
    config: LbpCacheConfig,
    workers: int | None,
) -> NDArray[np.float32]:
    if workers is not None and (
        isinstance(workers, bool) or not isinstance(workers, Integral) or workers <= 0
    ):
        raise ValueError("workers must be a positive integer or None")
    max_workers = (
        int(workers)
        if workers is not None
        else min(32, (os.cpu_count() or 1) + 4)
    )
    matrix = np.empty((len(rows), config.feature_dim), dtype=np.float32)
    tasks = ((row["resolved_face_path"], config) for row in rows)

    def run(task: tuple[object, LbpCacheConfig]) -> NDArray[np.float32]:
        path, task_config = task
        return _extract_one(Path(path), task_config)

    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="lbp") as pool:
        for index, feature in enumerate(pool.map(run, tasks)):
            array = np.asarray(feature)
            if array.dtype != np.float32 or array.shape != (config.feature_dim,):
                raise LbpCacheError(
                    f"feature {index} has dtype/shape {array.dtype}/{array.shape}; "
                    f"expected float32/({config.feature_dim},)"
                )
            if not np.isfinite(array).all():
                raise LbpCacheError(f"feature {index} contains NaN or infinity")
            matrix[index] = array
    return matrix


def _read_csv(path: Path) -> tuple[list[dict[str, str]], tuple[str, ...]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise LbpCacheError(f"{path.name} has no CSV header")
            fields = tuple(reader.fieldnames)
            rows: list[dict[str, str]] = []
            for row_number, source_row in enumerate(reader, start=2):
                row = dict(source_row)
                if None in row or any(row.get(field) is None for field in fields):
                    raise LbpCacheError(
                        f"{path.name} row {row_number} does not match its CSV header"
                    )
                rows.append(row)  # type: ignore[arg-type]
            return rows, fields
    except (OSError, UnicodeError, csv.Error) as exc:
        if isinstance(exc, LbpCacheError):
            raise
        raise LbpCacheError(f"could not read {path}: {exc}") from exc


def _metadata_int(metadata: Mapping[str, Any], name: str) -> int:
    value = metadata.get(name)
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise LbpCacheError(f"metadata field {name!r} must be an integer")
    return int(value)


def load_lbp_cache(
    cache_dir: Path | str,
    *,
    expected_fingerprint: str | None = None,
) -> LbpDataset:
    """Load and fully validate a published LBP cache.

    Validation covers the completion marker, address derivation, checksums,
    artifact byte sizes, CSV schema/order, matrix dtype/shape, row counts, and
    provenance agreement.  Source face images are not needed after the cache
    has been built.
    """

    directory = Path(cache_dir).resolve()
    metadata_path = directory / "metadata.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LbpCacheError(
            f"could not read cache metadata {metadata_path}: {exc}"
        ) from exc
    if not isinstance(metadata, dict):
        raise LbpCacheError("cache metadata must be a JSON object")
    if metadata.get("complete") is not True:
        raise LbpCacheError("cache metadata is not marked complete")
    if _metadata_int(metadata, "cache_version") != LBP_CACHE_VERSION:
        raise LbpCacheError("unsupported cache metadata version")

    config_payload = metadata.get("config")
    if not isinstance(config_payload, dict):
        raise LbpCacheError("cache metadata config must be an object")
    try:
        config = LbpCacheConfig(**config_payload)
        config.validate()
    except (TypeError, ValueError) as exc:
        raise LbpCacheError(f"invalid cached LBP configuration: {exc}") from exc
    manifest_sha256 = str(metadata.get("manifest_sha256", ""))
    preprocess_fingerprint = str(metadata.get("preprocess_fingerprint", ""))
    if len(manifest_sha256) != 64 or not preprocess_fingerprint:
        raise LbpCacheError("cache metadata has invalid source fingerprints")
    fingerprint = _cache_fingerprint(
        config, manifest_sha256, preprocess_fingerprint
    )
    if metadata.get("fingerprint") != fingerprint:
        raise LbpCacheError("cache fingerprint does not match its provenance")
    if expected_fingerprint is not None and fingerprint != expected_fingerprint:
        raise LbpCacheError(
            f"cache fingerprint {fingerprint} does not match expected "
            f"{expected_fingerprint}"
        )

    artifacts = metadata.get("artifacts")
    if not isinstance(artifacts, dict):
        raise LbpCacheError("cache metadata artifacts must be an object")
    for artifact_name in _ARTIFACT_NAMES:
        details = artifacts.get(artifact_name)
        if not isinstance(details, dict) or details.get("path") != artifact_name:
            raise LbpCacheError(f"missing or invalid metadata for {artifact_name}")
        artifact_path = directory / artifact_name
        if not artifact_path.is_file():
            raise LbpCacheError(f"cache artifact is missing: {artifact_name}")
        if details.get("sha256") != _sha256_file(artifact_path):
            raise LbpCacheError(f"checksum mismatch for {artifact_name}")
        if details.get("size_bytes") != artifact_path.stat().st_size:
            raise LbpCacheError(f"byte-size mismatch for {artifact_name}")

    index_rows, index_fields = _read_csv(directory / "index.csv")
    if index_fields != _INDEX_FIELDS:
        raise LbpCacheError(
            f"index.csv schema is {index_fields!r}; expected {_INDEX_FIELDS!r}"
        )
    excluded_rows, excluded_fields = _read_csv(directory / "excluded.csv")
    required_excluded_fields = _REQUIRED_MANIFEST_FIELDS | {"exclusion_reason"}
    if not required_excluded_fields.issubset(excluded_fields):
        raise LbpCacheError("excluded.csv is missing provenance columns")
    valid_count = _metadata_int(metadata, "valid_rows")
    excluded_count = _metadata_int(metadata, "excluded_rows")
    feature_dim = _metadata_int(metadata, "feature_dim")
    manifest_rows = _metadata_int(metadata, "manifest_rows")
    if valid_count != len(index_rows):
        raise LbpCacheError("index.csv row count does not match metadata")
    if excluded_count != len(excluded_rows):
        raise LbpCacheError("excluded.csv row count does not match metadata")
    if manifest_rows != valid_count + excluded_count:
        raise LbpCacheError("valid and excluded counts do not cover the manifest")
    if feature_dim != config.feature_dim:
        raise LbpCacheError("feature dimension does not match cached config")
    if metadata.get("feature_dtype") != "float32":
        raise LbpCacheError("feature dtype metadata must be 'float32'")
    for name, actual_rows in (
        ("index.csv", len(index_rows)),
        ("features.npz", len(index_rows)),
        ("excluded.csv", len(excluded_rows)),
    ):
        details = artifacts[name]
        if details.get("rows") != actual_rows:
            raise LbpCacheError(f"artifact row count mismatch for {name}")

    try:
        with np.load(directory / "features.npz", allow_pickle=False) as archive:
            if archive.files != ["X"]:
                raise LbpCacheError("features.npz must contain exactly the array 'X'")
            features = np.asarray(archive["X"])
            if features.dtype != np.float32:
                raise LbpCacheError(
                    f"feature matrix dtype is {features.dtype}; expected float32"
                )
            if features.shape != (valid_count, feature_dim):
                raise LbpCacheError(
                    f"feature matrix shape is {features.shape}; expected "
                    f"({valid_count}, {feature_dim})"
                )
            if not np.isfinite(features).all():
                raise LbpCacheError("feature matrix contains NaN or infinity")
            features = features.copy()
    except (OSError, ValueError, KeyError) as exc:
        if isinstance(exc, LbpCacheError):
            raise
        raise LbpCacheError(f"could not load features.npz: {exc}") from exc

    expected_indices = [str(index) for index in range(valid_count)]
    if [row["feature_index"] for row in index_rows] != expected_indices:
        raise LbpCacheError("index.csv feature_index is not contiguous and ordered")
    frame_ids = [row["frame_id"] for row in index_rows]
    if len(frame_ids) != len(set(frame_ids)):
        raise LbpCacheError("index.csv contains duplicate frame_id values")
    if any(
        row["preprocess_fingerprint"] != preprocess_fingerprint
        for row in index_rows
    ):
        raise LbpCacheError("index.csv preprocessing provenance is inconsistent")
    if any(not row["video_id"] or not row["split"] for row in index_rows):
        raise LbpCacheError("index.csv video_id and split must be non-empty")
    if any(
        not row["face_path"]
        or Path(row["face_path"]).is_absolute()
        or ".." in Path(row["face_path"]).parts
        for row in index_rows
    ):
        raise LbpCacheError("index.csv face_path values must be project-relative")
    excluded_frame_ids = [row["frame_id"] for row in excluded_rows]
    if any(not frame_id for frame_id in excluded_frame_ids):
        raise LbpCacheError("excluded.csv frame_id values must be non-empty")
    if len(set(frame_ids + excluded_frame_ids)) != manifest_rows:
        raise LbpCacheError("cache rows do not contain unique manifest frame_ids")
    if any(row["exclusion_reason"] != "no_face" for row in excluded_rows):
        raise LbpCacheError("excluded.csv contains an unsupported exclusion reason")
    if any(
        row["face_detected"].strip().lower() not in {"false", "0", "no"}
        for row in excluded_rows
    ):
        raise LbpCacheError("excluded.csv contains a detected face row")
    if any(
        row["preprocess_fingerprint"] != preprocess_fingerprint
        for row in excluded_rows
    ):
        raise LbpCacheError("excluded.csv preprocessing provenance is inconsistent")

    def ints(field: str) -> NDArray[np.int64]:
        try:
            return np.asarray([int(row[field]) for row in index_rows], dtype=np.int64)
        except (TypeError, ValueError) as exc:
            raise LbpCacheError(f"index.csv column {field} is not integral") from exc

    sample_indices = ints("sample_index")
    frame_indices = ints("frame_index")
    labels = ints("label")
    if not np.isin(labels, np.asarray([0, 1], dtype=np.int64)).all():
        raise LbpCacheError("index.csv labels must be 0 or 1")

    return LbpDataset(
        features=features,
        frame_ids=np.asarray(frame_ids, dtype=np.str_),
        video_ids=np.asarray([row["video_id"] for row in index_rows], dtype=np.str_),
        sample_indices=sample_indices,
        frame_indices=frame_indices,
        splits=np.asarray([row["split"] for row in index_rows], dtype=np.str_),
        labels=labels,
        face_paths=np.asarray([row["face_path"] for row in index_rows], dtype=np.str_),
        excluded_rows=tuple(excluded_rows),
        metadata=metadata,
        cache_dir=directory,
    )


def _publish_cache(temporary: Path, destination: Path) -> None:
    """Atomically publish a completed directory, replacing only invalid data."""

    if not destination.exists():
        try:
            os.rename(temporary, destination)
            return
        except FileExistsError:
            # Another builder won the race; the caller validates it below.
            return

    backup = destination.with_name(
        f".{destination.name}.{uuid.uuid4().hex}.invalid"
    )
    os.rename(destination, backup)
    try:
        os.rename(temporary, destination)
    except Exception:
        os.rename(backup, destination)
        raise
    else:
        shutil.rmtree(backup, ignore_errors=True)


def build_lbp_cache(
    manifest_path: Path | str,
    cache_root: Path | str,
    config: LbpCacheConfig | None = None,
    *,
    workers: int | None = None,
    project_root: Path | str | None = None,
    force: bool = False,
) -> LbpDataset:
    """Build or reuse the content-addressed LBP cache for a frame manifest.

    Undetected-face rows are recorded in ``excluded.csv`` and never receive a
    feature row.  Detected crops retain manifest order in both ``index.csv``
    and the ``X`` array in ``features.npz``.
    """

    if not isinstance(force, bool):
        raise TypeError("force must be a boolean")
    if workers is not None and (
        isinstance(workers, bool)
        or not isinstance(workers, Integral)
        or workers <= 0
    ):
        raise ValueError("workers must be a positive integer or None")
    extraction_config = config or LbpCacheConfig()
    extraction_config.validate()
    source_manifest = Path(manifest_path).resolve()
    if not source_manifest.is_file():
        raise FileNotFoundError(f"frame manifest does not exist: {source_manifest}")
    rows, manifest_fields = _read_manifest(source_manifest)
    root = (
        Path(project_root).resolve()
        if project_root is not None
        else _discover_project_root(source_manifest, rows)
    )
    manifest_sha256 = _sha256_file(source_manifest)
    preprocess_fingerprint = rows[0]["preprocess_fingerprint"].strip()
    fingerprint = _cache_fingerprint(
        extraction_config, manifest_sha256, preprocess_fingerprint
    )
    output_root = Path(cache_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    destination = output_root / fingerprint

    if destination.is_dir() and not force:
        try:
            return load_lbp_cache(
                destination, expected_fingerprint=fingerprint
            )
        except LbpCacheError:
            # A partial or corrupted directory is never accepted as a hit.
            pass

    # Source crops are intentionally inspected only on a cache miss.  A valid
    # feature cache remains loadable after raw/intermediate images are moved.
    valid_rows, excluded_rows = _normalise_rows(rows, root)

    temporary = Path(
        tempfile.mkdtemp(
            prefix=f".{fingerprint}.", suffix=".tmp", dir=output_root
        )
    )
    try:
        extraction_started = time.perf_counter()
        features = _extract_matrix(valid_rows, extraction_config, workers)
        extraction_seconds = time.perf_counter() - extraction_started
        index_rows: list[dict[str, object]] = []
        for feature_index, row in enumerate(valid_rows):
            index_rows.append(
                {
                    "feature_index": feature_index,
                    "manifest_row": row["manifest_row"],
                    "frame_id": row["frame_id"],
                    "video_id": row["video_id"],
                    "sample_index": row["sample_index"],
                    "frame_index": row["frame_index"],
                    "split": row["split"],
                    "label": row["label"],
                    "face_path": row["face_path"],
                    "preprocess_fingerprint": row["preprocess_fingerprint"],
                }
            )
        _write_csv(temporary / "index.csv", _INDEX_FIELDS, index_rows)
        excluded_fields = tuple(manifest_fields) + ("exclusion_reason",)
        _write_csv(
            temporary / "excluded.csv", excluded_fields, excluded_rows
        )
        np.savez_compressed(temporary / "features.npz", X=features)
        (temporary / "features.npz").chmod(0o644)

        artifacts = {
            "index.csv": _artifact_metadata(
                temporary / "index.csv", rows=len(index_rows)
            ),
            "features.npz": _artifact_metadata(
                temporary / "features.npz", rows=len(index_rows)
            ),
            "excluded.csv": _artifact_metadata(
                temporary / "excluded.csv", rows=len(excluded_rows)
            ),
        }
        metadata: dict[str, object] = {
            "complete": True,
            "cache_version": LBP_CACHE_VERSION,
            "fingerprint": fingerprint,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": extraction_config.canonical_dict(),
            "feature_dim": extraction_config.feature_dim,
            "feature_dtype": "float32",
            "manifest_path": _portable_path(source_manifest, root),
            "manifest_sha256": manifest_sha256,
            "manifest_rows": len(rows),
            "preprocess_fingerprint": preprocess_fingerprint,
            "valid_rows": len(index_rows),
            "excluded_rows": len(excluded_rows),
            "valid_rows_by_split": dict(
                sorted(
                    Counter(str(row["split"]) for row in valid_rows).items()
                )
            ),
            "extraction_seconds": extraction_seconds,
            "artifacts": artifacts,
        }
        metadata_path = temporary / "metadata.json"
        metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        metadata_path.chmod(0o644)

        # Validate exactly what will be published, including artifact checksums.
        load_lbp_cache(temporary, expected_fingerprint=fingerprint)

        if destination.is_dir() and not force:
            try:
                dataset = load_lbp_cache(
                    destination, expected_fingerprint=fingerprint
                )
            except LbpCacheError:
                _publish_cache(temporary, destination)
            else:
                shutil.rmtree(temporary, ignore_errors=True)
                return dataset
        else:
            _publish_cache(temporary, destination)
        # A concurrent valid publisher can make _publish_cache leave our temp
        # directory intact; either way the addressed destination is authoritative.
        return load_lbp_cache(destination, expected_fingerprint=fingerprint)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)


# Common initialism spellings kept as aliases for ergonomic imports.
LBPCacheConfig = LbpCacheConfig
LBPDataset = LbpDataset


__all__ = [
    "LBP_CACHE_VERSION",
    "LBPCacheConfig",
    "LBPDataset",
    "LbpCacheConfig",
    "LbpCacheError",
    "LbpDataset",
    "build_lbp_cache",
    "load_lbp_cache",
]
