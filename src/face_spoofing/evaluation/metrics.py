"""Binary classification metrics for face anti-spoofing.

The project uses ``0`` for bona-fide/live presentations and ``1`` for
spoof/attack presentations.  A score greater than or equal to the decision
threshold is therefore classified as spoof.

This module intentionally has no third-party dependencies so that the metric
definitions can be tested independently from the training stack.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from numbers import Real
from typing import TypeAlias


MetricValue: TypeAlias = int | float
Metrics: TypeAlias = dict[str, MetricValue]


def _as_list(values: Iterable[object], *, name: str) -> list[object]:
    """Materialise an iterable and provide a useful error for non-iterables."""

    if isinstance(values, (str, bytes)):
        raise TypeError(f"{name} must be an iterable of values, not a string")
    try:
        return list(values)
    except TypeError as exc:
        raise TypeError(f"{name} must be an iterable") from exc


def _validate_binary_labels(values: Iterable[object], *, name: str) -> list[int]:
    labels = _as_list(values, name=name)
    normalised: list[int] = []
    for index, value in enumerate(labels):
        if isinstance(value, bool) or not isinstance(value, Real) or value not in (0, 1):
            raise ValueError(
                f"{name}[{index}] must be 0 (live) or 1 (spoof), got {value!r}"
            )
        normalised.append(int(value))
    return normalised


def _validate_scores(scores: Iterable[object]) -> list[float]:
    values = _as_list(scores, name="scores")
    normalised: list[float] = []
    for index, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(f"scores[{index}] must be a real number, got {value!r}")
        score = float(value)
        if not math.isfinite(score):
            raise ValueError(f"scores[{index}] must be finite, got {value!r}")
        normalised.append(score)
    return normalised


def _validate_threshold(threshold: object) -> float:
    if isinstance(threshold, bool) or not isinstance(threshold, Real):
        raise TypeError(f"threshold must be a real number, got {threshold!r}")
    value = float(threshold)
    if math.isnan(value):
        raise ValueError("threshold must not be NaN")
    return value


def _safe_divide(numerator: int, denominator: int, zero_division: float) -> float:
    return numerator / denominator if denominator else zero_division


def _metrics_from_counts(
    *, tn: int, fp: int, fn: int, tp: int, zero_division: float
) -> Metrics:
    """Build the metric dictionary from already validated confusion counts."""

    total = tn + fp + fn + tp
    accuracy = (tp + tn) / total
    precision = _safe_divide(tp, tp + fp, zero_division)
    recall = _safe_divide(tp, tp + fn, zero_division)
    f1 = _safe_divide(2 * tp, 2 * tp + fp + fn, zero_division)
    apcer = _safe_divide(fn, tp + fn, zero_division)
    bpcer = _safe_divide(fp, tn + fp, zero_division)

    return {
        "n_samples": total,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "apcer": apcer,
        "bpcer": bpcer,
        "acer": (apcer + bpcer) / 2.0,
    }


def predict_labels(scores: Iterable[object], threshold: float = 0.5) -> list[int]:
    """Convert spoof scores to labels using ``score >= threshold``.

    Scores must be finite.  Infinite thresholds are accepted because ``+inf``
    is a well-defined way to represent the all-live operating point.
    """

    score_values = _validate_scores(scores)
    threshold_value = _validate_threshold(threshold)
    return [int(score >= threshold_value) for score in score_values]


def confusion_counts(
    y_true: Iterable[object], y_pred: Iterable[object]
) -> dict[str, int]:
    """Return binary confusion counts for positive class spoof/attack."""

    true_labels = _validate_binary_labels(y_true, name="y_true")
    predicted_labels = _validate_binary_labels(y_pred, name="y_pred")
    if len(true_labels) != len(predicted_labels):
        raise ValueError(
            "y_true and y_pred must have the same length "
            f"({len(true_labels)} != {len(predicted_labels)})"
        )
    if not true_labels:
        raise ValueError("at least one sample is required")

    tn = fp = fn = tp = 0
    for actual, predicted in zip(true_labels, predicted_labels):
        if actual == 1 and predicted == 1:
            tp += 1
        elif actual == 1:
            fn += 1
        elif predicted == 1:
            fp += 1
        else:
            tn += 1
    return {"tn": tn, "fp": fp, "fn": fn, "tp": tp}


def confusion_matrix(
    y_true: Iterable[object], y_pred: Iterable[object]
) -> list[list[int]]:
    """Return ``[[TN, FP], [FN, TP]]`` using label order ``[0, 1]``."""

    counts = confusion_counts(y_true, y_pred)
    return [
        [counts["tn"], counts["fp"]],
        [counts["fn"], counts["tp"]],
    ]


def compute_metrics(
    y_true: Iterable[object],
    y_pred: Iterable[object],
    *,
    zero_division: float = 0.0,
) -> Metrics:
    """Compute project metrics for already-thresholded predictions.

    ``APCER = FN / (TP + FN)`` is the fraction of attacks accepted as live.
    ``BPCER = FP / (TN + FP)`` is the fraction of live samples rejected as
    attacks.  ``ACER`` is their arithmetic mean.

    A split containing only one class makes one of these rates mathematically
    undefined.  For stable machine-readable output it is assigned
    ``zero_division`` (``0.0`` by default), matching the common convention for
    undefined precision/recall.  Empty inputs remain an error because no metric
    is meaningful for them.
    """

    if isinstance(zero_division, bool) or not isinstance(zero_division, Real):
        raise TypeError("zero_division must be a real number")
    zero_value = float(zero_division)
    if not math.isfinite(zero_value):
        raise ValueError("zero_division must be finite")

    counts = confusion_counts(y_true, y_pred)
    tn, fp, fn, tp = (
        counts["tn"],
        counts["fp"],
        counts["fn"],
        counts["tp"],
    )
    return _metrics_from_counts(
        tn=tn,
        fp=fp,
        fn=fn,
        tp=tp,
        zero_division=zero_value,
    )


def evaluate_scores(
    y_true: Iterable[object],
    scores: Iterable[object],
    threshold: float = 0.5,
    *,
    zero_division: float = 0.0,
) -> Metrics:
    """Threshold spoof scores and compute all binary metrics."""

    true_labels = _validate_binary_labels(y_true, name="y_true")
    score_values = _validate_scores(scores)
    if len(true_labels) != len(score_values):
        raise ValueError(
            "y_true and scores must have the same length "
            f"({len(true_labels)} != {len(score_values)})"
        )
    threshold_value = _validate_threshold(threshold)
    predictions = predict_labels(score_values, threshold_value)
    metrics = compute_metrics(true_labels, predictions, zero_division=zero_division)
    return {"threshold": threshold_value, **metrics}


# A descriptive alias for callers that prefer an explicit binary name.
compute_binary_metrics = compute_metrics


__all__ = [
    "Metrics",
    "compute_binary_metrics",
    "compute_metrics",
    "confusion_counts",
    "confusion_matrix",
    "evaluate_scores",
    "predict_labels",
]
