"""Tests for processed face-crop manifest validation."""

from __future__ import annotations

import csv
from pathlib import Path
import tempfile
import unittest

from face_spoofing.data.frame_sampler import uniform_frame_indices
from face_spoofing.data.oulu import VideoRecord
from face_spoofing.data.preprocess import FRAME_MANIFEST_FIELDS
from face_spoofing.data.processed_validation import validate_processed_faces


def _record(video_id: str, *, split: str, subject_id: int, label: int) -> VideoRecord:
    return VideoRecord(
        video_id=video_id,
        split=split,
        protocol_label=1 if label == 0 else -1,
        label=label,
        label_name="spoof" if label else "live",
        attack_type="print" if label else "live",
        attack_instrument="printer_1" if label else "none",
        phone_id=1,
        session_id=1,
        subject_id=subject_id,
        access_id=2 if label else 1,
    )


def _rows_for(
    record: VideoRecord,
    output_root: Path,
    *,
    frames_per_video: int = 3,
    source_frame_count: int = 10,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    indices = uniform_frame_indices(source_frame_count, frames_per_video)
    video_root = output_root / "protocol_1" / record.video_id
    video_root.mkdir(parents=True, exist_ok=True)
    for sample_index, frame_index in enumerate(indices):
        face_path = video_root / f"sample_{sample_index:02d}.png"
        # Decoding is disabled in structural tests, but existence is always
        # part of the processed-data contract.
        face_path.write_bytes(b"placeholder")
        row = {field: "" for field in FRAME_MANIFEST_FIELDS}
        row.update(
            {
                "frame_id": f"{record.video_id}__{sample_index:02d}",
                "video_id": record.video_id,
                "sample_index": sample_index,
                "frame_index": frame_index,
                "split": record.split,
                "label": record.label,
                "label_name": record.label_name,
                "source_frame_count": source_frame_count,
                "source_width": 640,
                "source_height": 480,
                "face_path": face_path.as_posix(),
                "face_detected": True,
                "detector_score": 0.9,
                "crop_bbox_x1": 100,
                "crop_bbox_y1": 50,
                "crop_bbox_x2": 300,
                "crop_bbox_y2": 250,
                "crop_size": 256,
            }
        )
        rows.append(row)
    return rows


def _write_manifest(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FRAME_MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


class ProcessedValidationTests(unittest.TestCase):
    def test_valid_small_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "faces"
            records = [
                _record("train_video", split="train", subject_id=1, label=0),
                _record("dev_video", split="dev", subject_id=2, label=1),
            ]
            rows = [row for record in records for row in _rows_for(record, root)]
            manifest = Path(temporary) / "frames.csv"
            _write_manifest(manifest, rows)

            report = validate_processed_faces(
                records,
                manifest,
                root,
                frames_per_video=3,
                check_images=False,
            )

            self.assertTrue(report["ok"], report["errors"])
            self.assertEqual(report["error_count"], 0)
            self.assertEqual(report["stats"]["manifest_rows"], 6)
            self.assertEqual(report["stats"]["faces_detected"], 6)
            self.assertEqual(report["stats"]["detection_rate"], 1.0)
            self.assertEqual(
                report["stats"]["videos_with_zero_detected_faces"], 0
            )
            self.assertEqual(report["stats"]["orphan_pngs"], 0)
            self.assertEqual(report["stats"]["invalid_crop_metadata"], 0)

    def test_invalid_crop_bbox_is_reported_once_in_stats(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "faces"
            record = _record("train_video", split="train", subject_id=1, label=0)
            rows = _rows_for(record, root)
            rows[0]["crop_bbox_x2"] = 700

            report = validate_processed_faces(
                [record], rows, root, frames_per_video=3, check_images=False
            )

            messages = "\n".join(report["errors"])
            self.assertFalse(report["ok"])
            self.assertEqual(report["stats"]["invalid_crop_metadata"], 1)
            self.assertIn("crop bbox must be within", messages)
            self.assertIn("crop bbox must be square", messages)

    def test_some_detection_failures_are_allowed_above_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "faces"
            record = _record("train_video", split="train", subject_id=1, label=0)
            rows = _rows_for(record, root)
            failed_path = Path(str(rows[0]["face_path"]))
            failed_path.unlink()
            rows[0]["face_detected"] = False
            rows[0]["face_path"] = ""
            rows[0]["detector_status"] = "no_face"

            report = validate_processed_faces(
                [record],
                rows,
                root,
                frames_per_video=3,
                check_images=False,
                minimum_detection_rate=0.6,
            )

            self.assertTrue(report["ok"], report["errors"])
            self.assertAlmostEqual(report["stats"]["detection_rate"], 2 / 3)
            self.assertEqual(report["stats"]["faces_undetected"], 1)

    def test_low_detection_rate_and_zero_detection_video_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "faces"
            record = _record("train_video", split="train", subject_id=1, label=0)
            rows = _rows_for(record, root)
            for row in rows:
                Path(str(row["face_path"])).unlink()
                row["face_detected"] = False
                row["face_path"] = ""
                row["detector_status"] = "no_face"

            report = validate_processed_faces(
                [record],
                rows,
                root,
                frames_per_video=3,
                check_images=False,
            )

            messages = "\n".join(report["errors"])
            self.assertFalse(report["ok"])
            self.assertEqual(report["stats"]["detection_rate"], 0.0)
            self.assertEqual(
                report["stats"]["videos_with_zero_detected_faces"], 1
            )
            self.assertIn("zero detected faces", messages)
            self.assertIn("below the minimum target", messages)

    def test_reports_sampling_metadata_duplicates_and_orphans(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "faces"
            record = _record("train_video", split="train", subject_id=1, label=0)
            rows = _rows_for(record, root)
            rows.pop()
            rows[1]["sample_index"] = 0
            rows[1]["frame_index"] = 7
            rows[1]["split"] = "test"
            rows[1]["label"] = 1
            rows[1]["frame_id"] = rows[0]["frame_id"]
            rows[1]["face_path"] = rows[0]["face_path"]
            orphan = root / "protocol_1" / record.video_id / "orphan.png"
            orphan.write_bytes(b"placeholder")

            report = validate_processed_faces(
                [record], rows, root, frames_per_video=3, check_images=False
            )

            messages = "\n".join(report["errors"])
            self.assertFalse(report["ok"])
            self.assertIn("expected 3", messages)
            self.assertIn("sample_index values", messages)
            self.assertIn("frame_index mismatch", messages)
            self.assertIn("split mismatch", messages)
            self.assertIn("label mismatch", messages)
            self.assertIn("Duplicate frame_id", messages)
            self.assertIn("Duplicate face_path", messages)
            self.assertIn("Orphan PNG", messages)

    def test_subject_leakage_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "faces"
            records = [
                _record("train_video", split="train", subject_id=8, label=0),
                _record("dev_video", split="dev", subject_id=8, label=1),
            ]
            rows = [row for record in records for row in _rows_for(record, root)]

            report = validate_processed_faces(
                records, rows, root, frames_per_video=3, check_images=False
            )

            self.assertFalse(report["ok"])
            self.assertEqual(report["stats"]["leaking_subjects"], 1)
            self.assertTrue(
                any("Subject leakage" in error for error in report["errors"])
            )

    def test_detected_file_must_exist_even_when_decode_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "faces"
            record = _record("train_video", split="train", subject_id=1, label=0)
            rows = _rows_for(record, root)
            Path(str(rows[0]["face_path"])).unlink()

            report = validate_processed_faces(
                [record], rows, root, frames_per_video=3, check_images=False
            )

            self.assertFalse(report["ok"])
            self.assertEqual(report["stats"]["missing_face_files"], 1)

    def test_invalid_detection_target_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            validate_processed_faces(
                [], [], Path("unused"), minimum_detection_rate=float("nan")
            )
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            validate_processed_faces(
                [], [], Path("unused"), minimum_detection_rate=1.01
            )


if __name__ == "__main__":
    unittest.main()
