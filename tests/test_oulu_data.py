from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from face_spoofing.data.manifest import write_video_manifest
from face_spoofing.data.oulu import (
    OuluDataError,
    PROTOCOL_1_EXPECTED,
    SPLIT_ORDER,
    parse_protocol_line,
    parse_video_id,
    validate_protocol_1,
)


def build_complete_protocol():
    records = []
    for split in SPLIT_ORDER:
        expected = PROTOCOL_1_EXPECTED[split]
        for phone in range(1, 7):
            for session in sorted(expected["sessions"]):
                for subject in sorted(expected["subjects"]):
                    for access in range(1, 6):
                        label = (
                            1
                            if access == 1
                            else -2
                            if split == "test" and access in {4, 5}
                            else -1
                        )
                        video_id = (
                            f"{phone}_{session}_{subject:02d}_{access}"
                        )
                        records.append(
                            parse_protocol_line(
                                f"{label:+d},{video_id}",
                                split=split,
                                line_number=len(records) + 1,
                            )
                        )
    return records


class VideoIdTests(unittest.TestCase):
    def test_strict_video_id(self):
        self.assertEqual(parse_video_id("6_3_55_5"), (6, 3, 55, 5))

    def test_subject_must_be_zero_padded(self):
        with self.assertRaises(OuluDataError):
            parse_video_id("1_1_1_1")

    def test_out_of_range_subject_is_rejected(self):
        with self.assertRaises(OuluDataError):
            parse_video_id("1_1_99_1")


class ProtocolLineTests(unittest.TestCase):
    def test_live_mapping_is_spoof_negative(self):
        record = parse_protocol_line(
            "+1,1_1_01_1", split="train", line_number=1
        )
        self.assertEqual(record.label, 0)
        self.assertEqual(record.label_name, "live")

    def test_test_replay_uses_official_minus_two(self):
        record = parse_protocol_line(
            "-2,1_3_36_4", split="test", line_number=1
        )
        self.assertEqual(record.label, 1)
        self.assertEqual(record.attack_type, "replay")
        self.assertEqual(record.attack_instrument, "display_1")

    def test_inconsistent_label_is_rejected(self):
        with self.assertRaises(OuluDataError):
            parse_protocol_line(
                "-1,1_1_01_1", split="train", line_number=1
            )


class ProtocolValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = build_complete_protocol()

    def test_complete_official_cartesian_product(self):
        result = validate_protocol_1(self.records)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.counts["train"]["total"], 1200)
        self.assertEqual(result.counts["dev"]["total"], 900)
        self.assertEqual(result.counts["test"]["total"], 600)

    def test_missing_record_is_detected(self):
        result = validate_protocol_1(self.records[:-1])
        self.assertFalse(result.ok)
        self.assertTrue(
            any("missing" in error.lower() for error in result.errors)
        )

    def test_duplicate_record_is_detected(self):
        result = validate_protocol_1([*self.records, self.records[0]])
        self.assertFalse(result.ok)
        self.assertTrue(
            any("duplicate" in error.lower() for error in result.errors)
        )

    def test_manifest_is_deterministic_and_marks_missing_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "raw"
            output = Path(temporary) / "videos.csv"
            summary = write_video_manifest(
                self.records[:2], root, output
            )
            self.assertTrue(output.is_file())
            self.assertEqual(summary["rows"], 2)
            self.assertEqual(summary["extracted_rows"], 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("video_id,split,label", text)


if __name__ == "__main__":
    unittest.main()

