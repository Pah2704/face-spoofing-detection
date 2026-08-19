"""Tests for the E02/E03 frame-level CNN dataset."""

from __future__ import annotations

import csv
from pathlib import Path
import tempfile
import unittest


try:
    from PIL import Image
    import torch
    from torch.utils.data import DataLoader

    from face_spoofing.data.cnn_dataset import (
        IMAGENET_MEAN,
        IMAGENET_STD,
        CnnDatasetError,
        CnnFrameDataset,
        CnnTransformConfig,
        make_dataloader_generator,
    )

    _DEEP_AVAILABLE = True
except (ImportError, OSError):
    _DEEP_AVAILABLE = False


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


@unittest.skipUnless(_DEEP_AVAILABLE, "torch/torchvision/Pillow deep extra unavailable")
class CnnFrameDatasetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.face_root = self.root / "faces"
        self.face_root.mkdir()
        self.manifest = self.root / "data" / "manifests" / "frames_protocol1.csv"
        self.manifest.parent.mkdir(parents=True)

        Image.new("RGB", (9, 7), (255, 128, 0)).save(
            self.face_root / "train_live.png"
        )
        asymmetric = Image.new("RGB", (4, 2))
        asymmetric.putdata(
            [
                (255, 0, 0),
                (255, 0, 0),
                (0, 0, 255),
                (0, 0, 255),
                (255, 0, 0),
                (255, 0, 0),
                (0, 0, 255),
                (0, 0, 255),
            ]
        )
        asymmetric.save(self.face_root / "train_spoof.png")
        Image.new("L", (5, 5), 64).save(self.face_root / "dev_gray.png")

        self.rows = [
            self._row(
                "train_live__00", "train_live", 0, "train", 0, "faces/train_live.png"
            ),
            self._row(
                "train_spoof__00",
                "train_spoof",
                0,
                "train",
                1,
                "faces/train_spoof.png",
            ),
            self._row(
                "dev_live__00", "dev_live", 0, "dev", 0, "faces/dev_gray.png"
            ),
            self._row(
                "dev_spoof__00", "dev_spoof", 0, "dev", 1, "", detected=False
            ),
        ]
        self._write_manifest(self.rows)

    @staticmethod
    def _row(
        frame_id: str,
        video_id: str,
        sample_index: int,
        split: str,
        label: int,
        face_path: str,
        *,
        detected: bool = True,
    ) -> dict[str, str]:
        return {
            "frame_id": frame_id,
            "video_id": video_id,
            "sample_index": str(sample_index),
            "frame_index": str(sample_index * 10),
            "split": split,
            "label": str(label),
            "face_path": face_path,
            "face_detected": str(detected),
            "preprocess_fingerprint": "preprocess-locked",
        }

    def _write_manifest(self, rows: list[dict[str, str]]) -> None:
        with self.manifest.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def test_eval_item_is_rgb_224_imagenet_normalized_and_deterministic(self) -> None:
        dataset = CnnFrameDataset(
            "data/manifests/frames_protocol1.csv",
            "train",
            project_root=self.root,
        )

        first = dataset[0]
        second = dataset[0]

        self.assertEqual(set(first), {"image", "label", "frame_id", "video_id"})
        self.assertEqual(first["image"].shape, (3, 224, 224))
        self.assertEqual(first["image"].dtype, torch.float32)
        self.assertTrue(first["image"].is_contiguous())
        self.assertEqual(first["label"].dtype, torch.long)
        self.assertEqual(first["label"].item(), 0)
        self.assertEqual(first["frame_id"], "train_live__00")
        self.assertEqual(first["video_id"], "train_live")
        torch.testing.assert_close(first["image"], second["image"], rtol=0, atol=0)

        expected = torch.tensor(
            [
                (1.0 - IMAGENET_MEAN[0]) / IMAGENET_STD[0],
                ((128.0 / 255.0) - IMAGENET_MEAN[1]) / IMAGENET_STD[1],
                (0.0 - IMAGENET_MEAN[2]) / IMAGENET_STD[2],
            ]
        )
        torch.testing.assert_close(first["image"][:, 100, 100], expected)

    def test_grayscale_source_is_converted_to_three_rgb_channels(self) -> None:
        dataset = CnnFrameDataset(self.manifest, "dev", project_root=self.root)

        item = dataset[0]

        self.assertEqual(item["image"].shape, (3, 224, 224))
        raw_channels = torch.stack(
            [
                item["image"][channel] * IMAGENET_STD[channel]
                + IMAGENET_MEAN[channel]
                for channel in range(3)
            ]
        )
        torch.testing.assert_close(raw_channels[0], raw_channels[1])
        torch.testing.assert_close(raw_channels[1], raw_channels[2])

    def test_selected_split_excludes_no_face_and_reports_coverage(self) -> None:
        dataset = CnnFrameDataset(self.manifest, "dev", project_root=self.root)

        self.assertEqual(len(dataset), 1)
        self.assertEqual(dataset.coverage.manifest_rows, 4)
        self.assertEqual(dataset.coverage.split_rows, 2)
        self.assertEqual(dataset.coverage.included_rows, 1)
        self.assertEqual(dataset.coverage.excluded_no_face_rows, 1)
        self.assertEqual(dataset.coverage.unique_videos, 1)
        self.assertEqual(dataset.coverage.live_frames, 1)
        self.assertEqual(dataset.coverage.spoof_frames, 0)
        self.assertEqual(dataset.coverage.detection_rate, 0.5)
        self.assertEqual(
            dataset.coverage.preprocess_fingerprint, "preprocess-locked"
        )
        self.assertEqual(
            dataset.coverage_metadata["manifest_path"],
            "data/manifests/frames_protocol1.csv",
        )
        self.assertEqual(len(dataset.coverage.manifest_sha256), 64)

    def test_training_horizontal_flip_is_the_only_spatial_augmentation(self) -> None:
        no_flip = CnnFrameDataset(
            self.manifest,
            "train",
            project_root=self.root,
            training=True,
            transform_config=CnnTransformConfig(horizontal_flip_probability=0.0),
        )
        always_flip = CnnFrameDataset(
            self.manifest,
            "train",
            project_root=self.root,
            training=True,
            transform_config=CnnTransformConfig(horizontal_flip_probability=1.0),
        )

        original = no_flip[1]["image"]
        flipped = always_flip[1]["image"]

        torch.testing.assert_close(flipped, torch.flip(original, dims=[2]))

    def test_transform_contract_is_fixed_to_imagenet_rgb_224(self) -> None:
        with self.assertRaisesRegex(ValueError, "image_size must be 224"):
            CnnTransformConfig(image_size=128).validate()
        with self.assertRaisesRegex(ValueError, "ImageNet mean"):
            CnnTransformConfig(mean=(0.5, 0.5, 0.5)).validate()
        with self.assertRaisesRegex(ValueError, "ImageNet std"):
            CnnTransformConfig(std=(0.5, 0.5, 0.5)).validate()

    def test_training_stream_is_repeatable_by_seed_worker_and_epoch(self) -> None:
        first = CnnFrameDataset(
            self.manifest,
            "train",
            project_root=self.root,
            training=True,
            seed=17,
        )
        second = CnnFrameDataset(
            self.manifest,
            "train",
            project_root=self.root,
            training=True,
            seed=17,
        )

        first_sequence = [first[1]["image"] for _ in range(8)]
        second_sequence = [second[1]["image"] for _ in range(8)]
        for left, right in zip(first_sequence, second_sequence):
            torch.testing.assert_close(left, right, rtol=0, atol=0)

        first.set_epoch(3)
        second.set_epoch(3)
        for _ in range(4):
            torch.testing.assert_close(
                first[1]["image"], second[1]["image"], rtol=0, atol=0
            )

    def test_default_collation_produces_training_ready_batch(self) -> None:
        dataset = CnnFrameDataset(self.manifest, "train", project_root=self.root)
        loader = DataLoader(
            dataset,
            batch_size=2,
            shuffle=True,
            generator=make_dataloader_generator(7),
        )

        batch = next(iter(loader))

        self.assertEqual(batch["image"].shape, (2, 3, 224, 224))
        self.assertEqual(batch["label"].shape, (2,))
        self.assertEqual(batch["label"].dtype, torch.long)
        self.assertEqual(len(batch["frame_id"]), 2)
        self.assertEqual(len(batch["video_id"]), 2)

    def test_training_augmentation_is_rejected_for_dev_or_test(self) -> None:
        with self.assertRaisesRegex(ValueError, "only for split='train'"):
            CnnFrameDataset(
                self.manifest,
                "dev",
                project_root=self.root,
                training=True,
            )

    def test_manifest_validation_rejects_duplicate_frame_id(self) -> None:
        rows = [dict(row) for row in self.rows]
        rows[1]["frame_id"] = rows[0]["frame_id"]
        self._write_manifest(rows)

        with self.assertRaisesRegex(CnnDatasetError, "duplicate frame_id"):
            CnnFrameDataset(self.manifest, "train", project_root=self.root)

    def test_manifest_validation_rejects_invalid_boolean(self) -> None:
        rows = [dict(row) for row in self.rows]
        rows[0]["face_detected"] = "maybe"
        self._write_manifest(rows)

        with self.assertRaisesRegex(CnnDatasetError, "must be true or false"):
            CnnFrameDataset(self.manifest, "train", project_root=self.root)

    def test_manifest_validation_rejects_missing_or_escaping_crop(self) -> None:
        rows = [dict(row) for row in self.rows]
        rows[0]["face_path"] = "../outside.png"
        self._write_manifest(rows)
        with self.assertRaisesRegex(CnnDatasetError, "escapes project_root"):
            CnnFrameDataset(self.manifest, "train", project_root=self.root)

        rows[0]["face_path"] = "faces/missing.png"
        self._write_manifest(rows)
        with self.assertRaisesRegex(CnnDatasetError, "does not exist"):
            CnnFrameDataset(self.manifest, "train", project_root=self.root)

    def test_other_split_crop_is_not_touched_before_that_split_is_built(self) -> None:
        rows = [dict(row) for row in self.rows]
        rows[2]["face_path"] = "faces/not_created_test_isolation.png"
        self._write_manifest(rows)

        train = CnnFrameDataset(self.manifest, "train", project_root=self.root)
        self.assertEqual(len(train), 2)
        with self.assertRaisesRegex(CnnDatasetError, "does not exist"):
            CnnFrameDataset(self.manifest, "dev", project_root=self.root)

    def test_corrupt_crop_has_frame_specific_decode_error(self) -> None:
        (self.face_root / "train_live.png").write_bytes(b"not an image")
        dataset = CnnFrameDataset(self.manifest, "train", project_root=self.root)

        with self.assertRaisesRegex(CnnDatasetError, "train_live__00"):
            dataset[0]


if __name__ == "__main__":
    unittest.main()
