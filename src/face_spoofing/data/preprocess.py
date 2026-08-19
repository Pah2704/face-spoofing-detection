"""Deterministic frame sampling and MediaPipe face-crop cache."""

from __future__ import annotations

from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
import csv
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import random
import tempfile
from typing import Callable, Iterable

from .frame_sampler import uniform_frame_indices
from .manifest import write_json_atomic
from .oulu import VideoRecord


PREPROCESS_PIPELINE_VERSION = 1


FRAME_MANIFEST_FIELDS = (
    "frame_id",
    "video_id",
    "sample_index",
    "frame_index",
    "timestamp_ms",
    "split",
    "label",
    "label_name",
    "source_video_path",
    "source_frame_count",
    "source_fps",
    "source_width",
    "source_height",
    "face_path",
    "face_detected",
    "detector_status",
    "detector",
    "detector_score",
    "crop_bbox_x1",
    "crop_bbox_y1",
    "crop_bbox_x2",
    "crop_bbox_y2",
    "crop_size",
    "preprocess_version",
    "preprocess_fingerprint",
)


@dataclass(frozen=True, slots=True)
class PreprocessConfig:
    frames_per_video: int = 10
    output_size: int = 256
    margin: float = 0.2
    model_selection: int = 0
    min_detection_confidence: float = 0.5
    detection_max_side: int = 640
    png_compression: int = 3

    def validate(self) -> None:
        if self.frames_per_video < 2:
            raise ValueError("frames_per_video must be at least 2.")
        if self.output_size <= 0:
            raise ValueError("output_size must be positive.")
        if not 0.0 <= self.margin <= 1.0:
            raise ValueError("margin must be between 0 and 1.")
        if self.model_selection not in {0, 1}:
            raise ValueError("MediaPipe model_selection must be 0 or 1.")
        if not 0.0 < self.min_detection_confidence <= 1.0:
            raise ValueError(
                "min_detection_confidence must be in the interval (0, 1]."
            )
        if self.detection_max_side < 128:
            raise ValueError("detection_max_side must be at least 128.")
        if not 0 <= self.png_compression <= 9:
            raise ValueError("png_compression must be between 0 and 9.")

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()[:16]


@dataclass(frozen=True, slots=True)
class VideoPreprocessResult:
    video_id: str
    rows: tuple[dict[str, object], ...]
    errors: tuple[str, ...]
    cache_hit: bool


@dataclass(frozen=True, slots=True)
class PreprocessProgress:
    completed_videos: int
    total_videos: int
    detected_faces: int
    requested_faces: int
    current_video_id: str


_WORKER_DETECTOR = None
_WORKER_CONFIG: PreprocessConfig | None = None


def _require_cv2():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is required for preprocessing. Activate the Python 3.10 "
            "ML environment before running this command."
        ) from exc
    return cv2


def _initialize_worker(config: PreprocessConfig) -> None:
    global _WORKER_CONFIG, _WORKER_DETECTOR
    config.validate()
    cv2 = _require_cv2()
    cv2.setNumThreads(1)
    try:
        import mediapipe as mp
    except ImportError as exc:
        raise RuntimeError(
            "MediaPipe is required for face detection. Activate the Python "
            "3.10 ML environment before running preprocessing."
        ) from exc

    _WORKER_CONFIG = config
    _WORKER_DETECTOR = mp.solutions.face_detection.FaceDetection(
        model_selection=config.model_selection,
        min_detection_confidence=config.min_detection_confidence,
    )


def _atomic_json(path: Path, payload: object) -> None:
    write_json_atomic(path, payload)


def _write_png_atomic(path: Path, image, compression: int) -> None:
    cv2 = _require_cv2()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.stem + ".part" + path.suffix)
    temporary.unlink(missing_ok=True)
    ok = cv2.imwrite(
        str(temporary),
        image,
        [cv2.IMWRITE_PNG_COMPRESSION, compression],
    )
    if not ok:
        temporary.unlink(missing_ok=True)
        raise OSError(f"OpenCV failed to write {temporary}.")
    os.replace(temporary, path)


def _load_cached_result(
    metadata_path: Path,
    *,
    video_id: str,
    config: PreprocessConfig,
) -> VideoPreprocessResult | None:
    if not metadata_path.is_file():
        return None
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        if payload.get("preprocess_fingerprint") != config.fingerprint:
            return None
        payload_version = int(
            payload.get("preprocess_version", PREPROCESS_PIPELINE_VERSION)
        )
        if payload_version != PREPROCESS_PIPELINE_VERSION:
            return None
        rows = payload["rows"]
        if len(rows) != config.frames_per_video:
            return None
        for row in rows:
            for axis in ("x1", "y1", "x2", "y2"):
                new_key = f"crop_bbox_{axis}"
                legacy_key = f"bbox_{axis}"
                if new_key not in row and legacy_key in row:
                    row[new_key] = row[legacy_key]
            row.setdefault(
                "preprocess_version", PREPROCESS_PIPELINE_VERSION
            )
            if row.get("face_detected") and not Path(str(row["face_path"])).is_file():
                return None
        return VideoPreprocessResult(
            video_id=video_id,
            rows=tuple(rows),
            errors=tuple(payload.get("errors", [])),
            cache_hit=True,
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def _best_detection(frame, config: PreprocessConfig):
    cv2 = _require_cv2()
    if _WORKER_DETECTOR is None:
        raise RuntimeError("MediaPipe worker was not initialized.")

    height, width = frame.shape[:2]
    max_side = max(height, width)
    scale = min(1.0, config.detection_max_side / max_side)
    candidates = []
    if scale < 1.0:
        resized = cv2.resize(
            frame,
            (max(1, round(width * scale)), max(1, round(height * scale))),
            interpolation=cv2.INTER_AREA,
        )
        candidates.append(("ok_scaled", resized))
    candidates.append(("ok_full_retry" if scale < 1.0 else "ok_full", frame))

    for status, detection_frame in candidates:
        rgb = cv2.cvtColor(detection_frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = _WORKER_DETECTOR.process(rgb)
        detections = list(result.detections or [])
        if not detections:
            continue
        detection = max(
            detections,
            key=lambda item: float(item.score[0]) if item.score else 0.0,
        )
        relative = detection.location_data.relative_bounding_box
        x = float(relative.xmin) * width
        y = float(relative.ymin) * height
        box_width = float(relative.width) * width
        box_height = float(relative.height) * height
        if box_width <= 1 or box_height <= 1:
            continue
        score = float(detection.score[0]) if detection.score else 0.0
        return status, score, (x, y, box_width, box_height)
    return "no_face", 0.0, None


def _expanded_square_box(
    raw_box: tuple[float, float, float, float],
    image_width: int,
    image_height: int,
    margin: float,
) -> tuple[int, int, int, int]:
    x, y, width, height = raw_box
    center_x = x + width / 2.0
    center_y = y + height / 2.0
    side = max(width, height) * (1.0 + 2.0 * margin)
    side = min(side, float(image_width), float(image_height))
    side_int = max(2, int(round(side)))

    x1 = int(round(center_x - side_int / 2.0))
    y1 = int(round(center_y - side_int / 2.0))
    x1 = max(0, min(x1, image_width - side_int))
    y1 = max(0, min(y1, image_height - side_int))
    x2 = x1 + side_int
    y2 = y1 + side_int
    return x1, y1, x2, y2


def _frame_row_base(
    record: VideoRecord,
    *,
    sample_index: int,
    frame_index: int,
    source_video_path: Path,
    frame_count: int,
    fps: float,
    config: PreprocessConfig,
) -> dict[str, object]:
    timestamp_ms = 1000.0 * frame_index / fps if fps > 0 else ""
    return {
        "frame_id": f"{record.video_id}__{sample_index:02d}",
        "video_id": record.video_id,
        "sample_index": sample_index,
        "frame_index": frame_index,
        "timestamp_ms": round(timestamp_ms, 3) if timestamp_ms != "" else "",
        "split": record.split,
        "label": record.label,
        "label_name": record.label_name,
        "source_video_path": source_video_path.as_posix(),
        "source_frame_count": frame_count,
        "source_fps": round(fps, 6) if fps > 0 else "",
        "source_width": "",
        "source_height": "",
        "face_path": "",
        "face_detected": False,
        "detector_status": "pending",
        "detector": "mediapipe",
        "detector_score": "",
        "crop_bbox_x1": "",
        "crop_bbox_y1": "",
        "crop_bbox_x2": "",
        "crop_bbox_y2": "",
        "crop_size": config.output_size,
        "preprocess_version": PREPROCESS_PIPELINE_VERSION,
        "preprocess_fingerprint": config.fingerprint,
    }


def _process_video(
    record: VideoRecord,
    raw_root: str,
    output_root: str,
    force: bool,
) -> VideoPreprocessResult:
    if _WORKER_CONFIG is None:
        raise RuntimeError("Preprocessing worker configuration is missing.")
    config = _WORKER_CONFIG
    cv2 = _require_cv2()
    raw_path = Path(raw_root)
    output_path = Path(output_root)
    video_output = output_path / "protocol_1" / record.video_id
    metadata_path = video_output / "metadata.json"

    if not force:
        cached = _load_cached_result(
            metadata_path, video_id=record.video_id, config=config
        )
        if cached is not None:
            return cached

    video_path = record.video_path(raw_path)
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        return VideoPreprocessResult(
            video_id=record.video_id,
            rows=(),
            errors=(f"Cannot open video: {video_path}.",),
            cache_hit=False,
        )

    rows: list[dict[str, object]] = []
    errors: list[str] = []
    try:
        frame_count = int(round(capture.get(cv2.CAP_PROP_FRAME_COUNT)))
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        indices = uniform_frame_indices(
            frame_count, frames_per_video=config.frames_per_video
        )

        for sample_index, frame_index in enumerate(indices):
            row = _frame_row_base(
                record,
                sample_index=sample_index,
                frame_index=frame_index,
                source_video_path=video_path,
                frame_count=frame_count,
                fps=fps,
                config=config,
            )
            capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, frame = capture.read()
            if not ok or frame is None:
                row["detector_status"] = "read_error"
                errors.append(
                    f"{record.video_id}: cannot read frame {frame_index}."
                )
                rows.append(row)
                continue

            height, width = frame.shape[:2]
            row["source_width"] = width
            row["source_height"] = height
            status, score, raw_box = _best_detection(frame, config)
            row["detector_status"] = status
            row["detector_score"] = round(score, 8)
            if raw_box is None:
                errors.append(
                    f"{record.video_id}: no face at frame {frame_index}."
                )
                rows.append(row)
                continue

            x1, y1, x2, y2 = _expanded_square_box(
                raw_box,
                image_width=width,
                image_height=height,
                margin=config.margin,
            )
            crop = frame[y1:y2, x1:x2]
            if crop.size == 0:
                row["detector_status"] = "invalid_crop"
                errors.append(
                    f"{record.video_id}: empty crop at frame {frame_index}."
                )
                rows.append(row)
                continue

            interpolation = (
                cv2.INTER_AREA
                if max(crop.shape[:2]) > config.output_size
                else cv2.INTER_LINEAR
            )
            resized = cv2.resize(
                crop,
                (config.output_size, config.output_size),
                interpolation=interpolation,
            )
            face_path = (
                video_output
                / f"sample_{sample_index:02d}_frame_{frame_index:06d}.png"
            )
            _write_png_atomic(face_path, resized, config.png_compression)
            row.update(
                {
                    "face_path": face_path.as_posix(),
                    "face_detected": True,
                    "crop_bbox_x1": x1,
                    "crop_bbox_y1": y1,
                    "crop_bbox_x2": x2,
                    "crop_bbox_y2": y2,
                }
            )
            rows.append(row)
    except (OSError, RuntimeError, ValueError) as exc:
        errors.append(f"{record.video_id}: {exc}")
    finally:
        capture.release()

    payload = {
        "video_id": record.video_id,
        "preprocess_version": PREPROCESS_PIPELINE_VERSION,
        "preprocess_fingerprint": config.fingerprint,
        "config": asdict(config),
        "rows": rows,
        "errors": errors,
    }
    _atomic_json(metadata_path, payload)
    return VideoPreprocessResult(
        video_id=record.video_id,
        rows=tuple(rows),
        errors=tuple(errors),
        cache_hit=False,
    )


def select_balanced_subset(
    records: Iterable[VideoRecord], limit_per_group: int
) -> list[VideoRecord]:
    """Select deterministic smoke-test rows from every split/label group."""

    materialized = list(records)
    if limit_per_group <= 0:
        return materialized
    groups: dict[tuple[str, int], list[VideoRecord]] = defaultdict(list)
    for record in materialized:
        groups[(record.split, record.label)].append(record)
    selected_ids: set[str] = set()
    for key in sorted(groups):
        for record in sorted(groups[key], key=lambda item: item.video_id)[
            :limit_per_group
        ]:
            selected_ids.add(record.video_id)
    return [record for record in materialized if record.video_id in selected_ids]


def write_frame_manifest(
    rows: Iterable[dict[str, object]], output_path: Path | str
) -> None:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        prefix=destination.name + ".",
        suffix=".tmp",
        dir=destination.parent,
        delete=False,
    )
    temporary = Path(handle.name)
    try:
        with handle:
            writer = csv.DictWriter(handle, fieldnames=FRAME_MANIFEST_FIELDS)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in FRAME_MANIFEST_FIELDS})
        os.replace(temporary, destination)
        destination.chmod(0o644)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _build_summary(
    records: list[VideoRecord],
    rows: list[dict[str, object]],
    errors: list[str],
    cache_hits: int,
    config: PreprocessConfig,
    output_root: Path,
    frame_manifest: Path,
) -> dict[str, object]:
    detected = sum(bool(row["face_detected"]) for row in rows)
    requested = len(records) * config.frames_per_video
    statuses = Counter(str(row["detector_status"]) for row in rows)
    group_stats: dict[str, dict[str, int | float]] = {}
    rows_by_group: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        rows_by_group[(str(row["split"]), str(row["label_name"]))].append(row)
    for (split, label_name), group_rows in sorted(rows_by_group.items()):
        group_detected = sum(bool(row["face_detected"]) for row in group_rows)
        group_stats[f"{split}/{label_name}"] = {
            "requested": len(group_rows),
            "detected": group_detected,
            "failed": len(group_rows) - group_detected,
            "detection_rate": group_detected / len(group_rows),
        }

    detection_rate = detected / requested if requested else 0.0
    rows_by_video_id: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        rows_by_video_id[str(row["video_id"])].append(row)
    videos_with_zero_detected_faces = sum(
        not any(
            bool(row["face_detected"])
            for row in rows_by_video_id.get(record.video_id, [])
        )
        for record in records
    )
    fatal_status_names = {"read_error", "invalid_crop", "pending"}
    fatal_status_count = sum(
        count for status, count in statuses.items() if status in fatal_status_names
    )
    complete_manifest = len(rows) == requested
    meets_detection_target = detection_rate >= 0.98
    nonfatal_warnings = [
        error for error in errors if ": no face at frame " in error
    ]
    fatal_errors = [
        error for error in errors if error not in nonfatal_warnings
    ]
    return {
        "ok": (
            complete_manifest
            and meets_detection_target
            and fatal_status_count == 0
            and videos_with_zero_detected_faces == 0
        ),
        "meets_detection_target": meets_detection_target,
        "complete_manifest": complete_manifest,
        "protocol": 1,
        "preprocess_version": PREPROCESS_PIPELINE_VERSION,
        "config": asdict(config),
        "preprocess_fingerprint": config.fingerprint,
        "videos": len(records),
        "cache_hits": cache_hits,
        "frames_requested": requested,
        "manifest_rows": len(rows),
        "faces_detected": detected,
        "faces_failed": requested - detected,
        "detection_rate": detection_rate,
        "videos_with_zero_detected_faces": videos_with_zero_detected_faces,
        "fatal_status_count": fatal_status_count,
        "status_counts": dict(sorted(statuses.items())),
        "by_split_label": group_stats,
        "warnings": nonfatal_warnings,
        "video_errors": fatal_errors,
        "output_root": output_root.as_posix(),
        "frame_manifest": frame_manifest.as_posix(),
    }


def run_preprocessing(
    records: Iterable[VideoRecord],
    raw_root: Path | str,
    output_root: Path | str,
    frame_manifest: Path | str,
    summary_path: Path | str,
    *,
    config: PreprocessConfig,
    workers: int = 1,
    force: bool = False,
    limit_per_group: int = 0,
    progress: Callable[[PreprocessProgress], None] | None = None,
) -> dict[str, object]:
    """Process selected videos, write frame manifest and return summary."""

    config.validate()
    if workers < 1:
        raise ValueError("workers must be at least 1.")
    selected = select_balanced_subset(records, limit_per_group)
    root = Path(raw_root)
    output = Path(output_root)
    manifest_path = Path(frame_manifest)
    results: dict[str, VideoPreprocessResult] = {}
    completed = 0
    detected_so_far = 0

    def accept_result(result: VideoPreprocessResult) -> None:
        nonlocal completed, detected_so_far
        results[result.video_id] = result
        completed += 1
        detected_so_far += sum(
            bool(row["face_detected"]) for row in result.rows
        )
        if progress is not None:
            progress(
                PreprocessProgress(
                    completed_videos=completed,
                    total_videos=len(selected),
                    detected_faces=detected_so_far,
                    requested_faces=completed * config.frames_per_video,
                    current_video_id=result.video_id,
                )
            )

    if workers == 1:
        _initialize_worker(config)
        for record in selected:
            accept_result(
                _process_video(
                    record,
                    raw_root=root.as_posix(),
                    output_root=output.as_posix(),
                    force=force,
                )
            )
    else:
        context = multiprocessing.get_context("spawn")
        with ProcessPoolExecutor(
            max_workers=workers,
            mp_context=context,
            initializer=_initialize_worker,
            initargs=(config,),
        ) as executor:
            futures = {
                executor.submit(
                    _process_video,
                    record,
                    root.as_posix(),
                    output.as_posix(),
                    force,
                ): record
                for record in selected
            }
            for future in as_completed(futures):
                record = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    result = VideoPreprocessResult(
                        video_id=record.video_id,
                        rows=(),
                        errors=(f"{record.video_id}: worker failure: {exc}",),
                        cache_hit=False,
                    )
                accept_result(result)

    ordered_rows: list[dict[str, object]] = []
    all_errors: list[str] = []
    cache_hits = 0
    for record in selected:
        result = results[record.video_id]
        ordered_rows.extend(
            sorted(result.rows, key=lambda row: int(row["sample_index"]))
        )
        all_errors.extend(result.errors)
        cache_hits += int(result.cache_hit)

    write_frame_manifest(ordered_rows, manifest_path)
    summary = _build_summary(
        selected,
        ordered_rows,
        all_errors,
        cache_hits,
        config,
        output,
        manifest_path,
    )
    write_json_atomic(summary_path, summary)
    return summary


def create_qc_montage(
    frame_manifest: Path | str,
    output_path: Path | str,
    *,
    per_group: int = 20,
    seed: int = 42,
    thumbnail_size: int = 160,
    columns: int = 10,
) -> dict[str, object]:
    """Create a deterministic montage balanced across split and label."""

    if per_group <= 0 or thumbnail_size <= 0 or columns <= 0:
        raise ValueError("QC montage dimensions and sample count must be positive.")
    cv2 = _require_cv2()
    with Path(frame_manifest).open("r", encoding="utf-8", newline="") as handle:
        rows = [
            row
            for row in csv.DictReader(handle)
            if row.get("face_detected", "").lower() == "true"
        ]
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[(row["split"], row["label_name"])].append(row)

    selected: list[dict[str, str]] = []
    rng = random.Random(seed)
    for key in sorted(groups):
        candidates = sorted(groups[key], key=lambda row: row["frame_id"])
        selected.extend(
            rng.sample(candidates, min(per_group, len(candidates)))
        )
    if not selected:
        raise ValueError("No detected face rows are available for QC montage.")

    header_height = 24
    tile_height = thumbnail_size + header_height
    rows_count = (len(selected) + columns - 1) // columns
    import numpy as np

    canvas = np.full(
        (rows_count * tile_height, columns * thumbnail_size, 3),
        245,
        dtype=np.uint8,
    )
    for index, row in enumerate(selected):
        image = cv2.imread(row["face_path"], cv2.IMREAD_COLOR)
        if image is None:
            raise OSError(f"Cannot read QC face image: {row['face_path']}.")
        image = cv2.resize(
            image,
            (thumbnail_size, thumbnail_size),
            interpolation=cv2.INTER_AREA,
        )
        grid_row, grid_column = divmod(index, columns)
        x1 = grid_column * thumbnail_size
        y1 = grid_row * tile_height
        color = (30, 150, 30) if row["label_name"] == "live" else (30, 30, 180)
        cv2.rectangle(
            canvas,
            (x1, y1),
            (x1 + thumbnail_size, y1 + header_height),
            color,
            thickness=-1,
        )
        label = f"{row['split']} {row['label_name']} {row['video_id']}"
        cv2.putText(
            canvas,
            label,
            (x1 + 3, y1 + 16),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.34,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
        canvas[
            y1 + header_height : y1 + tile_height,
            x1 : x1 + thumbnail_size,
        ] = image

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.stem + ".part" + destination.suffix)
    ok = cv2.imwrite(str(temporary), canvas, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not ok:
        temporary.unlink(missing_ok=True)
        raise OSError(f"Cannot write QC montage: {destination}.")
    os.replace(temporary, destination)
    return {
        "output": destination.as_posix(),
        "samples": len(selected),
        "groups": {
            f"{split}/{label}": sum(
                row["split"] == split and row["label_name"] == label
                for row in selected
            )
            for split, label in sorted(groups)
        },
    }
