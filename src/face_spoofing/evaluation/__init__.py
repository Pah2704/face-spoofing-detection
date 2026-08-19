"""Evaluation primitives for frame and video face anti-spoofing scores."""

from .aggregation import (
    VideoPrediction,
    aggregate_by_video,
    aggregate_video_scores,
    mean_aggregate,
    mean_aggregate_records,
)
from .metrics import (
    Metrics,
    compute_binary_metrics,
    compute_metrics,
    confusion_counts,
    confusion_matrix,
    evaluate_scores,
    predict_labels,
)
from .threshold import candidate_thresholds, select_dev_threshold, select_threshold
from .oulu_official import evaluate_oulu_attack_types, select_oulu_eer_threshold

__all__ = [
    "Metrics",
    "VideoPrediction",
    "aggregate_by_video",
    "aggregate_video_scores",
    "candidate_thresholds",
    "compute_binary_metrics",
    "compute_metrics",
    "confusion_counts",
    "confusion_matrix",
    "evaluate_scores",
    "evaluate_oulu_attack_types",
    "mean_aggregate",
    "mean_aggregate_records",
    "predict_labels",
    "select_dev_threshold",
    "select_oulu_eer_threshold",
    "select_threshold",
]
