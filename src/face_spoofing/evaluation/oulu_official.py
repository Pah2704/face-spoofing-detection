"""Secondary reporting compatible with the OULU-NPU baseline script.

The bundled ``Baseline/Tools/performances.m`` uses VLFeat's development EER
threshold, then reports APCER separately for each test attack type and a
worst-case row.  The project's primary comparison remains development
minimum-ACER for consistency across E01--E03; this module provides the
official-compatible view without changing that locked primary policy.

The MATLAB code orients larger scores toward bona-fide presentations.  Public
functions here retain the repository-wide contract that larger scores mean
spoof and convert orientation internally.
"""

from __future__ import annotations

import math
from numbers import Real
from typing import Iterable


def _materialise_labels(values: Iterable[object]) -> list[int]:
    try:
        raw = list(values)
    except TypeError as exc:
        raise TypeError("labels must be an iterable") from exc
    if not raw:
        raise ValueError("at least one label is required")
    labels: list[int] = []
    for index, value in enumerate(raw):
        if isinstance(value, bool) or not isinstance(value, Real) or value not in (0, 1):
            raise ValueError(f"labels[{index}] must be live=0 or spoof=1")
        labels.append(int(value))
    if set(labels) != {0, 1}:
        raise ValueError("both live and spoof labels are required")
    return labels


def _materialise_scores(values: Iterable[object]) -> list[float]:
    try:
        raw = list(values)
    except TypeError as exc:
        raise TypeError("scores must be an iterable") from exc
    scores: list[float] = []
    for index, value in enumerate(raw):
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(f"scores[{index}] must be a real number")
        score = float(value)
        if not math.isfinite(score):
            raise ValueError(f"scores[{index}] must be finite")
        scores.append(score)
    return scores


def select_oulu_eer_threshold(
    labels: Iterable[object],
    spoof_scores: Iterable[object],
) -> dict[str, float | str]:
    """Reproduce ``vl_roc(...).eerThreshold`` in spoof-score orientation.

    The returned EER is the staircase-intersection value used by VLFeat.  The
    threshold is converted back to the project decision rule
    ``spoof_score >= threshold => spoof``.
    """

    y_true = _materialise_labels(labels)
    scores = _materialise_scores(spoof_scores)
    if len(y_true) != len(scores):
        raise ValueError("labels and spoof_scores must have the same length")

    # OULU's MATLAB baseline uses positive/live labels and a score whose larger
    # value means live. Python's sort is stable, matching modern MATLAB's
    # deterministic ordering of equal values.
    live_scores = [-score for score in scores]
    order = sorted(range(len(scores)), key=lambda index: -live_scores[index])
    positives = sum(label == 0 for label in y_true)
    negatives = sum(label == 1 for label in y_true)

    true_positive = 0
    false_positive = 0
    true_positive_rates = [0.0]
    true_negative_rates = [1.0]
    for index in order:
        if y_true[index] == 0:
            true_positive += 1
        else:
            false_positive += 1
        true_positive_rates.append(true_positive / positives)
        true_negative_rates.append(1.0 - false_positive / negatives)

    crossing_index = max(
        index
        for index, (tnr, tpr) in enumerate(
            zip(true_negative_rates, true_positive_rates)
        )
        if tnr > tpr
    )
    if crossing_index == len(true_positive_rates) - 1:
        raise RuntimeError("development ROC does not cross the EER diagonal")

    if (
        true_positive_rates[crossing_index]
        == true_positive_rates[crossing_index + 1]
    ):
        eer = 1.0 - true_positive_rates[crossing_index]
    else:
        eer = 1.0 - true_negative_rates[crossing_index]

    live_threshold = live_scores[order[crossing_index]]
    return {
        "selection_split": "dev",
        "selection_policy": "vlfeat_eer_compatible",
        "eer": eer,
        "threshold": -live_threshold,
        "score_orientation": "higher_is_spoof",
        "decision_rule": "score >= threshold => spoof",
    }


def _attack_type(video_id: str) -> str:
    try:
        access_id = int(str(video_id).rsplit("_", 1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"invalid OULU-NPU video_id: {video_id!r}") from exc
    if access_id in {2, 3}:
        return "print"
    if access_id in {4, 5}:
        return "replay"
    if access_id == 1:
        return "live"
    raise ValueError(f"invalid OULU-NPU access id in {video_id!r}")


def evaluate_oulu_attack_types(
    video_ids: Iterable[object],
    labels: Iterable[object],
    spoof_scores: Iterable[object],
    threshold: float,
) -> dict[str, object]:
    """Report test APCER per print/replay and the OULU worst-case row."""

    ids = [str(value) for value in video_ids]
    y_true = _materialise_labels(labels)
    scores = _materialise_scores(spoof_scores)
    if not (len(ids) == len(y_true) == len(scores)):
        raise ValueError("video_ids, labels and spoof_scores must have equal length")
    if isinstance(threshold, bool) or not isinstance(threshold, Real):
        raise TypeError("threshold must be a real number")
    threshold_value = float(threshold)
    if math.isnan(threshold_value):
        raise ValueError("threshold must not be NaN")

    live_indices = [index for index, label in enumerate(y_true) if label == 0]
    bpcer = sum(scores[index] >= threshold_value for index in live_indices) / len(
        live_indices
    )
    groups: dict[str, dict[str, float | int]] = {}
    for attack_name in ("print", "replay"):
        indices = [
            index
            for index, (video_id, label) in enumerate(zip(ids, y_true))
            if label == 1 and _attack_type(video_id) == attack_name
        ]
        if not indices:
            raise ValueError(f"no {attack_name} attacks were provided")
        accepted_as_live = sum(scores[index] < threshold_value for index in indices)
        apcer = accepted_as_live / len(indices)
        groups[attack_name] = {
            "attacks": len(indices),
            "accepted_as_live": accepted_as_live,
            "apcer": apcer,
            "bpcer": bpcer,
            "acer": (apcer + bpcer) / 2.0,
        }

    return {
        "threshold": threshold_value,
        "selection_policy": "dev_vlfeat_eer_compatible",
        "groups": groups,
        "worst_case": {
            "apcer": max(float(group["apcer"]) for group in groups.values()),
            "bpcer": bpcer,
            "acer": max(float(group["acer"]) for group in groups.values()),
        },
    }


__all__ = ["evaluate_oulu_attack_types", "select_oulu_eer_threshold"]
