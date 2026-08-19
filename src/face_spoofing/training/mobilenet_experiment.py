"""E02 MobileNetV2 training with dev-only selection and frozen test use."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import time
from typing import Any, Iterable, Sequence

import numpy as np

from face_spoofing.evaluation import (
    evaluate_oulu_attack_types,
    evaluate_scores,
    mean_aggregate,
    predict_labels,
    select_oulu_eer_threshold,
    select_threshold,
)
from face_spoofing.models.mobilenet_v2 import (
    MobileNetV2Config,
    assert_spoof_logit_contract,
    build_mobilenet_v2,
    load_mobilenet_v2_checkpoint,
    save_mobilenet_v2_checkpoint,
)

from .artifacts import (
    atomic_write_csv,
    atomic_write_json,
    config_hash,
    create_run_directory,
    environment_metadata,
    finalize_run_manifest,
    sha256_file,
    write_source_tree_snapshot,
)


EXPERIMENT_ID = "E02"
MODEL_NAME = "mobilenet_v2"


@dataclass(frozen=True, slots=True)
class CnnTrainingConfig:
    """Locked main-run training and early-stopping policy for E02."""

    batch_size: int = 16
    num_workers: int = 4
    max_epochs: int = 15
    minimum_epochs: int = 3
    early_stopping_patience: int = 3
    learning_rate: float = 1e-4
    backbone_learning_rate: float | None = None
    weight_decay: float = 1e-4
    seed: int = 42
    deterministic: bool = True
    use_amp: bool = False
    device: str = "auto"
    smoke: bool = False
    smoke_videos_per_label: int = 2

    def validate(self) -> None:
        integer_fields = (
            "batch_size",
            "num_workers",
            "max_epochs",
            "minimum_epochs",
            "early_stopping_patience",
            "seed",
            "smoke_videos_per_label",
        )
        for name in integer_fields:
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.num_workers < 0:
            raise ValueError("num_workers must be non-negative")
        if self.max_epochs <= 0:
            raise ValueError("max_epochs must be positive")
        if not 1 <= self.minimum_epochs <= self.max_epochs:
            raise ValueError("minimum_epochs must be between 1 and max_epochs")
        if self.early_stopping_patience <= 0:
            raise ValueError("early_stopping_patience must be positive")
        if self.seed < 0 or self.seed >= (1 << 63):
            raise ValueError("seed must be between 0 and 2**63 - 1")
        if self.smoke_videos_per_label <= 0:
            raise ValueError("smoke_videos_per_label must be positive")
        for name in ("learning_rate", "weight_decay"):
            value = getattr(self, name)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or float(value) < 0.0
            ):
                raise ValueError(f"{name} must be finite and non-negative")
        if self.learning_rate <= 0.0:
            raise ValueError("learning_rate must be positive")
        if self.backbone_learning_rate is not None:
            value = self.backbone_learning_rate
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or float(value) <= 0.0
            ):
                raise ValueError(
                    "backbone_learning_rate must be finite and positive"
                )
        if not isinstance(self.deterministic, bool):
            raise TypeError("deterministic must be a boolean")
        if not isinstance(self.use_amp, bool):
            raise TypeError("use_amp must be a boolean")
        if self.use_amp:
            raise ValueError("E02 main run keeps AMP disabled for reproducibility")
        if not isinstance(self.smoke, bool):
            raise TypeError("smoke must be a boolean")
        if self.device not in {"auto", "cpu", "cuda"}:
            raise ValueError("device must be one of: auto, cpu, cuda")

    def to_dict(self) -> dict[str, object]:
        self.validate()
        return asdict(self)


def _seed_everything(seed: int, deterministic: bool):
    cublas_config = os.environ.get("CUBLAS_WORKSPACE_CONFIG")
    if deterministic and cublas_config not in {None, ":4096:8", ":16:8"}:
        raise RuntimeError(
            "deterministic CUDA requires CUBLAS_WORKSPACE_CONFIG to be "
            "':4096:8' or ':16:8'"
        )
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    random.seed(seed)
    np.random.seed(seed % (2**32))
    import torch

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = deterministic
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.use_deterministic_algorithms(deterministic)
    return torch


def _resolve_device(torch, requested: str):
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if requested == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but no CUDA device is available")
    return torch.device(requested)


def _seed_worker(worker_id: int) -> None:
    import torch

    worker_seed = torch.initial_seed() % (2**32)
    random.seed(worker_seed)
    np.random.seed(worker_seed)


def _selection_key(metrics: dict[str, float], epoch: int) -> tuple[float, ...]:
    return (
        float(metrics["acer"]),
        float(metrics["apcer"]),
        -float(metrics["f1"]),
        float(epoch),
    )


def _balanced_subset_indices(
    records: Sequence[object], videos_per_label: int
) -> list[int]:
    selected: dict[int, list[str]] = {0: [], 1: []}
    selected_sets: dict[int, set[str]] = {0: set(), 1: set()}
    for record in records:
        label = int(getattr(record, "label"))
        video_id = str(getattr(record, "video_id"))
        if (
            len(selected[label]) < videos_per_label
            and video_id not in selected_sets[label]
        ):
            selected[label].append(video_id)
            selected_sets[label].add(video_id)
    if any(len(values) != videos_per_label for values in selected.values()):
        raise ValueError("split has too few videos for the balanced smoke subset")
    allowed = selected_sets[0] | selected_sets[1]
    return [
        index
        for index, record in enumerate(records)
        if str(getattr(record, "video_id")) in allowed
    ]


def _make_loader(
    dataset,
    *,
    batch_size: int,
    num_workers: int,
    shuffle: bool,
    seed: int,
    pin_memory: bool,
):
    import torch
    from face_spoofing.data.cnn_dataset import make_dataloader_generator

    options: dict[str, object] = {
        "dataset": dataset,
        "batch_size": batch_size,
        "shuffle": shuffle,
        "num_workers": num_workers,
        "pin_memory": pin_memory,
        "drop_last": False,
        "persistent_workers": False,
        "generator": make_dataloader_generator(seed),
        "worker_init_fn": _seed_worker,
    }
    if num_workers > 0:
        options["prefetch_factor"] = 2
    return torch.utils.data.DataLoader(**options)


def _train_one_epoch(
    model,
    loader,
    criterion,
    optimizer,
    device,
) -> dict[str, float | int]:
    import torch

    model.train()
    loss_sum = 0.0
    correct = 0
    samples = 0
    started = time.perf_counter()
    for batch in loader:
        images = batch["image"].to(device, non_blocking=True)
        labels = batch["label"].to(device, non_blocking=True)
        targets = labels.to(dtype=torch.float32).unsqueeze(1)
        optimizer.zero_grad(set_to_none=True)
        logits = model(images)
        loss = criterion(logits, targets)
        if not torch.isfinite(loss):
            raise RuntimeError("training loss became non-finite")
        loss.backward()
        optimizer.step()
        batch_size = int(labels.numel())
        loss_sum += float(loss.detach().item()) * batch_size
        predicted = (logits.detach().squeeze(1) >= 0.0).to(labels.dtype)
        correct += int((predicted == labels).sum().item())
        samples += batch_size
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    return {
        "loss": loss_sum / samples,
        "accuracy_at_0_5": correct / samples,
        "samples": samples,
        "seconds": time.perf_counter() - started,
    }


def _predict_loader(model, loader, criterion, device) -> dict[str, object]:
    import torch

    model.eval()
    frame_ids: list[str] = []
    video_ids: list[str] = []
    labels: list[int] = []
    logits_output: list[float] = []
    probabilities: list[float] = []
    loss_sum = 0.0
    samples = 0
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    started = time.perf_counter()
    with torch.inference_mode():
        for batch in loader:
            images = batch["image"].to(device, non_blocking=True)
            batch_labels = batch["label"].to(device, non_blocking=True)
            logits = model(images).squeeze(1)
            targets = batch_labels.to(dtype=torch.float32)
            loss = criterion(logits, targets)
            probability = torch.sigmoid(logits)
            if not torch.isfinite(logits).all() or not torch.isfinite(loss):
                raise RuntimeError("development/test inference became non-finite")
            count = int(batch_labels.numel())
            loss_sum += float(loss.item()) * count
            samples += count
            frame_ids.extend(str(value) for value in batch["frame_id"])
            video_ids.extend(str(value) for value in batch["video_id"])
            labels.extend(int(value) for value in batch_labels.cpu().tolist())
            logits_output.extend(float(value) for value in logits.cpu().tolist())
            probabilities.extend(
                float(value) for value in probability.cpu().tolist()
            )
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    return {
        "frame_ids": frame_ids,
        "video_ids": video_ids,
        "labels": labels,
        "logits": logits_output,
        "probabilities": probabilities,
        "loss": loss_sum / samples,
        "samples": samples,
        "seconds": time.perf_counter() - started,
    }


def _aggregate_prediction(prediction: dict[str, object]) -> dict[str, object]:
    values = mean_aggregate(
        prediction["video_ids"],
        prediction["probabilities"],
        prediction["labels"],
    )
    return {
        "video_ids": [str(value.video_id) for value in values],
        "scores": [float(value.score) for value in values],
        "labels": [int(value.label) for value in values],
        "frame_counts": [int(value.num_frames) for value in values],
    }


def _load_frame_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("frame manifest has no header")
        rows = list(reader)
    if not rows:
        raise ValueError("frame manifest is empty")
    frame_ids = [row["frame_id"] for row in rows]
    if len(frame_ids) != len(set(frame_ids)):
        raise ValueError("frame manifest contains duplicate frame_id values")
    return rows


def _attack_metadata(video_id: str) -> tuple[str, str]:
    try:
        access_id = int(video_id.rsplit("_", 1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"invalid OULU-NPU video_id: {video_id!r}") from exc
    mapping = {
        1: ("live", "none"),
        2: ("print", "printer_1"),
        3: ("print", "printer_2"),
        4: ("replay", "display_1"),
        5: ("replay", "display_2"),
    }
    try:
        return mapping[access_id]
    except KeyError as exc:
        raise ValueError(f"invalid access id in {video_id!r}") from exc


def _attack_error_breakdown(
    video_ids: Sequence[str],
    labels: Sequence[int],
    scores: Sequence[float],
    threshold: float,
) -> dict[str, dict[str, float | int]]:
    predicted = predict_labels(scores, threshold)
    groups: dict[str, list[int]] = defaultdict(list)
    for index, (video_id, label) in enumerate(zip(video_ids, labels)):
        if int(label) != 1:
            continue
        attack_type, instrument = _attack_metadata(str(video_id))
        groups[f"type/{attack_type}"].append(index)
        groups[f"instrument/{instrument}"].append(index)
    result: dict[str, dict[str, float | int]] = {}
    for name, indices in sorted(groups.items()):
        accepted = sum(int(predicted[index]) == 0 for index in indices)
        result[name] = {
            "attacks": len(indices),
            "accepted_as_live": accepted,
            "apcer": accepted / len(indices),
        }
    return result


def _evaluate_split(
    *,
    split: str,
    frame_rows: list[dict[str, str]],
    prediction: dict[str, object],
    frame_threshold: float,
    video_threshold: float,
    official_threshold: float | None,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    frame_ids = [str(value) for value in prediction["frame_ids"]]
    video_ids = [str(value) for value in prediction["video_ids"]]
    labels = [int(value) for value in prediction["labels"]]
    logits = [float(value) for value in prediction["logits"]]
    probabilities = [float(value) for value in prediction["probabilities"]]
    frame_metrics = evaluate_scores(labels, probabilities, frame_threshold)
    frame_at_video_threshold = evaluate_scores(
        labels, probabilities, video_threshold
    )
    aggregated = _aggregate_prediction(prediction)
    video_metrics = evaluate_scores(
        aggregated["labels"], aggregated["scores"], video_threshold
    )

    score_by_frame = dict(zip(frame_ids, probabilities))
    logit_by_frame = dict(zip(frame_ids, logits))
    label_by_frame = dict(zip(frame_ids, labels))
    expected_by_video = Counter(row["video_id"] for row in frame_rows)
    frame_prediction_rows: list[dict[str, object]] = []
    for row in frame_rows:
        frame_id = row["frame_id"]
        score = score_by_frame.get(frame_id)
        if score is None:
            if row["face_detected"].strip().lower() not in {"false", "0"}:
                raise RuntimeError(f"valid frame {frame_id} has no prediction")
            frame_prediction_rows.append(
                {
                    "frame_id": frame_id,
                    "video_id": row["video_id"],
                    "sample_index": int(row["sample_index"]),
                    "frame_index": int(row["frame_index"]),
                    "split": split,
                    "label": int(row["label"]),
                    "face_path": row["face_path"],
                    "prediction_status": "excluded_no_face",
                    "exclusion_reason": row["detector_status"],
                    "spoof_logit": "",
                    "spoof_probability": "",
                    "frame_threshold": "",
                    "predicted_label": "",
                    "video_threshold": "",
                    "prediction_at_video_threshold": "",
                }
            )
            continue
        if label_by_frame[frame_id] != int(row["label"]):
            raise RuntimeError(f"label mismatch for frame {frame_id}")
        frame_prediction_rows.append(
            {
                "frame_id": frame_id,
                "video_id": row["video_id"],
                "sample_index": int(row["sample_index"]),
                "frame_index": int(row["frame_index"]),
                "split": split,
                "label": int(row["label"]),
                "face_path": row["face_path"],
                "prediction_status": "ok",
                "exclusion_reason": "",
                "spoof_logit": logit_by_frame[frame_id],
                "spoof_probability": score,
                "frame_threshold": frame_threshold,
                "predicted_label": int(score >= frame_threshold),
                "video_threshold": video_threshold,
                "prediction_at_video_threshold": int(score >= video_threshold),
            }
        )

    video_prediction_rows: list[dict[str, object]] = []
    for video_id, label, score, count in zip(
        aggregated["video_ids"],
        aggregated["labels"],
        aggregated["scores"],
        aggregated["frame_counts"],
    ):
        attack_type, instrument = _attack_metadata(str(video_id))
        expected = expected_by_video[str(video_id)]
        video_prediction_rows.append(
            {
                "video_id": video_id,
                "split": split,
                "label": label,
                "attack_type": attack_type,
                "attack_instrument": instrument,
                "spoof_probability": score,
                "threshold": video_threshold,
                "predicted_label": int(float(score) >= video_threshold),
                "num_frames_expected": expected,
                "num_frames_scored": count,
                "num_frames_missing": expected - int(count),
            }
        )

    counts = Counter(video_ids)
    metrics: dict[str, object] = {
        "split": split,
        "coverage": {
            "manifest_rows": len(frame_rows),
            "scored_frames": len(frame_ids),
            "excluded_frames": len(frame_rows) - len(frame_ids),
            "videos": len(counts),
            "min_scored_frames_per_video": min(counts.values()),
            "max_scored_frames_per_video": max(counts.values()),
        },
        "frame": {
            "threshold_policy": "dev_frame_min_acer",
            "metrics": frame_metrics,
            "attack_breakdown": _attack_error_breakdown(
                video_ids, labels, probabilities, frame_threshold
            ),
        },
        "frame_at_video_threshold": {
            "threshold_policy": "frozen_dev_video_min_acer",
            "metrics": frame_at_video_threshold,
            "attack_breakdown": _attack_error_breakdown(
                video_ids, labels, probabilities, video_threshold
            ),
        },
        "video": {
            "threshold_policy": "dev_video_min_acer",
            "metrics": video_metrics,
            "attack_breakdown": _attack_error_breakdown(
                aggregated["video_ids"],
                aggregated["labels"],
                aggregated["scores"],
                video_threshold,
            ),
        },
    }
    if official_threshold is not None:
        metrics["official_compatible_video"] = evaluate_oulu_attack_types(
            aggregated["video_ids"],
            aggregated["labels"],
            aggregated["scores"],
            official_threshold,
        )
    return metrics, frame_prediction_rows, video_prediction_rows


def _write_confusion_figure(
    metrics: dict[str, object], path: Path, *, title: str
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
    for axis, level in zip(axes, ("frame", "video")):
        values = metrics[level]["metrics"]
        matrix = np.array(
            [[values["tn"], values["fp"]], [values["fn"], values["tp"]]]
        )
        axis.imshow(matrix, cmap="Blues")
        for row in range(2):
            for column in range(2):
                axis.text(
                    column,
                    row,
                    str(int(matrix[row, column])),
                    ha="center",
                    va="center",
                )
        axis.set_xticks([0, 1], ["Live", "Spoof"])
        axis.set_yticks([0, 1], ["Live", "Spoof"])
        axis.set_xlabel("Predicted")
        axis.set_ylabel("Actual")
        axis.set_title(f"{level} | ACER={values['acer']:.4f}")
    figure.suptitle(title)
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _write_training_curve(history: list[dict[str, object]], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    epochs = [int(row["epoch"]) for row in history]
    figure, left = plt.subplots(figsize=(6.4, 3.8))
    left.plot(
        epochs,
        [row["train_loss"] for row in history],
        marker="o",
        label="train loss",
    )
    left.plot(
        epochs,
        [row["dev_loss"] for row in history],
        marker="o",
        label="dev loss",
    )
    left.set_xlabel("Epoch")
    left.set_ylabel("Weighted BCE loss")
    right = left.twinx()
    right.plot(
        epochs,
        [row["dev_video_acer"] for row in history],
        color="tab:red",
        marker="o",
        label="dev video ACER",
    )
    right.set_ylabel("ACER")
    handles_left, labels_left = left.get_legend_handles_labels()
    handles_right, labels_right = right.get_legend_handles_labels()
    left.legend(handles_left + handles_right, labels_left + labels_right)
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _mobilenet_weights_metadata() -> dict[str, object]:
    import torch
    from torchvision.models import MobileNet_V2_Weights

    weights = MobileNet_V2_Weights.IMAGENET1K_V2
    filename = Path(weights.url).name
    cache_path = Path(torch.hub.get_dir()) / "checkpoints" / filename
    return {
        "enum": "MobileNet_V2_Weights.IMAGENET1K_V2",
        "url": weights.url,
        "cache_path": cache_path.as_posix(),
        "cached": cache_path.is_file(),
        "bytes": cache_path.stat().st_size if cache_path.is_file() else None,
        "sha256": sha256_file(cache_path) if cache_path.is_file() else None,
    }


def _benchmark_model(model, sample, device) -> dict[str, float | int]:
    import torch

    warmup = 20 if device.type == "cuda" else 3
    iterations = 100 if device.type == "cuda" else 10
    model.eval()
    sample = sample.to(device)
    with torch.inference_mode():
        for _ in range(warmup):
            torch.sigmoid(model(sample))
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        started = time.perf_counter()
        for _ in range(iterations):
            torch.sigmoid(model(sample))
        if device.type == "cuda":
            torch.cuda.synchronize(device)
    seconds = time.perf_counter() - started
    return {
        "warmup_iterations": warmup,
        "timed_iterations": iterations,
        "batch_size": int(sample.shape[0]),
        "total_seconds": seconds,
        "seconds_per_frame": seconds / (iterations * int(sample.shape[0])),
    }


def _run_binary_cnn_experiment(
    *,
    frame_manifest: Path | str,
    run_root: Path | str,
    project_root: Path | str,
    experiment_id: str,
    model_name: str,
    display_name: str,
    model_cfg,
    train_cfg: CnnTrainingConfig,
    build_model,
    assert_model_contract,
    save_checkpoint,
    load_checkpoint,
    weights_metadata,
    configure_model_for_training=None,
    optimizer_factory=None,
    expected_trainable_backbone_blocks: int = 0,
    training_stage: str = "frozen_backbone",
    training_policy: dict[str, object] | None = None,
    run_id: str | None = None,
) -> dict[str, object]:
    """Shared binary-CNN train/dev selection and frozen-test implementation."""

    model_cfg.validate()
    train_cfg.validate()
    torch = _seed_everything(train_cfg.seed, train_cfg.deterministic)
    device = _resolve_device(torch, train_cfg.device)
    project = Path(project_root).resolve()
    manifest_path = Path(frame_manifest)
    if not manifest_path.is_absolute():
        manifest_path = project / manifest_path
    manifest_path = manifest_path.resolve()

    from face_spoofing.data.cnn_dataset import CnnFrameDataset, CnnTransformConfig

    transform_config = CnnTransformConfig(horizontal_flip_probability=0.5)
    train_dataset = CnnFrameDataset(
        manifest_path,
        "train",
        project_root=project,
        training=True,
        seed=train_cfg.seed,
        transform_config=transform_config,
    )
    dev_dataset = CnnFrameDataset(
        manifest_path,
        "dev",
        project_root=project,
        training=False,
        seed=train_cfg.seed,
        transform_config=transform_config,
    )
    if not train_cfg.smoke:
        expected = {
            "train": (12_000, 12_000, 0, 1_200, 2_400, 9_600),
            "dev": (8_999, 9_000, 1, 900, 1_800, 7_199),
        }
        for dataset, split in ((train_dataset, "train"), (dev_dataset, "dev")):
            actual = (
                len(dataset),
                dataset.coverage.split_rows,
                dataset.coverage.excluded_no_face_rows,
                dataset.coverage.unique_videos,
                dataset.coverage.live_frames,
                dataset.coverage.spoof_frames,
            )
            if actual != expected[split]:
                raise ValueError(
                    f"{experiment_id} {split} coverage mismatch: "
                    f"expected {expected[split]}, "
                    f"found {actual}"
                )

    resolved_config = {
        "experiment_id": experiment_id,
        "model": model_cfg.to_dict(),
        "training": train_cfg.to_dict(),
        "transform": asdict(transform_config),
        "data": {
            "frame_manifest": manifest_path.relative_to(project).as_posix(),
            "frame_manifest_sha256": sha256_file(manifest_path),
            "train": train_dataset.coverage_metadata,
            "dev": dev_dataset.coverage_metadata,
            "expected_test_valid_frames": 6_000,
            "expected_test_videos": 600,
        },
        "selection": {
            "model_split": "dev",
            "model_level": "video",
            "model_objective": ["acer", "apcer", "-f1", "epoch"],
            "threshold_objective": ["acer", "apcer", "threshold"],
            "refit_train_plus_dev": False,
            "test_used_for_selection": False,
        },
        "training_policy": dict(training_policy or {}),
        "score_contract": {
            "type": "sigmoid_probability",
            "higher_score_label": 1,
            "aggregation": "mean_probability",
        },
        "official_compatible_secondary": {
            "source_archive": "data/raw/oulu_npu/Baseline.tar",
            "source_archive_sha256": sha256_file(
                project / "data/raw/oulu_npu/Baseline.tar"
            ),
            "member": "Baseline/Tools/performances.m",
            "threshold": "dev_vlfeat_eer",
        },
    }
    resolved_hash = config_hash(resolved_config)
    run_dir = create_run_directory(
        run_root,
        experiment_id=experiment_id,
        model_name=model_name,
        seed=train_cfg.seed,
        resolved_config_hash=resolved_hash,
        run_id=run_id,
    )
    started_at = datetime.now(timezone.utc)
    total_started = time.perf_counter()
    atomic_write_json(run_dir / "config_resolved.json", resolved_config)
    environment = environment_metadata(project)
    atomic_write_json(run_dir / "environment.json", environment)
    source_snapshot = write_source_tree_snapshot(
        run_dir,
        project,
        expected_sha256=str(environment["source_tree_sha256"]),
    )
    atomic_write_json(run_dir / "source" / "metadata.json", source_snapshot)

    if train_cfg.smoke:
        from torch.utils.data import Subset

        train_indices = _balanced_subset_indices(
            train_dataset.records, train_cfg.smoke_videos_per_label
        )
        dev_indices = _balanced_subset_indices(
            dev_dataset.records, train_cfg.smoke_videos_per_label
        )
        training_view = Subset(train_dataset, train_indices)
        development_view = Subset(dev_dataset, dev_indices)
    else:
        train_indices = list(range(len(train_dataset)))
        dev_indices = list(range(len(dev_dataset)))
        training_view = train_dataset
        development_view = dev_dataset

    selected_train_records = [train_dataset.records[index] for index in train_indices]
    class_counts = Counter(record.label for record in selected_train_records)
    if set(class_counts) != {0, 1}:
        raise ValueError("training view must contain both live and spoof frames")
    positive_weight = class_counts[0] / class_counts[1]

    model = build_model(model_cfg).to(device)
    if configure_model_for_training is not None:
        configure_model_for_training(model)
    assert_model_contract(model)
    parameter_counts = model.parameter_counts()
    actual_trainable_blocks = int(model.backbone_trainable_blocks)
    if actual_trainable_blocks != expected_trainable_backbone_blocks:
        raise RuntimeError(
            f"{experiment_id} requires {expected_trainable_backbone_blocks} "
            "trainable backbone blocks, found "
            f"{actual_trainable_blocks}"
        )
    if optimizer_factory is None:
        optimizer = torch.optim.Adam(
            [
                parameter
                for parameter in model.parameters()
                if parameter.requires_grad
            ],
            lr=train_cfg.learning_rate,
            weight_decay=train_cfg.weight_decay,
        )
    else:
        optimizer = optimizer_factory(torch, model, train_cfg)
    criterion = torch.nn.BCEWithLogitsLoss(
        pos_weight=torch.tensor([positive_weight], device=device)
    )
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    history: list[dict[str, object]] = []
    best: dict[str, object] | None = None
    non_improving_epochs = 0
    training_started = time.perf_counter()
    history_path = run_dir / "selection" / "history.csv"
    for epoch in range(1, train_cfg.max_epochs + 1):
        train_dataset.set_epoch(epoch)
        train_loader = _make_loader(
            training_view,
            batch_size=train_cfg.batch_size,
            num_workers=train_cfg.num_workers,
            shuffle=True,
            seed=train_cfg.seed + epoch,
            pin_memory=device.type == "cuda",
        )
        dev_loader = _make_loader(
            development_view,
            batch_size=train_cfg.batch_size,
            num_workers=train_cfg.num_workers,
            shuffle=False,
            seed=train_cfg.seed,
            pin_memory=device.type == "cuda",
        )
        train_result = _train_one_epoch(
            model, train_loader, criterion, optimizer, device
        )
        dev_prediction = _predict_loader(model, dev_loader, criterion, device)
        aggregated = _aggregate_prediction(dev_prediction)
        dev_threshold = select_threshold(
            aggregated["labels"], aggregated["scores"]
        )
        key = _selection_key(dev_threshold, epoch)
        improved = best is None or key < best["key"]
        row = {
            "epoch": epoch,
            "stage": training_stage,
            "learning_rate": train_cfg.learning_rate,
            "backbone_learning_rate": train_cfg.backbone_learning_rate,
            "train_loss": train_result["loss"],
            "train_accuracy_at_0_5": train_result["accuracy_at_0_5"],
            "train_samples": train_result["samples"],
            "train_seconds": train_result["seconds"],
            "dev_loss": dev_prediction["loss"],
            "dev_frames": dev_prediction["samples"],
            "dev_inference_seconds": dev_prediction["seconds"],
            "dev_videos": len(aggregated["video_ids"]),
            "dev_video_threshold": dev_threshold["threshold"],
            "dev_video_accuracy": dev_threshold["accuracy"],
            "dev_video_precision": dev_threshold["precision"],
            "dev_video_recall": dev_threshold["recall"],
            "dev_video_f1": dev_threshold["f1"],
            "dev_video_apcer": dev_threshold["apcer"],
            "dev_video_bpcer": dev_threshold["bpcer"],
            "dev_video_acer": dev_threshold["acer"],
            "selected_so_far": improved,
        }
        history.append(row)
        atomic_write_csv(history_path, list(history[0]), history)
        save_checkpoint(
            run_dir / "model" / "last.pt",
            model,
            extra_metadata={
                "epoch": epoch,
                "training_config": train_cfg.to_dict(),
                "dev_video_threshold_metrics": dev_threshold,
            },
        )
        if improved:
            best = {
                "key": key,
                "epoch": epoch,
                "threshold": dev_threshold,
                "dev_prediction": dev_prediction,
            }
            non_improving_epochs = 0
            save_checkpoint(
                run_dir / "model" / "best.pt",
                model,
                extra_metadata={
                    "epoch": epoch,
                    "training_config": train_cfg.to_dict(),
                    "dev_video_threshold_metrics": dev_threshold,
                },
            )
            atomic_write_json(
                run_dir / "selection" / "best_epoch.json",
                {
                    "epoch": epoch,
                    "selection_key": list(key),
                    "dev_video_threshold_metrics": dev_threshold,
                },
            )
        else:
            non_improving_epochs += 1
        print(
            json.dumps(
                {
                    "epoch": epoch,
                    "train_loss": train_result["loss"],
                    "dev_loss": dev_prediction["loss"],
                    "dev_video_acer": dev_threshold["acer"],
                    "dev_video_f1": dev_threshold["f1"],
                    "best_epoch": best["epoch"],
                    "non_improving_epochs": non_improving_epochs,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        if (
            epoch >= train_cfg.minimum_epochs
            and non_improving_epochs >= train_cfg.early_stopping_patience
        ):
            break
    training_seconds = time.perf_counter() - training_started
    assert best is not None

    reloaded, checkpoint_metadata = load_checkpoint(
        run_dir / "model" / "best.pt", map_location=device
    )
    reloaded = reloaded.to(device)
    assert_model_contract(reloaded)
    reload_dev_loader = _make_loader(
        development_view,
        batch_size=train_cfg.batch_size,
        num_workers=train_cfg.num_workers,
        shuffle=False,
        seed=train_cfg.seed,
        pin_memory=device.type == "cuda",
    )
    reload_prediction = _predict_loader(
        reloaded, reload_dev_loader, criterion, device
    )
    if reload_prediction["frame_ids"] != best["dev_prediction"]["frame_ids"]:
        raise RuntimeError("checkpoint reload changed development frame order")
    maximum_reload_difference = float(
        np.max(
            np.abs(
                np.asarray(reload_prediction["probabilities"])
                - np.asarray(best["dev_prediction"]["probabilities"])
            )
        )
    )
    if maximum_reload_difference > 1e-7:
        raise RuntimeError(
            "checkpoint reload changed development probabilities by "
            f"{maximum_reload_difference}"
        )

    dev_aggregated = _aggregate_prediction(reload_prediction)
    frame_threshold_result = select_threshold(
        reload_prediction["labels"], reload_prediction["probabilities"]
    )
    video_threshold_result = select_threshold(
        dev_aggregated["labels"], dev_aggregated["scores"]
    )
    frame_threshold = float(frame_threshold_result["threshold"])
    video_threshold = float(video_threshold_result["threshold"])
    official_selection = None
    official_threshold = None
    if not train_cfg.smoke:
        official_selection = select_oulu_eer_threshold(
            dev_aggregated["labels"], dev_aggregated["scores"]
        )
        official_threshold = float(official_selection["threshold"])

    threshold_payload = {
        "selection_split": "dev",
        "score_contract": {
            "type": "sigmoid_probability",
            "higher_score_label": 1,
            "decision_rule": "score >= threshold => spoof",
            "video_aggregation": "mean_probability",
        },
        "frame": {
            "threshold": frame_threshold,
            "objective": ["acer", "apcer", "threshold"],
            "dev_metrics": frame_threshold_result,
        },
        "video": {
            "threshold": video_threshold,
            "objective": ["acer", "apcer", "threshold"],
            "dev_metrics": video_threshold_result,
        },
        "official_compatible_secondary": official_selection,
    }
    atomic_write_json(run_dir / "threshold.json", threshold_payload)
    frozen_marker = {
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "selected_epoch": int(best["epoch"]),
        "checkpoint": "model/best.pt",
        "checkpoint_sha256": sha256_file(run_dir / "model" / "best.pt"),
        "frame_threshold": frame_threshold,
        "video_threshold": video_threshold,
        "official_compatible_video_threshold": official_threshold,
        "test_dataset_constructed": False,
        "test_used_for_selection": False,
    }
    atomic_write_json(run_dir / "selection" / "frozen.json", frozen_marker)

    manifest_rows = _load_frame_manifest(manifest_path)
    if train_cfg.smoke:
        allowed_dev_videos = {
            dev_dataset.records[index].video_id for index in dev_indices
        }
        dev_frame_rows = [
            row
            for row in manifest_rows
            if row["split"] == "dev" and row["video_id"] in allowed_dev_videos
        ]
    else:
        dev_frame_rows = [row for row in manifest_rows if row["split"] == "dev"]
    dev_metrics, dev_frame_predictions, dev_video_predictions = _evaluate_split(
        split="dev",
        frame_rows=dev_frame_rows,
        prediction=reload_prediction,
        frame_threshold=frame_threshold,
        video_threshold=video_threshold,
        official_threshold=official_threshold,
    )
    atomic_write_json(run_dir / "metrics" / "dev.json", dev_metrics)
    atomic_write_csv(
        run_dir / "predictions" / "dev_frames.csv",
        list(dev_frame_predictions[0]),
        dev_frame_predictions,
    )
    atomic_write_csv(
        run_dir / "predictions" / "dev_videos.csv",
        list(dev_video_predictions[0]),
        dev_video_predictions,
    )
    _write_confusion_figure(
        dev_metrics,
        run_dir / "figures" / "dev_confusion.png",
        title=f"{experiment_id} {display_name} — Development",
    )
    _write_training_curve(history, run_dir / "figures" / "training_curve.png")

    test_metrics = None
    test_prediction = None
    test_frame_predictions = None
    test_video_predictions = None
    if not train_cfg.smoke:
        # This is the first construction of a test Dataset and occurs only
        # after the checkpoint hashes and all dev thresholds are frozen above.
        test_dataset = CnnFrameDataset(
            manifest_path,
            "test",
            project_root=project,
            training=False,
            seed=train_cfg.seed,
            transform_config=transform_config,
        )
        test_coverage = (
            len(test_dataset),
            test_dataset.coverage.split_rows,
            test_dataset.coverage.excluded_no_face_rows,
            test_dataset.coverage.unique_videos,
            test_dataset.coverage.live_frames,
            test_dataset.coverage.spoof_frames,
        )
        if test_coverage != (6_000, 6_000, 0, 600, 1_200, 4_800):
            raise ValueError(
                "E02 test coverage must be 6000 valid rows, 600 videos, "
                "1200 live frames and 4800 spoof frames; found "
                f"{test_coverage}"
            )
        test_loader = _make_loader(
            test_dataset,
            batch_size=train_cfg.batch_size,
            num_workers=train_cfg.num_workers,
            shuffle=False,
            seed=train_cfg.seed,
            pin_memory=device.type == "cuda",
        )
        test_prediction = _predict_loader(reloaded, test_loader, criterion, device)
        atomic_write_json(
            run_dir / "selection" / "test_evaluation.json",
            {
                "started_after_frozen_marker": True,
                "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
                "checkpoint_sha256": frozen_marker["checkpoint_sha256"],
                "frame_threshold": frame_threshold,
                "video_threshold": video_threshold,
                "official_compatible_video_threshold": official_threshold,
                "test_used_for_selection": False,
            },
        )
        test_frame_rows = [
            row for row in manifest_rows if row["split"] == "test"
        ]
        (
            test_metrics,
            test_frame_predictions,
            test_video_predictions,
        ) = _evaluate_split(
            split="test",
            frame_rows=test_frame_rows,
            prediction=test_prediction,
            frame_threshold=frame_threshold,
            video_threshold=video_threshold,
            official_threshold=official_threshold,
        )
        atomic_write_json(run_dir / "metrics" / "test.json", test_metrics)
        atomic_write_csv(
            run_dir / "predictions" / "test_frames.csv",
            list(test_frame_predictions[0]),
            test_frame_predictions,
        )
        atomic_write_csv(
            run_dir / "predictions" / "test_videos.csv",
            list(test_video_predictions[0]),
            test_video_predictions,
        )
        _write_confusion_figure(
            test_metrics,
            run_dir / "figures" / "test_confusion.png",
            title=f"{experiment_id} {display_name} — Test",
        )

    summary_metrics = {"dev": dev_metrics, "test": test_metrics}
    atomic_write_json(run_dir / "metrics" / "summary.json", summary_metrics)
    sample = dev_dataset[dev_indices[0]]["image"].unsqueeze(0)
    pure_model_latency = _benchmark_model(reloaded, sample, device)
    checkpoint_path = run_dir / "model" / "best.pt"
    weights = weights_metadata()
    model_metadata = {
        "experiment_id": experiment_id,
        "model": model_name,
        "selected_epoch": int(best["epoch"]),
        "checkpoint_metadata": checkpoint_metadata,
        "checkpoint_bytes": checkpoint_path.stat().st_size,
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "parameter_counts": parameter_counts,
        "training_policy": dict(training_policy or {}),
        "weights": weights,
        "positive_weight": positive_weight,
        "class_counts": dict(sorted(class_counts.items())),
        "reload_probability_atol": 1e-7,
        "reload_max_absolute_difference": maximum_reload_difference,
    }
    atomic_write_json(run_dir / "model" / "metadata.json", model_metadata)
    completed_at = datetime.now(timezone.utc)
    timing = {
        "started_at_utc": started_at.isoformat(),
        "completed_at_utc": completed_at.isoformat(),
        "epochs_completed": len(history),
        "training_seconds": training_seconds,
        "final_dev_end_to_end_seconds": reload_prediction["seconds"],
        "final_dev_seconds_per_frame": reload_prediction["seconds"]
        / reload_prediction["samples"],
        "test_end_to_end_seconds": (
            None if test_prediction is None else test_prediction["seconds"]
        ),
        "test_seconds_per_frame": (
            None
            if test_prediction is None
            else test_prediction["seconds"] / test_prediction["samples"]
        ),
        "pure_model_latency": pure_model_latency,
        "peak_gpu_memory_bytes": (
            torch.cuda.max_memory_allocated(device)
            if device.type == "cuda"
            else None
        ),
        "total_seconds": time.perf_counter() - total_started,
    }
    atomic_write_json(run_dir / "timing.json", timing)
    result = {
        "ok": True,
        "status": "smoke_complete" if train_cfg.smoke else "complete",
        "experiment_id": experiment_id,
        "run_dir": run_dir.as_posix(),
        "device": str(device),
        "selected_epoch": int(best["epoch"]),
        "thresholds": {
            "frame": frame_threshold,
            "video": video_threshold,
            "official_compatible_video": official_threshold,
        },
        "dev": {
            "frame": dev_metrics["frame"]["metrics"],
            "video": dev_metrics["video"]["metrics"],
        },
        "test": (
            None
            if test_metrics is None
            else {
                "frame": test_metrics["frame"]["metrics"],
                "video": test_metrics["video"]["metrics"],
            }
        ),
        "timing": timing,
    }
    atomic_write_json(run_dir / "result.json", result)
    finalize_run_manifest(run_dir, status=str(result["status"]))
    return result


def run_mobilenet_v2_experiment(
    *,
    frame_manifest: Path | str,
    run_root: Path | str,
    project_root: Path | str,
    model_config: MobileNetV2Config | None = None,
    training_config: CnnTrainingConfig | None = None,
    run_id: str | None = None,
) -> dict[str, object]:
    """Run the locked E02 MobileNetV2 experiment."""

    model_cfg = model_config or MobileNetV2Config()
    train_cfg = training_config or CnnTrainingConfig()
    if model_cfg.weights != "IMAGENET1K_V2":
        raise ValueError(
            "E02 experiment requires pretrained IMAGENET1K_V2 weights; "
            "weights=None is reserved for isolated model tests/checkpoint restore"
        )
    return _run_binary_cnn_experiment(
        frame_manifest=frame_manifest,
        run_root=run_root,
        project_root=project_root,
        experiment_id=EXPERIMENT_ID,
        model_name=MODEL_NAME,
        display_name="MobileNetV2",
        model_cfg=model_cfg,
        train_cfg=train_cfg,
        build_model=build_mobilenet_v2,
        assert_model_contract=assert_spoof_logit_contract,
        save_checkpoint=save_mobilenet_v2_checkpoint,
        load_checkpoint=load_mobilenet_v2_checkpoint,
        weights_metadata=_mobilenet_weights_metadata,
        run_id=run_id,
    )


# Backward-compatible name used by the E02 CLI and existing tests.
MobileNetTrainingConfig = CnnTrainingConfig


__all__ = [
    "CnnTrainingConfig",
    "MobileNetTrainingConfig",
    "run_mobilenet_v2_experiment",
]
