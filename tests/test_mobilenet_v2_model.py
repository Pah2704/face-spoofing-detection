from __future__ import annotations

from dataclasses import replace
import tempfile
from pathlib import Path
import unittest

import torch

from face_spoofing.models.mobilenet_v2 import (
    MobileNetV2Config,
    assert_spoof_logit_contract,
    build_mobilenet_v2,
    load_mobilenet_v2_checkpoint,
    save_mobilenet_v2_checkpoint,
    spoof_probability,
)


class MobileNetV2ModelTests(unittest.TestCase):
    @staticmethod
    def config(**changes) -> MobileNetV2Config:
        return replace(MobileNetV2Config(weights=None), **changes)

    def test_default_contract_uses_imagenet_weights(self):
        config = MobileNetV2Config()
        config.validate()
        self.assertEqual(config.weights, "IMAGENET1K_V2")
        self.assertEqual(config.positive_label, 1)
        self.assertEqual(config.score_type, "logit")

    def test_frozen_backbone_has_trainable_classifier_and_one_logit(self):
        model = build_mobilenet_v2(self.config())
        counts = model.parameter_counts()

        self.assertEqual(counts["backbone_trainable"], 0)
        self.assertGreater(counts["classifier_trainable"], 0)
        self.assertEqual(
            counts["classifier_trainable"], counts["classifier_total"]
        )
        self.assertEqual(counts["trainable"], counts["classifier_total"])
        self.assertEqual(model.backbone_trainable_blocks, 0)

        model.train()
        self.assertFalse(model.features[0].training)
        self.assertTrue(model.classifier.training)
        inputs = torch.zeros((2, 3, 224, 224), dtype=torch.float32)
        with torch.no_grad():
            logits = model(inputs)
        self.assertEqual(tuple(logits.shape), (2, 1))
        assert_spoof_logit_contract(model)

    def test_new_binary_head_uses_torchvision_initialization_policy(self):
        torch.manual_seed(42)
        model = build_mobilenet_v2(self.config())

        self.assertEqual(float(model.classifier[-1].bias.item()), 0.0)
        self.assertLess(abs(float(model.classifier[-1].weight.mean())), 0.002)
        self.assertAlmostEqual(
            float(model.classifier[-1].weight.std()), 0.01, delta=0.001
        )

    def test_unfreeze_last_blocks_changes_only_requested_backbone_tail(self):
        model = build_mobilenet_v2(self.config())
        model.unfreeze_backbone(last_n_blocks=2)
        blocks = list(model.features)

        self.assertEqual(model.backbone_trainable_blocks, 2)
        self.assertTrue(
            all(
                not parameter.requires_grad
                for block in blocks[:-2]
                for parameter in block.parameters()
            )
        )
        self.assertTrue(
            all(
                parameter.requires_grad
                for block in blocks[-2:]
                for parameter in block.parameters()
            )
        )
        self.assertGreater(model.parameter_counts()["backbone_trainable"], 0)
        with self.assertRaisesRegex(ValueError, "between 1"):
            model.unfreeze_backbone(last_n_blocks=0)

    def test_score_orientation_is_spoof_positive(self):
        logits = torch.tensor([[-2.0], [0.0], [2.0]])
        probabilities = spoof_probability(logits)
        self.assertTrue(torch.all(probabilities[1:] > probabilities[:-1]))
        self.assertLess(float(probabilities[0]), 0.5)
        self.assertGreater(float(probabilities[-1]), 0.5)
        with self.assertRaisesRegex(ValueError, "final dimension"):
            spoof_probability(torch.zeros(2, 2))

    def test_config_validation_is_strict(self):
        with self.assertRaisesRegex(ValueError, "weights"):
            self.config(weights="IMAGENET1K_V1").validate()
        with self.assertRaisesRegex(ValueError, "exactly one"):
            self.config(output_dim=2).validate()
        with self.assertRaisesRegex(ValueError, "higher value means spoof"):
            self.config(higher_score_label=0).validate()
        with self.assertRaisesRegex(ValueError, "dropout"):
            self.config(dropout=1.0).validate()
        with self.assertRaisesRegex(ValueError, "antialias=True"):
            self.config(antialias=False).validate()
        with self.assertRaisesRegex(ValueError, "ImageNet normalization"):
            self.config(mean=(0.5, 0.5, 0.5)).validate()
        with self.assertRaisesRegex(ValueError, "Unknown"):
            MobileNetV2Config.from_dict({"weight": None})
        with self.assertRaisesRegex(TypeError, "tuple"):
            self.config(mean=[0.1, 0.2, 0.3]).validate()

    def test_checkpoint_round_trip_does_not_need_pretrained_weights(self):
        model = build_mobilenet_v2(self.config())
        with torch.no_grad():
            model.classifier[-1].bias.fill_(0.75)
        inputs = torch.zeros((1, 3, 64, 64), dtype=torch.float32)
        model.eval()
        with torch.no_grad():
            expected = model(inputs)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mobilenet_v2.pt"
            save_mobilenet_v2_checkpoint(
                path,
                model,
                extra_metadata={"epoch": 3},
            )
            restored, extra = load_mobilenet_v2_checkpoint(path)

        restored.eval()
        with torch.no_grad():
            actual = restored(inputs)
        torch.testing.assert_close(actual, expected, rtol=0.0, atol=0.0)
        self.assertEqual(extra, {"epoch": 3})
        self.assertEqual(restored.config.weights, None)
        self.assertEqual(restored.backbone_trainable_blocks, 0)

    def test_metadata_records_weights_preprocessing_and_output_contract(self):
        model = build_mobilenet_v2(self.config())
        self.assertIsNone(model.metadata["weights"])
        self.assertEqual(
            model.metadata["preprocessing"]["resize_size"], [224, 224]
        )
        self.assertIsNone(model.metadata["preprocessing"]["crop_size"])
        self.assertEqual(
            model.metadata["preprocessing"]["mean"],
            [0.485, 0.456, 0.406],
        )
        self.assertEqual(model.metadata["output"]["loss"], "BCEWithLogitsLoss")
        self.assertEqual(model.metadata["output"]["higher_score_means"], "spoof")


if __name__ == "__main__":
    unittest.main()
