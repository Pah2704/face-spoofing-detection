"""Binary ResNet18 model contract for the E03 baseline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math
import os
from pathlib import Path
from typing import Mapping


_CONFIGURED_WEIGHTS = object()
_CHECKPOINT_FORMAT = "face_spoofing.resnet18"
_CHECKPOINT_VERSION = 1


@dataclass(frozen=True, slots=True)
class ResNet18Config:
    architecture: str = "resnet18"
    experiment_id: str = "E03"
    weights: str | None = "IMAGENET1K_V1"
    output_dim: int = 1
    positive_label: int = 1
    negative_label: int = 0
    score_type: str = "logit"
    higher_score_label: int = 1
    freeze_backbone: bool = True
    input_channels: int = 3
    input_size: int = 224
    resize_size: int = 224
    interpolation: str = "bilinear"
    antialias: bool = True
    mean: tuple[float, float, float] = (0.485, 0.456, 0.406)
    std: tuple[float, float, float] = (0.229, 0.224, 0.225)

    def validate(self) -> None:
        if self.architecture != "resnet18":
            raise ValueError("ResNet18 experiments require architecture='resnet18'.")
        if self.experiment_id not in {"E03", "E04"}:
            raise ValueError("experiment_id must be 'E03' or 'E04'.")
        if self.weights not in {None, "IMAGENET1K_V1"}:
            raise ValueError("weights must be None or 'IMAGENET1K_V1'.")
        if (
            isinstance(self.output_dim, bool)
            or not isinstance(self.output_dim, int)
            or self.output_dim != 1
        ):
            raise ValueError("ResNet18 requires exactly one binary spoof logit.")
        if (self.negative_label, self.positive_label) != (0, 1):
            raise ValueError("ResNet18 requires live=0 and spoof=1 labels.")
        if self.score_type != "logit" or self.higher_score_label != 1:
            raise ValueError("ResNet18 requires a spoof-positive raw logit.")
        if not isinstance(self.freeze_backbone, bool):
            raise TypeError("freeze_backbone must be a boolean.")
        if self.input_channels != 3:
            raise ValueError("ImageNet ResNet18 requires three input channels.")
        if (self.input_size, self.resize_size) != (224, 224):
            raise ValueError("ResNet18 is locked to direct 224x224 resize.")
        if self.interpolation != "bilinear":
            raise ValueError("ResNet18 interpolation must be 'bilinear'.")
        if not isinstance(self.antialias, bool):
            raise TypeError("antialias must be a boolean.")
        if not self.antialias:
            raise ValueError("ResNet18 requires antialias=True.")
        for name, values, expected in (
            ("mean", self.mean, (0.485, 0.456, 0.406)),
            ("std", self.std, (0.229, 0.224, 0.225)),
        ):
            if not isinstance(values, tuple) or len(values) != 3:
                raise TypeError(f"{name} must be a tuple of three values.")
            if any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or (name == "std" and float(value) <= 0.0)
                for value in values
            ):
                raise ValueError(f"{name} contains invalid values.")
            if tuple(float(value) for value in values) != expected:
                raise ValueError(
                    f"ResNet18 {name} must match ImageNet normalization."
                )

    def to_dict(self) -> dict[str, object]:
        self.validate()
        payload = asdict(self)
        payload["mean"] = list(self.mean)
        payload["std"] = list(self.std)
        return payload

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "ResNet18Config":
        if not isinstance(payload, Mapping):
            raise TypeError("ResNet18 config payload must be a mapping.")
        known = {item.name for item in fields(cls)}
        unknown = sorted(set(payload) - known)
        if unknown:
            raise ValueError(f"Unknown ResNet18 config keys: {unknown}")
        values = dict(payload)
        for key in ("mean", "std"):
            if key in values and isinstance(values[key], list):
                values[key] = tuple(values[key])
        config = cls(**values)
        config.validate()
        return config


def _import_torch():
    try:
        import torch
        from torch import nn
        from torchvision.models import ResNet18_Weights, resnet18
    except ImportError as exc:
        raise RuntimeError(
            "ResNet18 requires the optional deep dependencies."
        ) from exc
    return torch, nn, ResNet18_Weights, resnet18


def _resolve_weights(name: str | None, weights_enum):
    if name is None:
        return None
    if name == "IMAGENET1K_V1":
        return weights_enum.IMAGENET1K_V1
    raise ValueError(f"unsupported ResNet18 weights: {name!r}")


def build_resnet18(
    config: ResNet18Config | None = None,
    *,
    weights_override: str | None | object = _CONFIGURED_WEIGHTS,
):
    config = config or ResNet18Config()
    config.validate()
    selected_weights = (
        config.weights
        if weights_override is _CONFIGURED_WEIGHTS
        else weights_override
    )
    if selected_weights not in {None, "IMAGENET1K_V1"}:
        raise ValueError("weights_override must be None or 'IMAGENET1K_V1'.")
    _, nn, weights_enum, factory = _import_torch()
    resolved_weights = _resolve_weights(selected_weights, weights_enum)
    network = factory(weights=resolved_weights)
    input_features = int(network.fc.in_features)
    network.fc = nn.Linear(input_features, 1)
    nn.init.normal_(network.fc.weight, mean=0.0, std=0.01)
    nn.init.zeros_(network.fc.bias)

    class BinaryResNet18(nn.Module):
        def __init__(self):
            super().__init__()
            self.network = network
            self.config = config
            self.metadata = {
                "architecture": "resnet18",
                "experiment_id": config.experiment_id,
                "weights": (
                    None
                    if resolved_weights is None
                    else f"ResNet18_Weights.{resolved_weights.name}"
                ),
                "preprocessing": {
                    "resize_size": [224, 224],
                    "crop_size": None,
                    "resize_policy": "direct_square",
                    "interpolation": "bilinear",
                    "antialias": True,
                    "mean": list(config.mean),
                    "std": list(config.std),
                },
                "output": {
                    "dimension": 1,
                    "score_type": "logit",
                    "loss": "BCEWithLogitsLoss",
                    "negative_label": 0,
                    "positive_label": 1,
                    "higher_score_means": "spoof",
                    "probability_transform": "sigmoid",
                },
                "initial_training_policy": {
                    "backbone_frozen": config.freeze_backbone,
                    "classifier_trainable": True,
                },
            }
            self._trainable_backbone_stages = 4
            if config.freeze_backbone:
                self.freeze_backbone()

        @property
        def classifier(self):
            return self.network.fc

        @property
        def backbone_trainable_blocks(self) -> int:
            return self._trainable_backbone_stages

        def _backbone_modules(self):
            return (
                self.network.conv1,
                self.network.bn1,
                self.network.relu,
                self.network.maxpool,
                self.network.layer1,
                self.network.layer2,
                self.network.layer3,
                self.network.layer4,
                self.network.avgpool,
            )

        def _stages(self):
            return (
                self.network.layer1,
                self.network.layer2,
                self.network.layer3,
                self.network.layer4,
            )

        def forward(self, inputs):
            return self.network(inputs)

        def freeze_backbone(self):
            for module in self._backbone_modules():
                for parameter in module.parameters():
                    parameter.requires_grad = False
            for parameter in self.classifier.parameters():
                parameter.requires_grad = True
            self._trainable_backbone_stages = 0
            if self.training:
                self._apply_backbone_modes()
            return self

        def unfreeze_backbone(self, last_n_blocks: int | None = None):
            if last_n_blocks is None:
                last_n_blocks = 4
            if (
                isinstance(last_n_blocks, bool)
                or not isinstance(last_n_blocks, int)
                or not 1 <= last_n_blocks <= 4
            ):
                raise ValueError("last_n_blocks must be between 1 and 4.")
            self.freeze_backbone()
            for stage in self._stages()[-last_n_blocks:]:
                for parameter in stage.parameters():
                    parameter.requires_grad = True
            self._trainable_backbone_stages = last_n_blocks
            if self.training:
                self._apply_backbone_modes()
            return self

        def _apply_backbone_modes(self):
            for module in self._backbone_modules():
                module.eval()
            for stage in self._stages()[-self._trainable_backbone_stages :]:
                if self._trainable_backbone_stages:
                    stage.train(True)

        def train(self, mode: bool = True):
            super().train(mode)
            if mode:
                self._apply_backbone_modes()
            return self

        def parameter_counts(self) -> dict[str, int]:
            classifier_ids = {id(parameter) for parameter in self.classifier.parameters()}
            backbone = [
                parameter
                for parameter in self.parameters()
                if id(parameter) not in classifier_ids
            ]
            classifier = list(self.classifier.parameters())
            return {
                "total": sum(parameter.numel() for parameter in self.parameters()),
                "trainable": sum(
                    parameter.numel()
                    for parameter in self.parameters()
                    if parameter.requires_grad
                ),
                "backbone_total": sum(parameter.numel() for parameter in backbone),
                "backbone_trainable": sum(
                    parameter.numel()
                    for parameter in backbone
                    if parameter.requires_grad
                ),
                "classifier_total": sum(parameter.numel() for parameter in classifier),
                "classifier_trainable": sum(
                    parameter.numel()
                    for parameter in classifier
                    if parameter.requires_grad
                ),
            }

    model = BinaryResNet18()
    assert_spoof_logit_contract(model)
    return model


def assert_spoof_logit_contract(model) -> None:
    config = getattr(model, "config", None)
    if not isinstance(config, ResNet18Config):
        raise ValueError("model has no ResNet18Config score contract.")
    config.validate()
    if getattr(model.classifier, "out_features", None) != 1:
        raise ValueError("ResNet18 classifier must produce one spoof logit.")


def spoof_probability(logits):
    torch, _, _, _ = _import_torch()
    if logits.ndim == 0 or logits.shape[-1] != 1:
        raise ValueError("expected logits with final dimension one.")
    return torch.sigmoid(logits)


def save_resnet18_checkpoint(
    path: str | Path,
    model,
    *,
    extra_metadata: Mapping[str, object] | None = None,
) -> Path:
    assert_spoof_logit_contract(model)
    torch, _, _, _ = _import_torch()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "format": _CHECKPOINT_FORMAT,
        "format_version": _CHECKPOINT_VERSION,
        "config": model.config.to_dict(),
        "model_metadata": dict(model.metadata),
        "training_state": {
            "backbone_trainable_blocks": model.backbone_trainable_blocks,
        },
        "extra_metadata": dict(extra_metadata or {}),
        "state_dict": model.state_dict(),
    }
    temporary = target.with_name(target.name + ".tmp")
    temporary.unlink(missing_ok=True)
    try:
        torch.save(payload, temporary)
        os.replace(temporary, target)
        target.chmod(0o644)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return target


def load_resnet18_checkpoint(
    path: str | Path,
    *,
    map_location: str | object = "cpu",
):
    torch, _, _, _ = _import_torch()
    payload = torch.load(path, map_location=map_location, weights_only=True)
    if not isinstance(payload, dict) or payload.get("format") != _CHECKPOINT_FORMAT:
        raise ValueError("unsupported ResNet18 checkpoint format.")
    if payload.get("format_version") != _CHECKPOINT_VERSION:
        raise ValueError("unsupported ResNet18 checkpoint version.")
    config_payload = payload.get("config")
    state_dict = payload.get("state_dict")
    if not isinstance(config_payload, Mapping) or not isinstance(state_dict, Mapping):
        raise ValueError("ResNet18 checkpoint is incomplete.")
    config = ResNet18Config.from_dict(config_payload)
    model = build_resnet18(config, weights_override=None)
    model.load_state_dict(state_dict, strict=True)
    state = payload.get("training_state", {})
    count = state.get("backbone_trainable_blocks", 0)
    if count == 0:
        model.freeze_backbone()
    else:
        model.unfreeze_backbone(last_n_blocks=int(count))
    saved_metadata = payload.get("model_metadata")
    if isinstance(saved_metadata, Mapping):
        model.metadata = dict(saved_metadata)
    extra = payload.get("extra_metadata", {})
    if not isinstance(extra, Mapping):
        raise ValueError("checkpoint extra_metadata is invalid.")
    assert_spoof_logit_contract(model)
    return model, dict(extra)


__all__ = [
    "ResNet18Config",
    "assert_spoof_logit_contract",
    "build_resnet18",
    "load_resnet18_checkpoint",
    "save_resnet18_checkpoint",
    "spoof_probability",
]
