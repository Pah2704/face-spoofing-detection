"""E03/E04 ResNet18 adapters for the shared frozen-test CNN runner."""

from __future__ import annotations

from pathlib import Path

from face_spoofing.models.resnet18 import (
    ResNet18Config,
    assert_spoof_logit_contract,
    build_resnet18,
    load_resnet18_checkpoint,
    save_resnet18_checkpoint,
)

from .artifacts import sha256_file
from .mobilenet_experiment import CnnTrainingConfig, _run_binary_cnn_experiment


def _resnet_weights_metadata() -> dict[str, object]:
    import torch
    from torchvision.models import ResNet18_Weights

    weights = ResNet18_Weights.IMAGENET1K_V1
    filename = Path(weights.url).name
    cache_path = Path(torch.hub.get_dir()) / "checkpoints" / filename
    return {
        "enum": "ResNet18_Weights.IMAGENET1K_V1",
        "url": weights.url,
        "cache_path": cache_path.as_posix(),
        "cached": cache_path.is_file(),
        "bytes": cache_path.stat().st_size if cache_path.is_file() else None,
        "sha256": sha256_file(cache_path) if cache_path.is_file() else None,
    }


def run_resnet18_experiment(
    *,
    frame_manifest: Path | str,
    run_root: Path | str,
    project_root: Path | str,
    model_config: ResNet18Config | None = None,
    training_config: CnnTrainingConfig | None = None,
    run_id: str | None = None,
) -> dict[str, object]:
    model_cfg = model_config or ResNet18Config()
    train_cfg = training_config or CnnTrainingConfig()
    if model_cfg.experiment_id != "E03":
        raise ValueError("E03 runner requires model experiment_id='E03'")
    if train_cfg.backbone_learning_rate is not None:
        raise ValueError("E03 head-only run does not use a backbone learning rate")
    if model_cfg.weights != "IMAGENET1K_V1":
        raise ValueError(
            "E03 experiment requires pretrained IMAGENET1K_V1 weights; "
            "weights=None is reserved for isolated model tests/checkpoint restore"
        )
    return _run_binary_cnn_experiment(
        frame_manifest=frame_manifest,
        run_root=run_root,
        project_root=project_root,
        experiment_id="E03",
        model_name="resnet18",
        display_name="ResNet18",
        model_cfg=model_cfg,
        train_cfg=train_cfg,
        build_model=build_resnet18,
        assert_model_contract=assert_spoof_logit_contract,
        save_checkpoint=save_resnet18_checkpoint,
        load_checkpoint=load_resnet18_checkpoint,
        weights_metadata=_resnet_weights_metadata,
        run_id=run_id,
    )


def _configure_layer4_finetune(model) -> None:
    """Open exactly ResNet layer4 while keeping earlier stages frozen."""

    model.unfreeze_backbone(last_n_blocks=1)
    model.metadata["fine_tuning_policy"] = {
        "trainable_backbone_stage": "layer4",
        "trainable_backbone_blocks": 1,
        "earlier_backbone_stages_frozen": True,
        "layer4_batch_norm_trainable": True,
        "classifier_trainable": True,
    }


def _build_layer4_optimizer(torch, model, train_cfg: CnnTrainingConfig):
    if train_cfg.backbone_learning_rate is None:
        raise ValueError("E04 requires backbone_learning_rate")
    backbone_parameters = [
        parameter
        for parameter in model.network.layer4.parameters()
        if parameter.requires_grad
    ]
    classifier_parameters = [
        parameter
        for parameter in model.classifier.parameters()
        if parameter.requires_grad
    ]
    grouped_ids = {
        id(parameter)
        for parameter in (*backbone_parameters, *classifier_parameters)
    }
    trainable_ids = {
        id(parameter) for parameter in model.parameters() if parameter.requires_grad
    }
    if not backbone_parameters or not classifier_parameters:
        raise RuntimeError("E04 optimizer groups must both be non-empty")
    if grouped_ids != trainable_ids:
        raise RuntimeError(
            "E04 optimizer groups do not exactly cover trainable parameters"
        )
    return torch.optim.Adam(
        [
            {
                "name": "resnet_layer4",
                "params": backbone_parameters,
                "lr": train_cfg.backbone_learning_rate,
            },
            {
                "name": "classifier_head",
                "params": classifier_parameters,
                "lr": train_cfg.learning_rate,
            },
        ],
        weight_decay=train_cfg.weight_decay,
    )


def run_resnet18_finetune_experiment(
    *,
    frame_manifest: Path | str,
    run_root: Path | str,
    project_root: Path | str,
    model_config: ResNet18Config | None = None,
    training_config: CnnTrainingConfig | None = None,
    run_id: str | None = None,
) -> dict[str, object]:
    """Run the pre-registered E04 layer4 fine-tuning ablation."""

    model_cfg = model_config or ResNet18Config(experiment_id="E04")
    train_cfg = training_config or CnnTrainingConfig(
        backbone_learning_rate=1e-5
    )
    if model_cfg.experiment_id != "E04":
        raise ValueError("E04 runner requires model experiment_id='E04'")
    if model_cfg.weights != "IMAGENET1K_V1":
        raise ValueError("E04 requires pretrained IMAGENET1K_V1 weights")
    locked_values = {
        "learning_rate": (train_cfg.learning_rate, 1e-4),
        "backbone_learning_rate": (train_cfg.backbone_learning_rate, 1e-5),
        "weight_decay": (train_cfg.weight_decay, 1e-4),
        "seed": (train_cfg.seed, 42),
    }
    mismatches = [
        f"{name}={actual!r} (expected {expected!r})"
        for name, (actual, expected) in locked_values.items()
        if actual != expected
    ]
    if mismatches:
        raise ValueError("E04 locked config mismatch: " + ", ".join(mismatches))

    policy = {
        "initialization": "ResNet18_Weights.IMAGENET1K_V1",
        "trainable_backbone_stage": "layer4",
        "trainable_backbone_blocks": 1,
        "earlier_stages": "frozen",
        "batch_norm": "layer4_trainable_earlier_frozen",
        "classifier": "trainable_one_spoof_logit",
        "optimizer": "Adam",
        "head_learning_rate": train_cfg.learning_rate,
        "backbone_learning_rate": train_cfg.backbone_learning_rate,
        "weight_decay": train_cfg.weight_decay,
    }
    return _run_binary_cnn_experiment(
        frame_manifest=frame_manifest,
        run_root=run_root,
        project_root=project_root,
        experiment_id="E04",
        model_name="resnet18_finetune_layer4",
        display_name="ResNet18 fine-tune layer4",
        model_cfg=model_cfg,
        train_cfg=train_cfg,
        build_model=build_resnet18,
        assert_model_contract=assert_spoof_logit_contract,
        save_checkpoint=save_resnet18_checkpoint,
        load_checkpoint=load_resnet18_checkpoint,
        weights_metadata=_resnet_weights_metadata,
        configure_model_for_training=_configure_layer4_finetune,
        optimizer_factory=_build_layer4_optimizer,
        expected_trainable_backbone_blocks=1,
        training_stage="fine_tune_layer4",
        training_policy=policy,
        run_id=run_id,
    )


__all__ = ["run_resnet18_experiment", "run_resnet18_finetune_experiment"]
