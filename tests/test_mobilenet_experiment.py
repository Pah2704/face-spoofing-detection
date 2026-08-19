from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace
import unittest

from face_spoofing.training.mobilenet_experiment import (
    MobileNetTrainingConfig,
    _balanced_subset_indices,
    _selection_key,
)


class MobileNetTrainingConfigTests(unittest.TestCase):
    def test_locked_default_main_run_is_valid(self) -> None:
        config = MobileNetTrainingConfig()

        config.validate()
        self.assertEqual(config.batch_size, 16)
        self.assertEqual(config.max_epochs, 15)
        self.assertEqual(config.minimum_epochs, 3)
        self.assertFalse(config.use_amp)

    def test_invalid_early_stopping_and_amp_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "minimum_epochs"):
            replace(MobileNetTrainingConfig(), minimum_epochs=16).validate()
        with self.assertRaisesRegex(ValueError, "AMP disabled"):
            replace(MobileNetTrainingConfig(), use_amp=True).validate()
        with self.assertRaisesRegex(ValueError, "backbone_learning_rate"):
            replace(
                MobileNetTrainingConfig(), backbone_learning_rate=0.0
            ).validate()


class MobileNetSelectionTests(unittest.TestCase):
    def test_checkpoint_key_prefers_acer_apcer_f1_then_earlier_epoch(self) -> None:
        base = {"acer": 0.1, "apcer": 0.08, "f1": 0.9}

        self.assertLess(
            _selection_key({**base, "acer": 0.09}, 5),
            _selection_key(base, 1),
        )
        self.assertLess(_selection_key(base, 2), _selection_key(base, 3))

    def test_smoke_subset_keeps_whole_balanced_videos(self) -> None:
        records = [
            SimpleNamespace(video_id=video_id, label=label)
            for video_id, label in (
                [("live_a", 0)] * 2
                + [("live_b", 0)] * 2
                + [("spoof_a", 1)] * 3
                + [("spoof_b", 1)] * 3
            )
        ]

        indices = _balanced_subset_indices(records, 1)
        selected = [records[index] for index in indices]

        self.assertEqual({record.video_id for record in selected}, {"live_a", "spoof_a"})
        self.assertEqual(len(selected), 5)


if __name__ == "__main__":
    unittest.main()
