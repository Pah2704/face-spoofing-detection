"""Manifest generation for OULU-NPU protocol records."""

from __future__ import annotations

from collections import Counter
import csv
import json
import os
from pathlib import Path
import tempfile
from typing import Iterable

from .oulu import VideoRecord


MANIFEST_FIELDS = (
    "video_id",
    "split",
    "label",
    "label_name",
    "protocol_label",
    "attack_type",
    "attack_instrument",
    "phone_id",
    "session_id",
    "subject_id",
    "access_id",
    "video_path",
    "eye_path",
    "archive_path",
    "archive_member",
    "extracted",
    "readable",
    "codec",
    "width",
    "height",
    "fps",
    "num_frames",
    "duration_seconds",
    "video_bytes",
    "eye_bytes",
)


def _portable_path(path: Path) -> str:
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def record_to_row(
    record: VideoRecord,
    raw_root: Path,
    probe_by_video_id: dict[str, dict[str, object]] | None = None,
) -> dict[str, object]:
    video_path = record.video_path(raw_root)
    eye_path = record.eye_path(raw_root)
    video_exists = video_path.is_file()
    eye_exists = eye_path.is_file()
    probe = (
        (probe_by_video_id or {}).get(record.video_id, {})
        if video_exists
        else {}
    )
    return {
        "video_id": record.video_id,
        "split": record.split,
        "label": record.label,
        "label_name": record.label_name,
        "protocol_label": record.protocol_label,
        "attack_type": record.attack_type,
        "attack_instrument": record.attack_instrument,
        "phone_id": record.phone_id,
        "session_id": record.session_id,
        "subject_id": record.subject_id,
        "access_id": record.access_id,
        "video_path": _portable_path(video_path),
        "eye_path": _portable_path(eye_path),
        "archive_path": _portable_path(raw_root / record.archive_name),
        "archive_member": record.video_member,
        "extracted": str(video_exists and eye_exists).lower(),
        "readable": (
            "true" if probe else ("false" if not video_exists else "")
        ),
        "codec": probe.get("codec", ""),
        "width": probe.get("width", ""),
        "height": probe.get("height", ""),
        "fps": probe.get("fps", ""),
        "num_frames": probe.get("frames", ""),
        "duration_seconds": probe.get("duration_seconds", ""),
        "video_bytes": video_path.stat().st_size if video_exists else "",
        "eye_bytes": eye_path.stat().st_size if eye_exists else "",
    }


def _atomic_text_writer(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        prefix=path.name + ".",
        suffix=".tmp",
        dir=path.parent,
        delete=False,
    )


def write_json_atomic(path: Path | str, payload: object) -> None:
    destination = Path(path)
    handle = _atomic_text_writer(destination)
    temporary = Path(handle.name)
    try:
        with handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temporary, destination)
        destination.chmod(0o644)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def write_video_manifest(
    records: Iterable[VideoRecord],
    raw_root: Path | str,
    output_path: Path | str,
    probe_report_path: Path | str | None = None,
) -> dict[str, object]:
    """Write a deterministic CSV plus a compact JSON summary."""

    materialized = list(records)
    root = Path(raw_root)
    destination = Path(output_path)
    probe_by_video_id: dict[str, dict[str, object]] = {}
    if probe_report_path is not None and Path(probe_report_path).is_file():
        with Path(probe_report_path).open("r", encoding="utf-8") as handle:
            probe_report = json.load(handle)
        probe_by_video_id = {
            str(item["video_id"]): dict(item)
            for item in probe_report.get("probes", [])
            if isinstance(item, dict) and item.get("video_id")
        }
    handle = _atomic_text_writer(destination)
    temporary = Path(handle.name)
    try:
        with handle:
            writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
            writer.writeheader()
            for record in materialized:
                writer.writerow(
                    record_to_row(record, root, probe_by_video_id)
                )
        os.replace(temporary, destination)
        destination.chmod(0o644)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    by_split = Counter(record.split for record in materialized)
    by_label = Counter(record.label_name for record in materialized)
    extracted = sum(
        record.video_path(root).is_file() and record.eye_path(root).is_file()
        for record in materialized
    )
    summary = {
        "protocol": 1,
        "rows": len(materialized),
        "by_split": dict(sorted(by_split.items())),
        "by_label": dict(sorted(by_label.items())),
        "extracted_rows": extracted,
        "missing_rows": len(materialized) - extracted,
        "rows_with_probe_metadata": sum(
            record.video_id in probe_by_video_id for record in materialized
        ),
        "manifest": destination.as_posix(),
    }
    write_json_atomic(destination.with_suffix(".summary.json"), summary)
    return summary
