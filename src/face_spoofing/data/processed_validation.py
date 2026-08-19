"""Validation for the shared, processed OULU-NPU face crops.

The validator deliberately has no import-time OpenCV dependency.  Structural
checks can therefore run in lightweight environments by passing
``check_images=False``; OpenCV is imported only when a crop actually needs to
be decoded.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import math
import os
from pathlib import Path
from typing import Callable, Iterable, Mapping

from .frame_sampler import uniform_frame_indices
from .oulu import VideoRecord
from .preprocess import FRAME_MANIFEST_FIELDS


MAX_REPORTED_ERRORS = 200


def _text(value: object) -> str:
    return "" if value is None else str(value).strip()


def _parse_int(value: object) -> int | None:
    """Parse an integer without silently accepting floats or booleans."""

    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    normalized = _text(value)
    if not normalized:
        return None
    digits = normalized[1:] if normalized[:1] in {"+", "-"} else normalized
    if not digits.isdigit():
        return None
    try:
        return int(normalized)
    except ValueError:
        return None


def _parse_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return bool(value) if value in {0, 1} else None
    normalized = _text(value).lower()
    if normalized in {"true", "1"}:
        return True
    if normalized in {"false", "0"}:
        return False
    return None


def _parse_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        parsed = float(value)
    else:
        normalized = _text(value)
        if not normalized:
            return None
        try:
            parsed = float(normalized)
        except ValueError:
            return None
    return parsed if math.isfinite(parsed) else None


def _read_manifest(
    frame_manifest: os.PathLike[str] | str | Iterable[Mapping[str, object]],
    add_error: Callable[[str], None],
) -> list[dict[str, object]]:
    """Materialize either the generated CSV or in-memory manifest rows."""

    if isinstance(frame_manifest, (str, os.PathLike)):
        path = Path(frame_manifest)
        if not path.is_file():
            add_error(f"Frame manifest does not exist: {path}.")
            return []
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                fieldnames = reader.fieldnames
                if fieldnames is None:
                    add_error(f"Frame manifest has no CSV header: {path}.")
                    return []
                duplicate_fields = sorted(
                    field
                    for field, count in Counter(fieldnames).items()
                    if count > 1
                )
                if duplicate_fields:
                    add_error(
                        "Frame manifest has duplicate columns: "
                        + ", ".join(duplicate_fields)
                        + "."
                    )
                missing_fields = [
                    field for field in FRAME_MANIFEST_FIELDS if field not in fieldnames
                ]
                if missing_fields:
                    add_error(
                        "Frame manifest is missing required columns: "
                        + ", ".join(missing_fields)
                        + "."
                    )
                return [dict(row) for row in reader]
        except (OSError, csv.Error, UnicodeError) as exc:
            add_error(f"Cannot read frame manifest {path}: {exc}.")
            return []

    if isinstance(frame_manifest, Mapping):
        add_error("frame_manifest must be a CSV path or an iterable of rows.")
        return []

    rows: list[dict[str, object]] = []
    try:
        for row_number, row in enumerate(frame_manifest, start=1):
            if not isinstance(row, Mapping):
                add_error(
                    f"Manifest row {row_number} is not a mapping: "
                    f"{type(row).__name__}."
                )
                continue
            materialized = dict(row)
            missing_fields = [
                field for field in FRAME_MANIFEST_FIELDS if field not in materialized
            ]
            if missing_fields:
                add_error(
                    f"Manifest row {row_number} is missing required fields: "
                    + ", ".join(missing_fields)
                    + "."
                )
            rows.append(materialized)
    except TypeError as exc:
        add_error(f"Cannot iterate frame_manifest: {exc}.")
    return rows


def _resolve_face_path(raw_value: object, output_root: Path) -> Path | None:
    value = _text(raw_value)
    if not value:
        return None
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.resolve(strict=False)

    # The preprocessing command currently writes paths relative to the working
    # directory.  Also accept paths relative to output_root so exported
    # manifests remain portable.
    from_working_directory = path.resolve(strict=False)
    protocol_root = (output_root / "protocol_1").resolve(strict=False)
    try:
        from_working_directory.relative_to(protocol_root)
    except ValueError:
        from_output_root = (output_root / path).resolve(strict=False)
        try:
            from_output_root.relative_to(protocol_root)
        except ValueError:
            return from_working_directory
        return from_output_root
    return from_working_directory


def _png_files(root: Path) -> set[Path]:
    if not root.is_dir():
        return set()
    return {
        path.resolve(strict=False)
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() == ".png"
    }


def validate_processed_faces(
    records: Iterable[VideoRecord],
    frame_manifest: os.PathLike[str] | str | Iterable[Mapping[str, object]],
    output_root: os.PathLike[str] | str,
    frames_per_video: int = 10,
    output_size: int = 256,
    check_images: bool = True,
    minimum_detection_rate: float = 0.98,
) -> dict[str, object]:
    """Validate the frame manifest and every referenced shared face crop.

    This validation is intentionally compatible with small protocol subsets,
    which makes it useful for preprocessing smoke tests as well as a complete
    2,700-video Protocol 1 run.
    """

    if isinstance(frames_per_video, bool) or not isinstance(frames_per_video, int):
        raise TypeError("frames_per_video must be an integer.")
    if frames_per_video < 2:
        raise ValueError("frames_per_video must be at least 2.")
    if isinstance(output_size, bool) or not isinstance(output_size, int):
        raise TypeError("output_size must be an integer.")
    if output_size <= 0:
        raise ValueError("output_size must be positive.")
    if not isinstance(check_images, bool):
        raise TypeError("check_images must be a boolean.")
    if isinstance(minimum_detection_rate, bool) or not isinstance(
        minimum_detection_rate, (int, float)
    ):
        raise TypeError("minimum_detection_rate must be a number.")
    minimum_detection_rate = float(minimum_detection_rate)
    if not math.isfinite(minimum_detection_rate) or not (
        0.0 <= minimum_detection_rate <= 1.0
    ):
        raise ValueError("minimum_detection_rate must be between 0 and 1.")

    errors: list[str] = []
    total_error_count = 0

    def add_error(message: str) -> None:
        nonlocal total_error_count
        total_error_count += 1
        if len(errors) < MAX_REPORTED_ERRORS:
            errors.append(message)

    materialized_records = list(records)
    root = Path(output_root)
    protocol_root = (root / "protocol_1").resolve(strict=False)
    rows = _read_manifest(frame_manifest, add_error)

    records_by_id: dict[str, VideoRecord] = {}
    record_id_counts = Counter(record.video_id for record in materialized_records)
    for video_id, count in sorted(record_id_counts.items()):
        if count > 1:
            add_error(
                f"Duplicate video_id in records: {video_id!r} appears {count} times."
            )
    for record in materialized_records:
        records_by_id.setdefault(record.video_id, record)

    subject_splits: dict[int, set[str]] = defaultdict(set)
    for record in materialized_records:
        subject_splits[record.subject_id].add(record.split)
    leaking_subjects = {
        subject_id: sorted(splits)
        for subject_id, splits in subject_splits.items()
        if len(splits) > 1
    }
    for subject_id, splits in sorted(leaking_subjects.items()):
        add_error(
            f"Subject leakage: subject {subject_id} occurs in splits "
            f"{', '.join(splits)}."
        )

    rows_by_video: dict[str, list[tuple[int, dict[str, object]]]] = defaultdict(list)
    manifest_video_splits: dict[str, set[str]] = defaultdict(set)
    frame_id_rows: dict[str, list[int]] = defaultdict(list)
    face_path_rows: dict[Path, list[int]] = defaultdict(list)
    referenced_face_paths: set[Path] = set()
    detected_face_paths: set[Path] = set()
    detected_faces = 0
    undetected_faces = 0
    missing_face_files = 0
    invalid_png_files = 0
    wrong_size_images = 0
    invalid_crop_metadata = 0
    checked_image_count = 0
    cv2_module = None
    cv2_import_failed = False

    for row_number, row in enumerate(rows, start=1):
        video_id = _text(row.get("video_id"))
        if not video_id:
            add_error(f"Manifest row {row_number} has an empty video_id.")
        else:
            rows_by_video[video_id].append((row_number, row))

        record = records_by_id.get(video_id)
        if video_id and record is None:
            add_error(
                f"Manifest row {row_number} references unknown video_id "
                f"{video_id!r}."
            )

        split = _text(row.get("split"))
        if video_id and split:
            manifest_video_splits[video_id].add(split)
        if record is not None and split != record.split:
            add_error(
                f"Manifest row {row_number} split mismatch for {video_id}: "
                f"got {split!r}, expected {record.split!r}."
            )

        label = _parse_int(row.get("label"))
        if label is None:
            add_error(f"Manifest row {row_number} has an invalid label.")
        elif record is not None and label != record.label:
            add_error(
                f"Manifest row {row_number} label mismatch for {video_id}: "
                f"got {label}, expected {record.label}."
            )
        label_name = _text(row.get("label_name"))
        if record is not None and label_name != record.label_name:
            add_error(
                f"Manifest row {row_number} label_name mismatch for {video_id}: "
                f"got {label_name!r}, expected {record.label_name!r}."
            )

        frame_id = _text(row.get("frame_id"))
        if not frame_id:
            add_error(f"Manifest row {row_number} has an empty frame_id.")
        else:
            frame_id_rows[frame_id].append(row_number)

        face_detected = _parse_bool(row.get("face_detected"))
        if face_detected is None:
            add_error(
                f"Manifest row {row_number} has an invalid face_detected value "
                f"{row.get('face_detected')!r}."
            )
            face_detected = False

        face_path = _resolve_face_path(row.get("face_path"), root)
        if face_path is not None:
            referenced_face_paths.add(face_path)
            face_path_rows[face_path].append(row_number)
        if face_detected:
            detected_faces += 1
            crop_metadata_errors: list[str] = []
            source_width = _parse_int(row.get("source_width"))
            source_height = _parse_int(row.get("source_height"))
            if source_width is None or source_width <= 0:
                crop_metadata_errors.append(
                    "source_width must be a positive integer"
                )
            if source_height is None or source_height <= 0:
                crop_metadata_errors.append(
                    "source_height must be a positive integer"
                )

            bbox_values = {
                field: _parse_int(row.get(field))
                for field in (
                    "crop_bbox_x1",
                    "crop_bbox_y1",
                    "crop_bbox_x2",
                    "crop_bbox_y2",
                )
            }
            if any(value is None for value in bbox_values.values()):
                crop_metadata_errors.append(
                    "crop_bbox_x1, crop_bbox_y1, crop_bbox_x2 and "
                    "crop_bbox_y2 must be integers"
                )
            else:
                x1 = bbox_values["crop_bbox_x1"]
                y1 = bbox_values["crop_bbox_y1"]
                x2 = bbox_values["crop_bbox_x2"]
                y2 = bbox_values["crop_bbox_y2"]
                # The None case was excluded above; these assertions also
                # keep static type checkers aware of that invariant.
                assert x1 is not None and y1 is not None
                assert x2 is not None and y2 is not None
                if not (x2 > x1 and y2 > y1):
                    crop_metadata_errors.append(
                        "crop bbox must satisfy x2 > x1 and y2 > y1"
                    )
                if (
                    source_width is not None
                    and source_height is not None
                    and source_width > 0
                    and source_height > 0
                    and not (
                        0 <= x1 < x2 <= source_width
                        and 0 <= y1 < y2 <= source_height
                    )
                ):
                    crop_metadata_errors.append(
                        "crop bbox must be within the source image bounds"
                    )
                if x2 - x1 != y2 - y1:
                    crop_metadata_errors.append("crop bbox must be square")

            crop_size = _parse_int(row.get("crop_size"))
            if crop_size != output_size:
                crop_metadata_errors.append(
                    f"crop_size must equal output_size ({output_size})"
                )
            detector_score = _parse_float(row.get("detector_score"))
            if detector_score is None or not 0.0 <= detector_score <= 1.0:
                crop_metadata_errors.append(
                    "detector_score must be finite and between 0 and 1"
                )
            if crop_metadata_errors:
                invalid_crop_metadata += 1
                for metadata_error in crop_metadata_errors:
                    add_error(
                        f"Manifest row {row_number} has invalid crop metadata: "
                        f"{metadata_error}."
                    )

            if face_path is None:
                missing_face_files += 1
                add_error(
                    f"Manifest row {row_number} marks a detected face but "
                    "face_path is empty."
                )
                continue
            detected_face_paths.add(face_path)
            try:
                face_path.relative_to(protocol_root)
            except ValueError:
                add_error(
                    f"Manifest row {row_number} face_path is outside "
                    f"{protocol_root}: {face_path}."
                )
            if video_id:
                expected_video_root = (
                    protocol_root / video_id
                ).resolve(strict=False)
                try:
                    face_path.relative_to(expected_video_root)
                except ValueError:
                    add_error(
                        f"Manifest row {row_number} face_path is not inside "
                        f"the directory for video {video_id}: {face_path}."
                    )
            if face_path.suffix.lower() != ".png":
                invalid_png_files += 1
                add_error(
                    f"Manifest row {row_number} face_path is not a PNG: "
                    f"{face_path}."
                )
            if not face_path.is_file():
                missing_face_files += 1
                add_error(f"Detected face file does not exist: {face_path}.")
                continue
            if check_images:
                if cv2_module is None and not cv2_import_failed:
                    try:
                        import cv2 as imported_cv2

                        cv2_module = imported_cv2
                    except ImportError:
                        cv2_import_failed = True
                        add_error(
                            "OpenCV is required to decode processed PNG files; "
                            "install preprocessing dependencies or use "
                            "check_images=False."
                        )
                if cv2_module is not None:
                    image = cv2_module.imread(
                        str(face_path), cv2_module.IMREAD_UNCHANGED
                    )
                    checked_image_count += 1
                    if image is None:
                        invalid_png_files += 1
                        add_error(f"Cannot decode PNG face crop: {face_path}.")
                    elif tuple(image.shape[:2]) != (output_size, output_size):
                        wrong_size_images += 1
                        add_error(
                            f"Face crop has size {image.shape[1]}x{image.shape[0]}, "
                            f"expected {output_size}x{output_size}: {face_path}."
                        )
        else:
            undetected_faces += 1
            if face_path is not None:
                add_error(
                    f"Manifest row {row_number} has face_detected=false but a "
                    f"non-empty face_path: {face_path}."
                )

    duplicate_frame_ids = {
        frame_id: row_numbers
        for frame_id, row_numbers in frame_id_rows.items()
        if len(row_numbers) > 1
    }
    for frame_id, row_numbers in sorted(duplicate_frame_ids.items()):
        add_error(
            f"Duplicate frame_id {frame_id!r} in manifest rows "
            + ", ".join(str(number) for number in row_numbers)
            + "."
        )

    duplicate_face_paths = {
        path: row_numbers
        for path, row_numbers in face_path_rows.items()
        if len(row_numbers) > 1
    }
    for path, row_numbers in sorted(
        duplicate_face_paths.items(), key=lambda item: item[0].as_posix()
    ):
        add_error(
            f"Duplicate face_path {path} in manifest rows "
            + ", ".join(str(number) for number in row_numbers)
            + "."
        )

    for video_id, splits in sorted(manifest_video_splits.items()):
        if len(splits) > 1:
            add_error(
                f"Video leakage: {video_id} occurs in manifest splits "
                f"{', '.join(sorted(splits))}."
            )

    detected_faces_by_video = {
        video_id: sum(
            _parse_bool(row.get("face_detected")) is True
            for _, row in rows_by_video.get(video_id, [])
        )
        for video_id in records_by_id
    }
    zero_detection_video_ids = sorted(
        video_id
        for video_id, count in detected_faces_by_video.items()
        if count == 0
    )
    for video_id in zero_detection_video_ids:
        add_error(f"Video {video_id} has zero detected faces.")

    expected_manifest_rows = len(materialized_records) * frames_per_video
    detected_expected_faces = sum(detected_faces_by_video.values())
    detection_rate = (
        detected_expected_faces / expected_manifest_rows
        if expected_manifest_rows
        else 0.0
    )
    if detection_rate < minimum_detection_rate:
        add_error(
            f"Face detection rate is {detection_rate:.6f}, below the minimum "
            f"target {minimum_detection_rate:.6f}."
        )

    expected_sample_indices = list(range(frames_per_video))
    for video_id, record in sorted(records_by_id.items()):
        video_rows = rows_by_video.get(video_id, [])
        if len(video_rows) != frames_per_video:
            add_error(
                f"Video {video_id} has {len(video_rows)} manifest rows, "
                f"expected {frames_per_video}."
            )

        parsed_rows: list[tuple[int, int | None, int | None, int | None]] = []
        for row_number, row in video_rows:
            sample_index = _parse_int(row.get("sample_index"))
            frame_index = _parse_int(row.get("frame_index"))
            source_frame_count = _parse_int(row.get("source_frame_count"))
            if sample_index is None:
                add_error(
                    f"Manifest row {row_number} for {video_id} has an invalid "
                    "sample_index."
                )
            if frame_index is None:
                add_error(
                    f"Manifest row {row_number} for {video_id} has an invalid "
                    "frame_index."
                )
            if source_frame_count is None or source_frame_count <= 0:
                add_error(
                    f"Manifest row {row_number} for {video_id} has an invalid "
                    "source_frame_count."
                )
                source_frame_count = None
            parsed_rows.append(
                (row_number, sample_index, frame_index, source_frame_count)
            )

        actual_sample_indices = [
            sample_index
            for _, sample_index, _, _ in parsed_rows
            if sample_index is not None
        ]
        if sorted(actual_sample_indices) != expected_sample_indices:
            add_error(
                f"Video {video_id} sample_index values are "
                f"{sorted(actual_sample_indices)}, expected "
                f"{expected_sample_indices}."
            )

        frame_counts = {
            frame_count
            for _, _, _, frame_count in parsed_rows
            if frame_count is not None
        }
        if len(frame_counts) > 1:
            add_error(
                f"Video {video_id} has inconsistent source_frame_count values: "
                + ", ".join(str(value) for value in sorted(frame_counts))
                + "."
            )
        if len(frame_counts) != 1:
            continue
        source_frame_count = next(iter(frame_counts))
        try:
            expected_frame_indices = uniform_frame_indices(
                source_frame_count, frames_per_video=frames_per_video
            )
        except (TypeError, ValueError) as exc:
            add_error(f"Cannot sample video {video_id}: {exc}.")
            continue
        for row_number, sample_index, frame_index, _ in parsed_rows:
            if (
                sample_index is None
                or frame_index is None
                or sample_index not in range(frames_per_video)
            ):
                continue
            expected_frame_index = expected_frame_indices[sample_index]
            if frame_index != expected_frame_index:
                add_error(
                    f"Manifest row {row_number} frame_index mismatch for "
                    f"{video_id} sample {sample_index}: got {frame_index}, "
                    f"expected {expected_frame_index}."
                )

    disk_pngs = _png_files(protocol_root)
    orphan_pngs = sorted(
        disk_pngs - referenced_face_paths, key=lambda path: path.as_posix()
    )
    for path in orphan_pngs:
        add_error(f"Orphan PNG is not referenced by the manifest: {path}.")

    by_split: dict[str, dict[str, int]] = {}
    split_names = sorted({record.split for record in materialized_records})
    for split in split_names:
        split_records = [
            record for record in materialized_records if record.split == split
        ]
        split_video_ids = {record.video_id for record in split_records}
        split_rows = sum(
            len(rows_by_video.get(video_id, [])) for video_id in split_video_ids
        )
        split_detected = sum(
            1
            for video_id in split_video_ids
            for _, row in rows_by_video.get(video_id, [])
            if _parse_bool(row.get("face_detected")) is True
        )
        by_split[split] = {
            "videos": len(split_records),
            "manifest_rows": split_rows,
            "faces_detected": split_detected,
        }

    if total_error_count > len(errors):
        errors.append(
            f"Only the first {MAX_REPORTED_ERRORS} validation errors are listed."
        )

    stats: dict[str, object] = {
        "records": len(materialized_records),
        "videos": len(records_by_id),
        "videos_in_manifest": len(rows_by_video),
        "expected_manifest_rows": expected_manifest_rows,
        "manifest_rows": len(rows),
        "faces_detected": detected_faces,
        "faces_undetected": undetected_faces,
        "detection_rate": detection_rate,
        "minimum_detection_rate": minimum_detection_rate,
        "videos_with_zero_detected_faces": len(zero_detection_video_ids),
        "missing_face_files": missing_face_files,
        "checked_images": checked_image_count,
        "invalid_png_files": invalid_png_files,
        "wrong_size_images": wrong_size_images,
        "invalid_crop_metadata": invalid_crop_metadata,
        "png_files_on_disk": len(disk_pngs),
        "orphan_pngs": len(orphan_pngs),
        "duplicate_frame_ids": len(duplicate_frame_ids),
        "duplicate_face_paths": len(duplicate_face_paths),
        "leaking_subjects": len(leaking_subjects),
        "by_split": by_split,
    }
    return {
        "ok": total_error_count == 0,
        "errors": errors,
        "error_count": total_error_count,
        "stats": stats,
    }


__all__ = ["validate_processed_faces"]
