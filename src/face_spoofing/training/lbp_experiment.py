"""LBP-SVM development selection and frozen test evaluation for E01/E05."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import math
from pathlib import Path
import time
import warnings

import numpy as np

from face_spoofing.evaluation import (
    evaluate_scores,
    mean_aggregate,
    predict_labels,
    select_threshold,
)
from face_spoofing.models.lbp_svm import (
    LBPSVMConfig,
    assert_spoof_positive_estimator,
    build_lbp_svm,
)
from .artifacts import (
    atomic_joblib_dump,
    atomic_write_csv,
    atomic_write_json,
    config_hash,
    create_run_directory,
    environment_metadata,
    finalize_run_manifest,
    sha256_file,
)


EXPERIMENT_ID = "E01"
MODEL_NAME = "lbp_svm"
RGB_EXPERIMENT_ID = "E05"
RGB_MODEL_NAME = "rgb_lbp_svm"


def _load_frame_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Frame manifest is empty: {path}.")
    frame_ids = [row["frame_id"] for row in rows]
    if len(frame_ids) != len(set(frame_ids)):
        raise ValueError("Frame manifest contains duplicate frame_id values.")
    return rows


def _attack_metadata(video_id: str) -> tuple[str, str]:
    access_id = int(video_id.rsplit("_", 1)[1])
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
        raise ValueError(f"Invalid OULU-NPU access id in {video_id}.") from exc


def _aggregate(
    video_ids: np.ndarray,
    scores: np.ndarray,
    labels: np.ndarray,
):
    predictions = mean_aggregate(
        video_ids.tolist(), scores.tolist(), labels.tolist()
    )
    ids = np.asarray([str(item.video_id) for item in predictions])
    aggregated_scores = np.asarray(
        [item.score for item in predictions], dtype=np.float64
    )
    aggregated_labels = np.asarray(
        [int(item.label) for item in predictions], dtype=np.int8
    )
    counts = np.asarray(
        [item.num_frames for item in predictions], dtype=np.int16
    )
    return ids, aggregated_scores, aggregated_labels, counts


def _selection_key(result: dict[str, float], c_value: float):
    return (
        float(result["acer"]),
        float(result["apcer"]),
        -float(result["f1"]),
        float(c_value),
    )


def _coverage(
    split_rows: list[dict[str, str]],
    scored_video_ids: np.ndarray,
) -> dict[str, object]:
    valid_rows = [row for row in split_rows if row["face_detected"].lower() == "true"]
    counts = Counter(str(value) for value in scored_video_ids)
    return {
        "manifest_rows": len(split_rows),
        "scored_frames": len(valid_rows),
        "excluded_frames": len(split_rows) - len(valid_rows),
        "videos": len(counts),
        "min_scored_frames_per_video": min(counts.values()),
        "max_scored_frames_per_video": max(counts.values()),
    }


def _attack_error_breakdown(
    video_ids: np.ndarray,
    labels: np.ndarray,
    scores: np.ndarray,
    threshold: float,
) -> dict[str, dict[str, float | int]]:
    predicted = np.asarray(predict_labels(scores.tolist(), threshold))
    groups: dict[str, list[int]] = defaultdict(list)
    for index, (video_id, label) in enumerate(zip(video_ids, labels)):
        if int(label) != 1:
            continue
        attack_type, instrument = _attack_metadata(str(video_id))
        groups[f"type/{attack_type}"].append(index)
        groups[f"instrument/{instrument}"].append(index)

    result: dict[str, dict[str, float | int]] = {}
    for name, indices in sorted(groups.items()):
        accepted_as_live = sum(int(predicted[index]) == 0 for index in indices)
        result[name] = {
            "attacks": len(indices),
            "accepted_as_live": accepted_as_live,
            "apcer": accepted_as_live / len(indices),
        }
    return result


def _evaluate_split(
    *,
    split: str,
    frame_rows: list[dict[str, str]],
    frame_ids: np.ndarray,
    video_ids: np.ndarray,
    labels: np.ndarray,
    frame_scores: np.ndarray,
    frame_threshold: float,
    video_threshold: float,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    frame_metrics = evaluate_scores(
        labels.tolist(), frame_scores.tolist(), frame_threshold
    )
    frame_at_video_threshold = evaluate_scores(
        labels.tolist(), frame_scores.tolist(), video_threshold
    )
    (
        aggregated_ids,
        video_scores,
        video_labels,
        video_frame_counts,
    ) = _aggregate(video_ids, frame_scores, labels)
    video_metrics = evaluate_scores(
        video_labels.tolist(), video_scores.tolist(), video_threshold
    )

    score_by_frame = {
        str(frame_id): float(score)
        for frame_id, score in zip(frame_ids, frame_scores)
    }
    label_at_frame_threshold = {
        frame_id: int(score >= frame_threshold)
        for frame_id, score in score_by_frame.items()
    }
    label_at_video_threshold = {
        frame_id: int(score >= video_threshold)
        for frame_id, score in score_by_frame.items()
    }
    frame_prediction_rows: list[dict[str, object]] = []
    expected_by_video = Counter(row["video_id"] for row in frame_rows)
    for row in frame_rows:
        score = score_by_frame.get(row["frame_id"])
        if score is None:
            frame_prediction_rows.append(
                {
                    "frame_id": row["frame_id"],
                    "video_id": row["video_id"],
                    "sample_index": int(row["sample_index"]),
                    "frame_index": int(row["frame_index"]),
                    "split": split,
                    "label": int(row["label"]),
                    "face_path": row["face_path"],
                    "prediction_status": "excluded_no_face",
                    "exclusion_reason": row["detector_status"],
                    "spoof_score": "",
                    "frame_threshold": "",
                    "predicted_label": "",
                    "video_threshold": "",
                    "prediction_at_video_threshold": "",
                }
            )
            continue
        frame_prediction_rows.append(
            {
                "frame_id": row["frame_id"],
                "video_id": row["video_id"],
                "sample_index": int(row["sample_index"]),
                "frame_index": int(row["frame_index"]),
                "split": split,
                "label": int(row["label"]),
                "face_path": row["face_path"],
                "prediction_status": "ok",
                "exclusion_reason": "",
                "spoof_score": score,
                "frame_threshold": frame_threshold,
                "predicted_label": label_at_frame_threshold[row["frame_id"]],
                "video_threshold": video_threshold,
                "prediction_at_video_threshold": label_at_video_threshold[
                    row["frame_id"]
                ],
            }
        )

    video_prediction_rows: list[dict[str, object]] = []
    for video_id, label, score, count in zip(
        aggregated_ids, video_labels, video_scores, video_frame_counts
    ):
        attack_type, instrument = _attack_metadata(str(video_id))
        expected = expected_by_video[str(video_id)]
        video_prediction_rows.append(
            {
                "video_id": str(video_id),
                "split": split,
                "label": int(label),
                "attack_type": attack_type,
                "attack_instrument": instrument,
                "spoof_score": float(score),
                "threshold": video_threshold,
                "predicted_label": int(score >= video_threshold),
                "num_frames_expected": expected,
                "num_frames_scored": int(count),
                "num_frames_missing": expected - int(count),
            }
        )

    metrics = {
        "split": split,
        "coverage": _coverage(frame_rows, video_ids),
        "frame": {
            "threshold_policy": "dev_frame_min_acer",
            "metrics": frame_metrics,
            "attack_breakdown": _attack_error_breakdown(
                video_ids, labels, frame_scores, frame_threshold
            ),
        },
        "frame_at_video_threshold": {
            "threshold_policy": "frozen_dev_video_min_acer",
            "metrics": frame_at_video_threshold,
            "attack_breakdown": _attack_error_breakdown(
                video_ids, labels, frame_scores, video_threshold
            ),
        },
        "video": {
            "threshold_policy": "dev_video_min_acer",
            "metrics": video_metrics,
            "attack_breakdown": _attack_error_breakdown(
                aggregated_ids, video_labels, video_scores, video_threshold
            ),
        },
    }
    return metrics, frame_prediction_rows, video_prediction_rows


def _write_confusion_figure(
    metrics: dict[str, object],
    path: Path,
    *,
    title: str,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    levels = ("frame", "video")
    figure, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
    for axis, level in zip(axes, levels):
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
                    color="black",
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


def _run_lbp_svm_experiment(
    dataset,
    *,
    frame_manifest: Path | str,
    run_root: Path | str,
    project_root: Path | str,
    model_config: LBPSVMConfig | None = None,
    run_id: str | None = None,
    experiment_id: str,
    model_name: str,
    expected_color_mode: str,
) -> dict[str, object]:
    """Run dev-only selection, freeze the experiment, then evaluate test."""

    started_at = datetime.now(timezone.utc)
    overall_start = time.perf_counter()
    config = model_config or LBPSVMConfig()
    config.validate()
    manifest_path = Path(frame_manifest)
    project = Path(project_root).resolve()
    frame_rows = _load_frame_manifest(manifest_path)

    cache_config = dataset.metadata.get("config")
    if not isinstance(cache_config, dict):
        raise ValueError("LBP feature cache metadata has no config object.")
    color_mode = cache_config.get("color_mode")
    if color_mode != expected_color_mode:
        raise ValueError(
            f"{experiment_id} requires color_mode={expected_color_mode!r}, "
            f"found {color_mode!r}."
        )
    expected_feature_dim = 640 if expected_color_mode == "grayscale" else 1920
    if dataset.features.ndim != 2 or dataset.features.shape[1] != expected_feature_dim:
        raise ValueError(
            f"{experiment_id} requires {expected_feature_dim} LBP features, "
            f"found shape {dataset.features.shape}."
        )

    expected_counts = {"train": 12_000, "dev": 8_999, "test": 6_000}
    split_indices = {
        split: np.asarray(dataset.select_split(split), dtype=np.int64)
        for split in ("train", "dev")
    }
    for split, expected in (("train", 12_000), ("dev", 8_999)):
        actual = len(split_indices[split])
        if actual != expected:
            raise ValueError(
                f"{experiment_id} expected {expected} valid {split} features, "
                f"found {actual}."
            )

    resolved_config = {
        "experiment_id": experiment_id,
        "model": model_name,
        "model_config": config.to_dict(),
        "feature_cache": {
            "path": Path(dataset.cache_dir).as_posix(),
            "fingerprint": dataset.metadata.get(
                "fingerprint", Path(dataset.cache_dir).name
            ),
            "feature_dim": int(dataset.features.shape[1]),
            "metadata": dataset.metadata,
        },
        "frame_manifest": {
            "path": manifest_path.as_posix(),
            "sha256": sha256_file(manifest_path),
        },
        "labels": {"live": 0, "spoof": 1, "positive_class": "spoof"},
        "aggregation": "mean_decision_score",
        "selection": {
            "split": "dev",
            "primary_level": "video",
            "threshold_objective": ["acer", "apcer", "threshold"],
            "model_objective": ["acer", "apcer", "-f1", "C"],
        },
    }
    resolved_hash = config_hash(resolved_config)
    run_dir = create_run_directory(
        run_root,
        experiment_id=experiment_id,
        model_name=model_name,
        seed=config.seed,
        resolved_config_hash=resolved_hash,
        run_id=run_id,
    )
    atomic_write_json(run_dir / "config_resolved.json", resolved_config)
    atomic_write_json(
        run_dir / "environment.json", environment_metadata(project)
    )

    train_idx = split_indices["train"]
    dev_idx = split_indices["dev"]
    x_train = dataset.features[train_idx]
    y_train = dataset.labels[train_idx]
    x_dev = dataset.features[dev_idx]
    y_dev = dataset.labels[dev_idx]
    dev_video_ids = dataset.video_ids[dev_idx]
    if not np.isfinite(x_train).all() or not np.isfinite(x_dev).all():
        raise ValueError("LBP feature cache contains non-finite values.")

    from sklearn.exceptions import ConvergenceWarning

    tuning_rows: list[dict[str, object]] = []
    best = None
    selection_start = time.perf_counter()
    for c_value in config.c_values:
        estimator = build_lbp_svm(float(c_value), config)
        fit_start = time.perf_counter()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ConvergenceWarning)
            estimator.fit(x_train, y_train)
        fit_seconds = time.perf_counter() - fit_start
        convergence_messages = [
            str(item.message)
            for item in caught
            if issubclass(item.category, ConvergenceWarning)
        ]
        assert_spoof_positive_estimator(estimator)

        decision_start = time.perf_counter()
        dev_scores = np.asarray(
            estimator.decision_function(x_dev), dtype=np.float64
        )
        decision_seconds = time.perf_counter() - decision_start
        (
            dev_aggregated_ids,
            dev_video_scores,
            dev_video_labels,
            dev_frame_counts,
        ) = _aggregate(dev_video_ids, dev_scores, y_dev)
        if len(dev_aggregated_ids) != 900:
            raise ValueError(
                f"Development aggregation produced {len(dev_aggregated_ids)} "
                "videos, expected 900."
            )
        threshold_result = select_threshold(
            dev_video_labels.tolist(), dev_video_scores.tolist()
        )
        svm = estimator.named_steps["svm"]
        row = {
            "C": float(c_value),
            "fit_seconds": fit_seconds,
            "dev_decision_seconds": decision_seconds,
            "n_iter": int(np.max(np.asarray(svm.n_iter_))),
            "convergence_warning": " | ".join(convergence_messages),
            "dev_video_threshold": float(threshold_result["threshold"]),
            "dev_video_accuracy": float(threshold_result["accuracy"]),
            "dev_video_precision": float(threshold_result["precision"]),
            "dev_video_recall": float(threshold_result["recall"]),
            "dev_video_f1": float(threshold_result["f1"]),
            "dev_video_apcer": float(threshold_result["apcer"]),
            "dev_video_bpcer": float(threshold_result["bpcer"]),
            "dev_video_acer": float(threshold_result["acer"]),
            "selected": False,
        }
        tuning_rows.append(row)
        key = _selection_key(threshold_result, float(c_value))
        if best is None or key < best["key"]:
            best = {
                "key": key,
                "C": float(c_value),
                "estimator": estimator,
                "dev_scores": dev_scores,
                "dev_video_scores": dev_video_scores,
                "dev_video_labels": dev_video_labels,
                "dev_video_ids": dev_aggregated_ids,
                "dev_frame_counts": dev_frame_counts,
                "video_threshold_result": threshold_result,
                "fit_seconds": fit_seconds,
                "decision_seconds": decision_seconds,
            }

    assert best is not None
    for row in tuning_rows:
        row["selected"] = float(row["C"]) == best["C"]
    if any(row["convergence_warning"] for row in tuning_rows):
        raise RuntimeError("At least one C trial emitted a convergence warning.")
    selection_seconds = time.perf_counter() - selection_start

    best_estimator = best["estimator"]
    dev_scores = best["dev_scores"]
    video_threshold = float(best["video_threshold_result"]["threshold"])
    frame_threshold_result = select_threshold(y_dev.tolist(), dev_scores.tolist())
    frame_threshold = float(frame_threshold_result["threshold"])

    # Test features are first selected only after C and both dev thresholds freeze.
    test_idx = np.asarray(dataset.select_split("test"), dtype=np.int64)
    if len(test_idx) != expected_counts["test"]:
        raise ValueError(
            f"{experiment_id} expected 6000 valid test features, "
            f"found {len(test_idx)}."
        )
    x_test = dataset.features[test_idx]
    y_test = dataset.labels[test_idx]
    test_video_ids = dataset.video_ids[test_idx]
    test_frame_ids = dataset.frame_ids[test_idx]
    test_start = time.perf_counter()
    test_scores = np.asarray(
        best_estimator.decision_function(x_test), dtype=np.float64
    )
    test_decision_seconds = time.perf_counter() - test_start

    split_manifest_rows = {
        split: [row for row in frame_rows if row["split"] == split]
        for split in ("dev", "test")
    }
    dev_metrics, dev_frame_predictions, dev_video_predictions = _evaluate_split(
        split="dev",
        frame_rows=split_manifest_rows["dev"],
        frame_ids=dataset.frame_ids[dev_idx],
        video_ids=dev_video_ids,
        labels=y_dev,
        frame_scores=dev_scores,
        frame_threshold=frame_threshold,
        video_threshold=video_threshold,
    )
    test_metrics, test_frame_predictions, test_video_predictions = _evaluate_split(
        split="test",
        frame_rows=split_manifest_rows["test"],
        frame_ids=test_frame_ids,
        video_ids=test_video_ids,
        labels=y_test,
        frame_scores=test_scores,
        frame_threshold=frame_threshold,
        video_threshold=video_threshold,
    )

    model_path = run_dir / "model" / f"{model_name}.joblib"
    atomic_joblib_dump(model_path, best_estimator)
    import joblib

    reloaded = joblib.load(model_path)
    assert_spoof_positive_estimator(reloaded)
    reloaded_dev_scores = np.asarray(
        reloaded.decision_function(x_dev), dtype=np.float64
    )
    reloaded_test_scores = np.asarray(
        reloaded.decision_function(x_test), dtype=np.float64
    )
    if not np.allclose(reloaded_dev_scores, dev_scores, rtol=0.0, atol=1e-12):
        raise RuntimeError("Reloaded model changed development decision scores.")
    if not np.allclose(reloaded_test_scores, test_scores, rtol=0.0, atol=1e-12):
        raise RuntimeError("Reloaded model changed test decision scores.")
    if not np.array_equal(
        reloaded_test_scores >= frame_threshold,
        test_scores >= frame_threshold,
    ):
        raise RuntimeError("Reloaded model changed test predicted labels.")

    tuning_fields = list(tuning_rows[0])
    atomic_write_csv(
        run_dir / "selection" / "c_search.csv",
        tuning_fields,
        tuning_rows,
    )
    threshold_payload = {
        "selection_split": "dev",
        "score_contract": {
            "type": "LinearSVC.decision_function",
            "higher_score_label": 1,
            "decision_rule": "score >= threshold => spoof",
        },
        "video": {
            "threshold": video_threshold,
            "objective": ["acer", "apcer", "threshold"],
            "dev_metrics": best["video_threshold_result"],
        },
        "frame": {
            "threshold": frame_threshold,
            "objective": ["acer", "apcer", "threshold"],
            "dev_metrics": frame_threshold_result,
        },
    }
    atomic_write_json(run_dir / "threshold.json", threshold_payload)
    atomic_write_json(run_dir / "metrics" / "dev.json", dev_metrics)
    atomic_write_json(run_dir / "metrics" / "test.json", test_metrics)
    atomic_write_json(
        run_dir / "metrics" / "summary.json",
        {"dev": dev_metrics, "test": test_metrics},
    )

    frame_fields = list(dev_frame_predictions[0])
    video_fields = list(dev_video_predictions[0])
    atomic_write_csv(
        run_dir / "predictions" / "dev_frames.csv",
        frame_fields,
        dev_frame_predictions,
    )
    atomic_write_csv(
        run_dir / "predictions" / "dev_videos.csv",
        video_fields,
        dev_video_predictions,
    )
    atomic_write_csv(
        run_dir / "predictions" / "test_frames.csv",
        frame_fields,
        test_frame_predictions,
    )
    atomic_write_csv(
        run_dir / "predictions" / "test_videos.csv",
        video_fields,
        test_video_predictions,
    )

    svm = best_estimator.named_steps["svm"]
    scaler = best_estimator.named_steps.get("scaler")
    model_metadata = {
        "experiment_id": experiment_id,
        "model": model_name,
        "color_mode": expected_color_mode,
        "selected_C": best["C"],
        "classes": [int(value) for value in svm.classes_],
        "feature_dim": int(dataset.features.shape[1]),
        "coef_shape": list(svm.coef_.shape),
        "coef_nonzero": int(np.count_nonzero(svm.coef_)),
        "intercept": [float(value) for value in svm.intercept_],
        "scaler_fit_samples": int(scaler.n_samples_seen_) if scaler is not None else None,
        "model_bytes": model_path.stat().st_size,
        "model_sha256": sha256_file(model_path),
        "reload_score_atol": 1e-12,
    }
    atomic_write_json(run_dir / "model" / "metadata.json", model_metadata)

    completed_at = datetime.now(timezone.utc)
    timing = {
        "started_at_utc": started_at.isoformat(),
        "completed_at_utc": completed_at.isoformat(),
        "selection_seconds": selection_seconds,
        "selected_fit_seconds": best["fit_seconds"],
        "selected_dev_decision_seconds": best["decision_seconds"],
        "test_decision_seconds": test_decision_seconds,
        "test_decision_seconds_per_frame": test_decision_seconds / len(test_idx),
        "total_seconds": time.perf_counter() - overall_start,
    }
    atomic_write_json(run_dir / "timing.json", timing)
    _write_confusion_figure(
        dev_metrics,
        run_dir / "figures" / "dev_confusion.png",
        title=f"{experiment_id} {model_name} — Development",
    )
    _write_confusion_figure(
        test_metrics,
        run_dir / "figures" / "test_confusion.png",
        title=f"{experiment_id} {model_name} — Test",
    )

    result = {
        "ok": True,
        "experiment_id": experiment_id,
        "run_dir": run_dir.as_posix(),
        "selected_C": best["C"],
        "thresholds": {
            "frame": frame_threshold,
            "video": video_threshold,
        },
        "dev": {
            "frame": dev_metrics["frame"]["metrics"],
            "video": dev_metrics["video"]["metrics"],
        },
        "test": {
            "frame": test_metrics["frame"]["metrics"],
            "video": test_metrics["video"]["metrics"],
        },
        "timing": timing,
    }
    atomic_write_json(run_dir / "result.json", result)
    finalize_run_manifest(run_dir, status="complete")
    return result


def run_lbp_svm_experiment(
    dataset,
    *,
    frame_manifest: Path | str,
    run_root: Path | str,
    project_root: Path | str,
    model_config: LBPSVMConfig | None = None,
    run_id: str | None = None,
) -> dict[str, object]:
    """Run the frozen grayscale E01 LBP-SVM experiment."""

    return _run_lbp_svm_experiment(
        dataset,
        frame_manifest=frame_manifest,
        run_root=run_root,
        project_root=project_root,
        model_config=model_config,
        run_id=run_id,
        experiment_id=EXPERIMENT_ID,
        model_name=MODEL_NAME,
        expected_color_mode="grayscale",
    )


def run_rgb_lbp_svm_experiment(
    dataset,
    *,
    frame_manifest: Path | str,
    run_root: Path | str,
    project_root: Path | str,
    model_config: LBPSVMConfig | None = None,
    run_id: str | None = None,
) -> dict[str, object]:
    """Run E05 RGB-LBP-SVM with dev-only selection and frozen test."""

    return _run_lbp_svm_experiment(
        dataset,
        frame_manifest=frame_manifest,
        run_root=run_root,
        project_root=project_root,
        model_config=model_config,
        run_id=run_id,
        experiment_id=RGB_EXPERIMENT_ID,
        model_name=RGB_MODEL_NAME,
        expected_color_mode="rgb",
    )


__all__ = ["run_lbp_svm_experiment", "run_rgb_lbp_svm_experiment"]
