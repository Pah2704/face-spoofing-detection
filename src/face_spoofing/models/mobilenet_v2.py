"""Binary MobileNetV2 model contract for the E02 deep-learning baseline.

The public factory imports torchvision lazily so that the classical E01
baseline remains usable when the optional deep-learning dependencies are not
installed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math
import os
from pathlib import Path
from typing import Mapping


_CONFIGURED_WEIGHTS = object()
_CHECKPOINT_FORMAT = "face_spoofing.mobilenet_v2"
_CHECKPOINT_VERSION = 1


@dataclass(frozen=True, slots=True)
class MobileNetV2Config:
    """Locked architecture and inference-preprocessing contract for E02."""

    architecture: str = "mobilenet_v2"
    experiment_id: str = "E02"
    weights: str | None = "IMAGENET1K_V2"
    output_dim: int = 1
    positive_label: int = 1
    negative_label: int = 0
    score_type: str = "logit"
    higher_score_label: int = 1
    dropout: float = 0.2
    freeze_backbone: bool = True
    input_channels: int = 3
    input_size: int = 224
    resize_size: int = 224
    interpolation: str = "bilinear"
    antialias: bool = True
    mean: tuple[float, float, float] = (0.485, 0.456, 0.406)
    std: tuple[float, float, float] = (0.229, 0.224, 0.225)

    def validate(self) -> None:
        """Reject configuration drift that would make scores ambiguous."""

        if self.architecture != "mobilenet_v2":
            raise ValueError("architecture must be 'mobilenet_v2'.")
        if self.experiment_id != "E02":
            raise ValueError("experiment_id must be 'E02'.")
        if self.weights is not None and (
            not isinstance(self.weights, str)
            or self.weights != "IMAGENET1K_V2"
        ):
            raise ValueError(
                "weights must be None or 'IMAGENET1K_V2' for the locked E02 "
                "preprocessing contract."
            )
        if (
            isinstance(self.output_dim, bool)
            or not isinstance(self.output_dim, int)
            or self.output_dim != 1
        ):
            raise ValueError("E02 requires exactly one binary spoof logit.")
        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (self.negative_label, self.positive_label)
        ) or (self.negative_label, self.positive_label) != (0, 1):
            raise ValueError("E02 requires live=0 and spoof=1 labels.")
        if (
            self.score_type != "logit"
            or isinstance(self.higher_score_label, bool)
            or not isinstance(self.higher_score_label, int)
            or self.higher_score_label != 1
        ):
            raise ValueError(
                "E02 requires a raw logit whose higher value means spoof (1)."
            )
        if (
            isinstance(self.dropout, bool)
            or not isinstance(self.dropout, (int, float))
            or not math.isfinite(float(self.dropout))
            or not 0.0 <= float(self.dropout) < 1.0
        ):
            raise ValueError("dropout must be finite and in [0, 1).")
        if not isinstance(self.freeze_backbone, bool):
            raise TypeError("freeze_backbone must be a boolean.")
        if (
            isinstance(self.input_channels, bool)
            or not isinstance(self.input_channels, int)
            or self.input_channels != 3
        ):
            raise ValueError("ImageNet MobileNetV2 requires three input channels.")
        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (self.input_size, self.resize_size)
        ) or (self.input_size, self.resize_size) != (224, 224):
            raise ValueError(
                "E02 is locked to direct 224x224 resize and input_size=224."
            )
        if self.interpolation != "bilinear":
            raise ValueError("E02 interpolation must be 'bilinear'.")
        if not isinstance(self.antialias, bool):
            raise TypeError("antialias must be a boolean.")
        if not self.antialias:
            raise ValueError("E02 requires antialias=True.")
        self._validate_normalization("mean", self.mean, positive=False)
        self._validate_normalization("std", self.std, positive=True)
        if tuple(float(value) for value in self.mean) != (0.485, 0.456, 0.406):
            raise ValueError("E02 mean must match ImageNet normalization.")
        if tuple(float(value) for value in self.std) != (0.229, 0.224, 0.225):
            raise ValueError("E02 std must match ImageNet normalization.")

    @staticmethod
    def _validate_normalization(
        name: str,
        values: tuple[float, float, float],
        *,
        positive: bool,
    ) -> None:
        if not isinstance(values, tuple) or len(values) != 3:
            raise TypeError(f"{name} must be a tuple of exactly three values.")
        for value in values:
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or (positive and float(value) <= 0.0)
            ):
                qualifier = "finite positive" if positive else "finite"
                raise ValueError(f"{name} values must be {qualifier} numbers.")

    def to_dict(self) -> dict[str, object]:
        self.validate()
        payload = asdict(self)
        payload["mean"] = list(self.mean)
        payload["std"] = list(self.std)
        return payload

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "MobileNetV2Config":
        """Build a config while rejecting misspelled or unsupported keys."""

        if not isinstance(payload, Mapping):
            raise TypeError("MobileNetV2 config payload must be a mapping.")
        known = {item.name for item in fields(cls)}
        unknown = sorted(set(payload) - known)
        if unknown:
            raise ValueError(f"Unknown MobileNetV2 config keys: {unknown}")
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
        from torchvision.models import MobileNet_V2_Weights, mobilenet_v2
    except ImportError as exc:  # pragma: no cover - depends on optional install
        raise RuntimeError(
            "MobileNetV2 requires the optional 'deep' dependencies: torch and "
            "torchvision."
        ) from exc
    return torch, nn, MobileNet_V2_Weights, mobilenet_v2


def _resolve_weights(weight_name: str | None, weights_enum):
    if weight_name is None:
        return None
    if weight_name == "IMAGENET1K_V2":
        return weights_enum.IMAGENET1K_V2
    raise ValueError(f"Unsupported MobileNetV2 weights: {weight_name!r}")


def _preprocessing_metadata(config: MobileNetV2Config, weights) -> dict[str, object]:
    metadata: dict[str, object] = {
        "resize_size": [config.resize_size, config.resize_size],
        "crop_size": None,
        "resize_policy": "direct_square",
        "input_channels": config.input_channels,
        "interpolation": config.interpolation,
        "antialias": config.antialias,
        "mean": list(config.mean),
        "std": list(config.std),
        "pixel_range_before_normalization": [0.0, 1.0],
    }
    if weights is not None:
        transform = weights.transforms()
        metadata["torchvision_weights_transform"] = {
            "resize_size": list(transform.resize_size),
            "crop_size": list(transform.crop_size),
            "interpolation": transform.interpolation.value,
            "antialias": bool(transform.antialias),
            "mean": list(transform.mean),
            "std": list(transform.std),
        }
    return metadata


def _build_metadata(
    config: MobileNetV2Config,
    resolved_weights,
) -> dict[str, object]:
    return {
        "architecture": config.architecture,
        "experiment_id": config.experiment_id,
        "weights": (
            None
            if resolved_weights is None
            else f"MobileNet_V2_Weights.{resolved_weights.name}"
        ),
        "preprocessing": _preprocessing_metadata(config, resolved_weights),
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


def build_mobilenet_v2(
    config: MobileNetV2Config | None = None,
    *,
    weights_override: str | None | object = _CONFIGURED_WEIGHTS,
):
    """Build a one-logit MobileNetV2 with a frozen backbone by default.

    ``weights_override=None`` is useful when restoring a checkpoint because it
    avoids downloading ImageNet weights before the saved state is loaded.
    """

    config = config or MobileNetV2Config()
    config.validate()
    selected_weights = (
        config.weights
        if weights_override is _CONFIGURED_WEIGHTS
        else weights_override
    )
    if selected_weights is not None and selected_weights != "IMAGENET1K_V2":
        raise ValueError(
            "weights_override must be None or 'IMAGENET1K_V2'."
        )

    _, nn, weights_enum, mobilenet_factory = _import_torch()
    resolved_weights = _resolve_weights(selected_weights, weights_enum)
    network = mobilenet_factory(
        weights=resolved_weights,
        dropout=float(config.dropout),
    )
    input_features = int(network.classifier[-1].in_features)
    network.classifier[-1] = nn.Linear(input_features, 1)
    nn.init.normal_(network.classifier[-1].weight, mean=0.0, std=0.01)
    nn.init.zeros_(network.classifier[-1].bias)

    class BinaryMobileNetV2(nn.Module):
        """Wrapper that also keeps frozen BatchNorm statistics immutable."""

        def __init__(self):
            super().__init__()
            self.network = network
            self.config = config
            self.metadata = _build_metadata(config, resolved_weights)
            self._trainable_backbone_blocks = len(self.features)
            if config.freeze_backbone:
                self.freeze_backbone()
            else:
                self.unfreeze_backbone()

        @property
        def features(self):
            return self.network.features

        @property
        def classifier(self):
            return self.network.classifier

        @property
        def backbone_trainable_blocks(self) -> int:
            return self._trainable_backbone_blocks

        def forward(self, inputs):
            return self.network(inputs)

        def freeze_backbone(self):
            self._set_trainable_backbone_blocks(0)
            return self

        def unfreeze_backbone(self, last_n_blocks: int | None = None):
            number_of_blocks = len(self.features)
            if last_n_blocks is None:
                last_n_blocks = number_of_blocks
            if (
                isinstance(last_n_blocks, bool)
                or not isinstance(last_n_blocks, int)
                or not 1 <= last_n_blocks <= number_of_blocks
            ):
                raise ValueError(
                    "last_n_blocks must be an integer between 1 and "
                    f"{number_of_blocks}."
                )
            self._set_trainable_backbone_blocks(last_n_blocks)
            return self

        def _set_trainable_backbone_blocks(self, count: int) -> None:
            split_index = len(self.features) - count
            for index, block in enumerate(self.features):
                requires_grad = index >= split_index
                for parameter in block.parameters():
                    parameter.requires_grad = requires_grad
            for parameter in self.classifier.parameters():
                parameter.requires_grad = True
            self._trainable_backbone_blocks = count
            if self.training:
                self._apply_backbone_module_modes()

        def _apply_backbone_module_modes(self) -> None:
            split_index = len(self.features) - self._trainable_backbone_blocks
            for index, block in enumerate(self.features):
                block.train(index >= split_index)

        def train(self, mode: bool = True):
            super().train(mode)
            if mode:
                self._apply_backbone_module_modes()
            return self

        def parameter_counts(self) -> dict[str, int]:
            backbone = list(self.features.parameters())
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
                "classifier_total": sum(
                    parameter.numel() for parameter in classifier
                ),
                "classifier_trainable": sum(
                    parameter.numel()
                    for parameter in classifier
                    if parameter.requires_grad
                ),
            }

    model = BinaryMobileNetV2()
    assert_spoof_logit_contract(model)
    return model


def assert_spoof_logit_contract(model) -> None:
    """Ensure a model exposes one raw score oriented toward spoof label 1."""

    config = getattr(model, "config", None)
    if not isinstance(config, MobileNetV2Config):
        raise ValueError("Model has no MobileNetV2Config score contract.")
    config.validate()
    classifier = getattr(model, "classifier", None)
    if classifier is None or not classifier:
        raise ValueError("Model has no classifier head.")
    output_features = getattr(classifier[-1], "out_features", None)
    if output_features != 1:
        raise ValueError(
            f"Expected one spoof logit, found out_features={output_features!r}."
        )


def spoof_probability(logits):
    """Convert spoof-positive raw logits to probabilities with sigmoid."""

    torch, _, _, _ = _import_torch()
    if logits.ndim == 0 or logits.shape[-1] != 1:
        raise ValueError("Expected logits with final dimension equal to one.")
    return torch.sigmoid(logits)


def save_mobilenet_v2_checkpoint(
    path: str | Path,
    model,
    *,
    extra_metadata: Mapping[str, object] | None = None,
) -> Path:
    """Save a portable state-dict checkpoint without serializing Python code."""

    assert_spoof_logit_contract(model)
    if extra_metadata is not None and not isinstance(extra_metadata, Mapping):
        raise TypeError("extra_metadata must be a mapping when provided.")
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
    # A fixed temporary basename keeps PyTorch's internal ZIP member prefix
    # deterministic. Runs never share a destination directory and the final
    # path is fail-if-exists at run creation, so there is no writer collision.
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


def load_mobilenet_v2_checkpoint(
    path: str | Path,
    *,
    map_location: str | object = "cpu",
):
    """Restore a checkpoint without fetching its original ImageNet weights."""

    torch, _, _, _ = _import_torch()
    payload = torch.load(path, map_location=map_location, weights_only=True)
    if not isinstance(payload, dict):
        raise ValueError("MobileNetV2 checkpoint payload must be a dictionary.")
    if payload.get("format") != _CHECKPOINT_FORMAT:
        raise ValueError("Unsupported MobileNetV2 checkpoint format.")
    if payload.get("format_version") != _CHECKPOINT_VERSION:
        raise ValueError("Unsupported MobileNetV2 checkpoint version.")
    config_payload = payload.get("config")
    if not isinstance(config_payload, Mapping):
        raise ValueError("Checkpoint is missing a valid config mapping.")
    state_dict = payload.get("state_dict")
    if not isinstance(state_dict, Mapping):
        raise ValueError("Checkpoint is missing a valid state_dict.")

    config = MobileNetV2Config.from_dict(config_payload)
    model = build_mobilenet_v2(config, weights_override=None)
    model.load_state_dict(state_dict, strict=True)
    training_state = payload.get("training_state", {})
    if not isinstance(training_state, Mapping):
        raise ValueError("Checkpoint has an invalid training_state mapping.")
    count = training_state.get("backbone_trainable_blocks", 0)
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("Checkpoint has an invalid backbone block count.")
    if count == 0:
        model.freeze_backbone()
    else:
        model.unfreeze_backbone(last_n_blocks=count)
    saved_metadata = payload.get("model_metadata")
    if isinstance(saved_metadata, Mapping):
        model.metadata = dict(saved_metadata)
    extra_metadata = payload.get("extra_metadata", {})
    if not isinstance(extra_metadata, Mapping):
        raise ValueError("Checkpoint has an invalid extra_metadata mapping.")
    assert_spoof_logit_contract(model)
    return model, dict(extra_metadata)


__all__ = [
    "MobileNetV2Config",
    "assert_spoof_logit_contract",
    "build_mobilenet_v2",
    "load_mobilenet_v2_checkpoint",
    "save_mobilenet_v2_checkpoint",
    "spoof_probability",
]
