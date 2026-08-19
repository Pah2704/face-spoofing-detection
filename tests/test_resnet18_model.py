from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

import torch

from face_spoofing.models.resnet18 import (
    ResNet18Config,
    assert_spoof_logit_contract,
    build_resnet18,
    load_resnet18_checkpoint,
    save_resnet18_checkpoint,
)
from face_spoofing.training.mobilenet_experiment import CnnTrainingConfig
from face_spoofing.training.resnet_experiment import (
    _build_layer4_optimizer,
    _configure_layer4_finetune,
    run_resnet18_finetune_experiment,
)


class ResNet18ModelTests(unittest.TestCase):
    @staticmethod
    def config(**changes) -> ResNet18Config:
        return replace(ResNet18Config(weights=None), **changes)

    def test_frozen_backbone_and_output_contract(self) -> None:
        model = build_resnet18(self.config())
        counts = model.parameter_counts()

        self.assertEqual(counts["backbone_trainable"], 0)
        self.assertEqual(counts["classifier_trainable"], 513)
        model.train()
        self.assertFalse(model.network.layer4.training)
        self.assertTrue(model.classifier.training)
        with torch.no_grad():
            output = model(torch.zeros(2, 3, 64, 64))
        self.assertEqual(tuple(output.shape), (2, 1))
        assert_spoof_logit_contract(model)

    def test_unfreeze_tail_is_explicit(self) -> None:
        model = build_resnet18(self.config())
        model.unfreeze_backbone(last_n_blocks=1)

        self.assertEqual(model.backbone_trainable_blocks, 1)
        self.assertTrue(any(p.requires_grad for p in model.network.layer4.parameters()))
        self.assertTrue(all(not p.requires_grad for p in model.network.layer3.parameters()))

    def test_config_is_locked(self) -> None:
        ResNet18Config().validate()
        ResNet18Config(experiment_id="E04").validate()
        with self.assertRaisesRegex(ValueError, "weights"):
            self.config(weights="DEFAULT").validate()
        with self.assertRaisesRegex(ValueError, "ImageNet normalization"):
            self.config(mean=(0.5, 0.5, 0.5)).validate()
        with self.assertRaisesRegex(ValueError, "antialias=True"):
            self.config(antialias=False).validate()

    def test_checkpoint_round_trip_is_exact_and_offline(self) -> None:
        torch.manual_seed(42)
        model = build_resnet18(self.config())
        model.eval()
        inputs = torch.zeros(1, 3, 64, 64)
        with torch.no_grad():
            expected = model(inputs)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resnet18.pt"
            save_resnet18_checkpoint(path, model, extra_metadata={"epoch": 2})
            restored, metadata = load_resnet18_checkpoint(path)
        restored.eval()
        with torch.no_grad():
            actual = restored(inputs)
        torch.testing.assert_close(actual, expected, rtol=0.0, atol=0.0)
        self.assertEqual(metadata, {"epoch": 2})

    def test_checkpoint_restores_layer4_finetune_state(self) -> None:
        model = build_resnet18(self.config(experiment_id="E04"))
        model.unfreeze_backbone(last_n_blocks=1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resnet18_finetune.pt"
            save_resnet18_checkpoint(path, model)
            restored, _ = load_resnet18_checkpoint(path)

        self.assertEqual(restored.backbone_trainable_blocks, 1)
        self.assertTrue(
            all(p.requires_grad for p in restored.network.layer4.parameters())
        )
        self.assertTrue(
            all(not p.requires_grad for p in restored.network.layer3.parameters())
        )


class ResNet18FineTunePolicyTests(unittest.TestCase):
    def test_layer4_optimizer_groups_cover_only_layer4_and_head(self) -> None:
        model = build_resnet18(
            ResNet18Config(experiment_id="E04", weights=None)
        )
        _configure_layer4_finetune(model)
        config = CnnTrainingConfig(backbone_learning_rate=1e-5)
        optimizer = _build_layer4_optimizer(torch, model, config)

        self.assertEqual(model.backbone_trainable_blocks, 1)
        self.assertEqual(
            [(group["name"], group["lr"]) for group in optimizer.param_groups],
            [("resnet_layer4", 1e-5), ("classifier_head", 1e-4)],
        )
        grouped = {
            id(parameter)
            for group in optimizer.param_groups
            for parameter in group["params"]
        }
        trainable = {
            id(parameter)
            for parameter in model.parameters()
            if parameter.requires_grad
        }
        self.assertEqual(grouped, trainable)
        self.assertTrue(
            all(not p.requires_grad for p in model.network.layer3.parameters())
        )

    def test_e04_rejects_unregistered_learning_rate(self) -> None:
        with self.assertRaisesRegex(ValueError, "locked config mismatch"):
            run_resnet18_finetune_experiment(
                frame_manifest="unused.csv",
                run_root="unused",
                project_root=".",
                training_config=CnnTrainingConfig(
                    learning_rate=2e-4,
                    backbone_learning_rate=1e-5,
                ),
            )


if __name__ == "__main__":
    unittest.main()
