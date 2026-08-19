"""Frame-to-video score aggregation utilities."""

from __future__ import annotations

import math
from collections import OrderedDict
from collections.abc import Hashable, Iterable, Mapping
from dataclasses import asdict, dataclass
from numbers import Real
from typing import Any


@dataclass(frozen=True, slots=True)
class VideoPrediction:
    """Mean spoof score and metadata for one video."""

    video_id: Hashable
    score: float
    label: int | None
    num_frames: int

    def to_dict(self) -> dict[str, Any]:
        """Return a CSV/JSON-friendly representation."""

        return asdict(self)


def _materialise(values: Iterable[Any], *, name: str) -> list[Any]:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{name} must be an iterable of values, not a string")
    try:
        return list(values)
    except TypeError as exc:
        raise TypeError(f"{name} must be an iterable") from exc


def _normalise_label(value: object, *, index: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Real) or value not in (0, 1):
        raise ValueError(
            f"labels[{index}] must be 0 (live) or 1 (spoof), got {value!r}"
        )
    return int(value)


def mean_aggregate(
    video_ids: Iterable[Hashable],
    scores: Iterable[object],
    labels: Iterable[object] | None = None,
) -> list[VideoPrediction]:
    """Aggregate frame scores by video using the arithmetic mean.

    Output order follows the first occurrence of each ``video_id``.  When
    labels are supplied, all frames from a video must carry the same label;
    this catches manifest leakage/corruption before evaluation.
    """

    ids = _materialise(video_ids, name="video_ids")
    score_values = _materialise(scores, name="scores")
    label_values = None if labels is None else _materialise(labels, name="labels")

    if len(ids) != len(score_values):
        raise ValueError(
            "video_ids and scores must have the same length "
            f"({len(ids)} != {len(score_values)})"
        )
    if label_values is not None and len(ids) != len(label_values):
        raise ValueError(
            "video_ids and labels must have the same length "
            f"({len(ids)} != {len(label_values)})"
        )
    if not ids:
        raise ValueError("at least one frame prediction is required")

    grouped: OrderedDict[Hashable, dict[str, Any]] = OrderedDict()
    for index, (video_id, raw_score) in enumerate(zip(ids, score_values)):
        if not isinstance(video_id, Hashable):
            raise TypeError(f"video_ids[{index}] must be hashable, got {video_id!r}")
        if video_id is None or (isinstance(video_id, str) and not video_id.strip()):
            raise ValueError(f"video_ids[{index}] must not be empty")
        if isinstance(raw_score, bool) or not isinstance(raw_score, Real):
            raise TypeError(f"scores[{index}] must be a real number, got {raw_score!r}")
        score = float(raw_score)
        if not math.isfinite(score):
            raise ValueError(f"scores[{index}] must be finite, got {raw_score!r}")

        label = (
            None
            if label_values is None
            else _normalise_label(label_values[index], index=index)
        )
        if video_id not in grouped:
            grouped[video_id] = {"score_sum": score, "num_frames": 1, "label": label}
            continue

        group = grouped[video_id]
        if label_values is not None and group["label"] != label:
            raise ValueError(
                f"video {video_id!r} has inconsistent labels: "
                f"{group['label']} and {label}"
            )
        group["score_sum"] += score
        group["num_frames"] += 1

    return [
        VideoPrediction(
            video_id=video_id,
            score=group["score_sum"] / group["num_frames"],
            label=group["label"],
            num_frames=group["num_frames"],
        )
        for video_id, group in grouped.items()
    ]


def mean_aggregate_records(
    records: Iterable[Mapping[str, Any]],
    *,
    video_id_key: str = "video_id",
    score_key: str = "score",
    label_key: str | None = "label",
) -> list[VideoPrediction]:
    """Aggregate dictionaries representing frame-level predictions.

    Set ``label_key=None`` for inference-only records.  With the default label
    key, labels may be absent from every record, but partially missing labels
    are rejected.
    """

    rows = _materialise(records, name="records")
    if not rows:
        raise ValueError("at least one frame prediction is required")
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise TypeError(f"records[{index}] must be a mapping")
        for key in (video_id_key, score_key):
            if key not in row:
                raise KeyError(f"records[{index}] is missing required key {key!r}")

    ids = [row[video_id_key] for row in rows]
    scores = [row[score_key] for row in rows]
    labels: list[Any] | None = None
    if label_key is not None:
        has_label = [label_key in row for row in rows]
        if any(has_label) and not all(has_label):
            missing_index = has_label.index(False)
            raise KeyError(
                f"records[{missing_index}] is missing label key {label_key!r}; "
                "labels must be present for every record or none"
            )
        if all(has_label):
            labels = [row[label_key] for row in rows]
    return mean_aggregate(ids, scores, labels)


# Readable aliases used by training/evaluation scripts.
aggregate_video_scores = mean_aggregate
aggregate_by_video = mean_aggregate_records


__all__ = [
    "VideoPrediction",
    "aggregate_by_video",
    "aggregate_video_scores",
    "mean_aggregate",
    "mean_aggregate_records",
]
