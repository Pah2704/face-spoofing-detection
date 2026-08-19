"""Development-set threshold selection for spoof scores."""

from __future__ import annotations

import math
from collections.abc import Iterable
from numbers import Real

from .metrics import Metrics, _metrics_from_counts, evaluate_scores


def candidate_thresholds(scores: Iterable[object]) -> list[float]:
    """Return thresholds covering every distinct prediction partition.

    With the decision rule ``score >= threshold``, each unique score creates a
    new operating point.  One threshold immediately above the maximum is added
    to include the all-live prediction.  The all-spoof point is already covered
    by the minimum score.
    """

    try:
        raw_values = list(scores)
    except TypeError as exc:
        raise TypeError("scores must be an iterable") from exc
    if not raw_values:
        raise ValueError("at least one development score is required")

    values: list[float] = []
    for index, raw_value in enumerate(raw_values):
        if isinstance(raw_value, bool) or not isinstance(raw_value, Real):
            raise TypeError(f"scores[{index}] must be a real number, got {raw_value!r}")
        value = float(raw_value)
        if not math.isfinite(value):
            raise ValueError(f"scores[{index}] must be finite, got {raw_value!r}")
        values.append(value)

    unique_scores = sorted(set(values))
    above_maximum = math.nextafter(unique_scores[-1], math.inf)
    return [*unique_scores, above_maximum]


def _normalise_thresholds(thresholds: Iterable[object]) -> list[float]:
    try:
        raw_values = list(thresholds)
    except TypeError as exc:
        raise TypeError("thresholds must be an iterable") from exc
    if not raw_values:
        raise ValueError("thresholds must contain at least one candidate")

    values: list[float] = []
    for index, raw_value in enumerate(raw_values):
        if isinstance(raw_value, bool) or not isinstance(raw_value, Real):
            raise TypeError(
                f"thresholds[{index}] must be a real number, got {raw_value!r}"
            )
        value = float(raw_value)
        if math.isnan(value):
            raise ValueError(f"thresholds[{index}] must not be NaN")
        values.append(value)
    return sorted(set(values))


def select_threshold(
    y_true: Iterable[object],
    scores: Iterable[object],
    *,
    thresholds: Iterable[object] | None = None,
    zero_division: float = 0.0,
) -> Metrics:
    """Select the dev threshold with minimum ACER, then minimum APCER.

    The returned dictionary contains the selected threshold and all metrics at
    that operating point, so it can be serialised directly as
    ``threshold.json``.  If ACER and APCER are both tied, the lower threshold is
    retained as a deterministic final tie-breaker.

    When candidates are derived from the scores, the implementation sorts once
    and sweeps the operating points in ``O(n log n)`` time.  Supplying an
    explicit candidate list retains exhaustive evaluation because arbitrary
    thresholds need not coincide with observed scores.

    This function deliberately has no split argument: callers must pass only
    development predictions.  Evaluation on test data is performed separately
    with :func:`face_spoofing.evaluation.evaluate_scores` and the frozen value.
    """

    try:
        labels = list(y_true)
    except TypeError as exc:
        raise TypeError("y_true must be an iterable") from exc
    try:
        score_values = list(scores)
    except TypeError as exc:
        raise TypeError("scores must be an iterable") from exc

    if len(labels) != len(score_values):
        raise ValueError(
            "y_true and scores must have the same length "
            f"({len(labels)} != {len(score_values)})"
        )
    if not labels:
        raise ValueError("at least one development sample is required")

    if thresholds is not None:
        candidates = _normalise_thresholds(thresholds)
        best: Metrics | None = None
        for threshold in candidates:
            result = evaluate_scores(
                labels,
                score_values,
                threshold,
                zero_division=zero_division,
            )
            if best is None or (
                result["acer"],
                result["apcer"],
                result["threshold"],
            ) < (best["acer"], best["apcer"], best["threshold"]):
                best = result

        assert best is not None
        return best

    candidates = candidate_thresholds(score_values)

    # Validate labels and zero_division through the canonical evaluator while
    # also obtaining the all-live operating point above the maximum score.
    best = evaluate_scores(
        labels,
        score_values,
        candidates[-1],
        zero_division=zero_division,
    )
    zero_value = float(zero_division)
    tn, fp, fn, tp = (
        int(best["tn"]),
        int(best["fp"]),
        int(best["fn"]),
        int(best["tp"]),
    )

    # Lower the threshold through each distinct score.  Samples tied at that
    # score cross the decision boundary together because score >= threshold.
    ordered = sorted(
        ((float(score), int(label)) for label, score in zip(labels, score_values)),
        reverse=True,
    )
    index = 0
    for threshold in reversed(candidates[:-1]):
        while index < len(ordered) and ordered[index][0] == threshold:
            label = ordered[index][1]
            if label == 1:
                fn -= 1
                tp += 1
            else:
                tn -= 1
                fp += 1
            index += 1

        result: Metrics = {
            "threshold": threshold,
            **_metrics_from_counts(
                tn=tn,
                fp=fp,
                fn=fn,
                tp=tp,
                zero_division=zero_value,
            ),
        }
        if (result["acer"], result["apcer"], result["threshold"]) < (
            best["acer"],
            best["apcer"],
            best["threshold"],
        ):
            best = result

    return best


# More explicit alias for experiment scripts.
select_dev_threshold = select_threshold


__all__ = ["candidate_thresholds", "select_dev_threshold", "select_threshold"]
