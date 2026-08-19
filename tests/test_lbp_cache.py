"""Tests for the content-addressed spatial-LBP feature cache."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from face_spoofing.features import (
    LbpCacheConfig,
    LbpCacheError,
    build_lbp_cache,
    load_lbp_cache,
)


_FIELDS = (
    "frame_id",
    "video_id",
    "sample_index",
    "frame_index",
    "split",
    "label",
    "face_path",
    "face_detected",
    "preprocess_fingerprint",
)


class LbpCacheTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "faces").mkdir()
        (self.root / "faces" / "train.crop").write_bytes(b"\x03train")
        (self.root / "faces" / "dev.crop").write_bytes(b"\x07dev")
        self.manifest = self.root / "data" / "manifests" / "frames.csv"
        self.manifest.parent.mkdir(parents=True)
        self.rows = [
            {
                "frame_id": "video_train__00",
                "video_id": "video_train",
                "sample_index": "0",
                "frame_index": "4",
                "split": "train",
                "label": "0",
                "face_path": "faces/train.crop",
                "face_detected": "True",
                "preprocess_fingerprint": "preprocess-abc",
            },
            {
                "frame_id": "video_dev__00",
                "video_id": "video_dev",
                "sample_index": "0",
                "frame_index": "9",
                "split": "dev",
                "label": "1",
                "face_path": "faces/dev.crop",
                "face_detected": "true",
                "preprocess_fingerprint": "preprocess-abc",
            },
            {
                "frame_id": "video_dev__01",
                "video_id": "video_dev",
                "sample_index": "1",
                "frame_index": "17",
                "split": "dev",
                "label": "1",
                "face_path": "",
                "face_detected": "False",
                "preprocess_fingerprint": "preprocess-abc",
            },
        ]
        self._write_manifest(self.rows)
        self.cache_root = self.root / "cache"

    def _write_manifest(self, rows: list[dict[str, str]]) -> None:
        with self.manifest.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _fake_extract(path: Path, config: LbpCacheConfig) -> np.ndarray:
        value = path.read_bytes()[0]
        return np.full(config.feature_dim, value, dtype=np.float32)

    def _build(self, config: LbpCacheConfig | None = None):
        with patch(
            "face_spoofing.features.cache._extract_one",
            side_effect=self._fake_extract,
        ):
            return build_lbp_cache(
                self.manifest,
                self.cache_root,
                config=config,
                workers=2,
                project_root=self.root,
            )

    def test_default_config_is_the_versioned_640_value_descriptor(self) -> None:
        config = LbpCacheConfig()

        config.validate()
        self.assertEqual(config.version, 1)
        self.assertEqual(config.color_mode, "grayscale")
        self.assertEqual(config.image_size, 128)
        self.assertEqual(config.resize_interpolation, "INTER_AREA")
        self.assertEqual((config.radius, config.points), (1, 8))
        self.assertEqual((config.grid_rows, config.grid_cols), (8, 8))
        self.assertEqual(config.feature_dim, 640)

    def test_rgb_config_is_a_versioned_1920_value_descriptor(self) -> None:
        config = LbpCacheConfig(color_mode="rgb")

        config.validate()
        self.assertEqual(config.version, 1)
        self.assertEqual(config.color_mode, "rgb")
        self.assertEqual(config.feature_dim, 1920)

    def test_invalid_color_mode_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "grayscale.*rgb"):
            LbpCacheConfig(color_mode="hsv").validate()

    def test_rgb_and_grayscale_have_distinct_content_addresses(self) -> None:
        grayscale = self._build()
        rgb = self._build(LbpCacheConfig(color_mode="rgb"))

        self.assertNotEqual(grayscale.cache_dir, rgb.cache_dir)
        self.assertEqual(grayscale.features.shape, (2, 640))
        self.assertEqual(rgb.features.shape, (2, 1920))
        self.assertEqual(rgb.metadata["config"]["color_mode"], "rgb")
        self.assertEqual(rgb.metadata["feature_dim"], 1920)

    def test_build_writes_aligned_artifacts_and_excludes_no_face(self) -> None:
        dataset = self._build()

        self.assertEqual(dataset.features.shape, (2, 640))
        self.assertEqual(dataset.features.dtype, np.float32)
        np.testing.assert_array_equal(dataset.features[:, 0], [3.0, 7.0])
        np.testing.assert_array_equal(
            dataset.frame_ids, ["video_train__00", "video_dev__00"]
        )
        np.testing.assert_array_equal(dataset.video_ids, ["video_train", "video_dev"])
        np.testing.assert_array_equal(dataset.sample_indices, [0, 0])
        np.testing.assert_array_equal(dataset.frame_indices, [4, 9])
        np.testing.assert_array_equal(dataset.splits, ["train", "dev"])
        np.testing.assert_array_equal(dataset.labels, [0, 1])
        np.testing.assert_array_equal(
            dataset.face_paths, ["faces/train.crop", "faces/dev.crop"]
        )
        np.testing.assert_array_equal(dataset.select_split("dev"), [1])
        np.testing.assert_array_equal(dataset.select_split("test"), [])
        self.assertEqual(len(dataset.excluded_rows), 1)
        self.assertEqual(dataset.excluded_rows[0]["frame_id"], "video_dev__01")
        self.assertEqual(dataset.excluded_rows[0]["exclusion_reason"], "no_face")

        self.assertEqual(dataset.cache_dir.name, dataset.metadata["fingerprint"])
        self.assertEqual(dataset.metadata["manifest_path"], "data/manifests/frames.csv")
        self.assertEqual(dataset.metadata["manifest_rows"], 3)
        self.assertEqual(dataset.metadata["valid_rows"], 2)
        self.assertEqual(dataset.metadata["excluded_rows"], 1)
        self.assertEqual(dataset.metadata["feature_dim"], 640)
        self.assertTrue(dataset.metadata["complete"])
        self.assertEqual(
            {path.name for path in dataset.cache_dir.iterdir()},
            {"index.csv", "features.npz", "excluded.csv", "metadata.json"},
        )

        with (dataset.cache_dir / "index.csv").open(
            "r", encoding="utf-8", newline=""
        ) as handle:
            index = list(csv.DictReader(handle))
        self.assertEqual([row["feature_index"] for row in index], ["0", "1"])
        self.assertEqual([row["manifest_row"] for row in index], ["2", "3"])

    def test_valid_cache_hit_does_not_extract_again(self) -> None:
        first = self._build()

        with patch(
            "face_spoofing.features.cache._extract_one",
            side_effect=AssertionError("cache hit attempted extraction"),
        ):
            second = build_lbp_cache(
                self.manifest,
                self.cache_root,
                project_root=self.root,
            )

        self.assertEqual(first.cache_dir, second.cache_dir)
        np.testing.assert_array_equal(first.features, second.features)

    def test_valid_cache_hit_does_not_require_source_crops(self) -> None:
        first = self._build()
        (self.root / "faces" / "train.crop").unlink()
        (self.root / "faces" / "dev.crop").unlink()

        second = build_lbp_cache(
            self.manifest,
            self.cache_root,
            project_root=self.root,
        )

        self.assertEqual(first.cache_dir, second.cache_dir)
        np.testing.assert_array_equal(first.features, second.features)

    def test_manifest_bytes_are_part_of_the_content_address(self) -> None:
        first = self._build()
        with self.manifest.open("a", encoding="utf-8") as handle:
            handle.write("\n")

        second = self._build()

        self.assertNotEqual(first.cache_dir, second.cache_dir)
        self.assertTrue(first.cache_dir.is_dir())
        self.assertTrue(second.cache_dir.is_dir())

    def test_loader_rejects_checksum_tampering_and_builder_repairs_it(self) -> None:
        first = self._build()
        with (first.cache_dir / "index.csv").open("a", encoding="utf-8") as handle:
            handle.write("\n")

        with self.assertRaisesRegex(LbpCacheError, "checksum mismatch"):
            load_lbp_cache(first.cache_dir)

        repaired = self._build()
        self.assertEqual(repaired.cache_dir, first.cache_dir)
        self.assertEqual(repaired.features.shape, (2, 640))
        load_lbp_cache(repaired.cache_dir)

    def test_mixed_preprocessing_provenance_is_rejected(self) -> None:
        rows = [dict(row) for row in self.rows]
        rows[1]["preprocess_fingerprint"] = "different"
        self._write_manifest(rows)

        with self.assertRaisesRegex(LbpCacheError, "exactly one"):
            build_lbp_cache(
                self.manifest,
                self.cache_root,
                project_root=self.root,
            )

    def test_extraction_failure_leaves_no_partial_cache(self) -> None:
        with patch(
            "face_spoofing.features.cache._extract_one",
            side_effect=OSError("synthetic read failure"),
        ):
            with self.assertRaisesRegex(OSError, "synthetic read failure"):
                build_lbp_cache(
                    self.manifest,
                    self.cache_root,
                    workers=2,
                    project_root=self.root,
                )

        self.assertEqual(list(self.cache_root.iterdir()), [])

    def test_metadata_complete_marker_is_mandatory(self) -> None:
        dataset = self._build()
        metadata_path = dataset.cache_dir / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["complete"] = False
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

        with self.assertRaisesRegex(LbpCacheError, "not marked complete"):
            load_lbp_cache(dataset.cache_dir)


if __name__ == "__main__":
    unittest.main()
