"""Protocol and extracted-video validation with machine-readable reports."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import subprocess
from typing import Iterable

from .oulu import SPLIT_ORDER, VideoRecord, validate_protocol_1


MAX_REPORTED_ERRORS = 200


def _append_error(errors: list[str], message: str) -> None:
    if len(errors) < MAX_REPORTED_ERRORS:
        errors.append(message)


def _read_eye_metadata(path: Path) -> dict[str, int]:
    rows = 0
    detector_failures = 0
    expected_frame = 0
    with path.open("r", encoding="utf-8-sig", newline=None) as handle:
        reader = csv.reader(handle)
        for row_number, row in enumerate(reader, start=1):
            if len(row) != 5:
                raise ValueError(
                    f"row {row_number} has {len(row)} columns, expected 5"
                )
            try:
                frame, left_x, left_y, right_x, right_y = (
                    int(value.strip()) for value in row
                )
            except ValueError as exc:
                raise ValueError(
                    f"row {row_number} contains a non-integer value"
                ) from exc
            if frame != expected_frame:
                raise ValueError(
                    f"row {row_number} frame is {frame}, expected {expected_frame}"
                )
            coordinates = (left_x, left_y, right_x, right_y)
            if any(value < 0 for value in coordinates):
                raise ValueError(
                    f"row {row_number} contains negative eye coordinates"
                )
            if coordinates == (0, 0, 0, 0):
                detector_failures += 1
            rows += 1
            expected_frame += 1
    if rows == 0:
        raise ValueError("file is empty")
    return {"rows": rows, "detector_failures": detector_failures}


def _is_avi(path: Path) -> bool:
    with path.open("rb") as handle:
        header = handle.read(12)
    return (
        len(header) == 12
        and header[:4] == b"RIFF"
        and header[8:12] == b"AVI "
    )


def _probe_video(path: Path) -> dict[str, object]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_name,width,height,r_frame_rate,nb_frames,duration",
        "-show_entries",
        "format=duration,size",
        "-of",
        "json",
        str(path),
    ]
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        raise ValueError(
            f"ffprobe failed with code {completed.returncode}: {stderr[:300]}"
        )
    payload = json.loads(completed.stdout)
    streams = payload.get("streams", [])
    if len(streams) != 1:
        raise ValueError(f"expected one video stream, found {len(streams)}")
    stream = streams[0]
    width = int(stream.get("width", 0))
    height = int(stream.get("height", 0))
    if width <= 0 or height <= 0:
        raise ValueError(f"invalid dimensions: {width} x {height}")
    return {
        "codec": stream.get("codec_name"),
        "width": width,
        "height": height,
        "fps": stream.get("r_frame_rate"),
        "frames": int(stream["nb_frames"]) if stream.get("nb_frames") else None,
        "duration_seconds": float(stream.get("duration", 0.0)),
    }


def _select_probe_records(
    records: list[VideoRecord], probe_per_group: int
) -> list[VideoRecord]:
    if probe_per_group <= 0:
        return []
    groups: dict[tuple[str, int], list[VideoRecord]] = defaultdict(list)
    for record in records:
        groups[(record.split, record.label)].append(record)
    selected: list[VideoRecord] = []
    for key in sorted(groups):
        selected.extend(
            sorted(groups[key], key=lambda item: item.video_id)[:probe_per_group]
        )
    return selected


def validate_extracted_protocol_1(
    records: Iterable[VideoRecord],
    raw_root: Path | str,
    *,
    probe_per_group: int = 1,
    full_probe: bool = False,
) -> dict[str, object]:
    """Validate every selected path and eye file, then probe representative AVIs."""

    materialized = list(records)
    root = Path(raw_root)
    protocol_result = validate_protocol_1(materialized)
    errors = list(protocol_result.errors)
    warnings = list(protocol_result.warnings)
    total_error_count = len(errors)

    missing_videos = 0
    missing_eye_files = 0
    invalid_avi_headers = 0
    invalid_eye_files = 0
    eye_rows = 0
    eye_detector_failures = 0
    video_bytes = 0
    eye_bytes = 0

    for record in materialized:
        video_path = record.video_path(root)
        eye_path = record.eye_path(root)

        if not video_path.is_file():
            missing_videos += 1
            total_error_count += 1
            _append_error(errors, f"Missing video: {video_path}.")
        else:
            video_bytes += video_path.stat().st_size
            try:
                if not _is_avi(video_path):
                    raise ValueError("RIFF/AVI signature not found")
            except (OSError, ValueError) as exc:
                invalid_avi_headers += 1
                total_error_count += 1
                _append_error(errors, f"Invalid AVI {video_path}: {exc}.")

        if not eye_path.is_file():
            missing_eye_files += 1
            total_error_count += 1
            _append_error(errors, f"Missing eye metadata: {eye_path}.")
        else:
            eye_bytes += eye_path.stat().st_size
            try:
                metadata = _read_eye_metadata(eye_path)
                eye_rows += metadata["rows"]
                eye_detector_failures += metadata["detector_failures"]
            except (OSError, ValueError) as exc:
                invalid_eye_files += 1
                total_error_count += 1
                _append_error(errors, f"Invalid eye metadata {eye_path}: {exc}.")

    if total_error_count > len(errors):
        warnings.append(
            f"Only the first {MAX_REPORTED_ERRORS} errors are included in this report."
        )

    if full_probe:
        probe_records = [
            record
            for record in materialized
            if record.video_path(root).is_file()
        ]
    else:
        probe_records = [
            record
            for record in _select_probe_records(
                materialized, probe_per_group=probe_per_group
            )
            if record.video_path(root).is_file()
        ]

    probes: list[dict[str, object]] = []
    probe_failures = 0
    for record in probe_records:
        video_path = record.video_path(root)
        try:
            details = _probe_video(video_path)
            probes.append(
                {
                    "video_id": record.video_id,
                    "split": record.split,
                    "label": record.label_name,
                    **details,
                }
            )
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            probe_failures += 1
            total_error_count += 1
            _append_error(errors, f"Cannot probe {video_path}: {exc}.")

    by_split = Counter(record.split for record in materialized)
    by_label = Counter(record.label_name for record in materialized)
    return {
        "ok": total_error_count == 0,
        "protocol": 1,
        "errors": errors,
        "error_count": total_error_count,
        "warnings": warnings,
        "protocol_counts": protocol_result.counts,
        "stats": {
            "records": len(materialized),
            "by_split": dict(sorted(by_split.items())),
            "by_label": dict(sorted(by_label.items())),
            "missing_videos": missing_videos,
            "missing_eye_files": missing_eye_files,
            "invalid_avi_headers": invalid_avi_headers,
            "invalid_eye_files": invalid_eye_files,
            "video_bytes": video_bytes,
            "eye_bytes": eye_bytes,
            "eye_rows": eye_rows,
            "eye_detector_failures": eye_detector_failures,
            "probed_videos": len(probe_records),
            "probe_failures": probe_failures,
        },
        "probes": probes,
    }

