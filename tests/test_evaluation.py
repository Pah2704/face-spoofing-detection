"""Unit tests for the dependency-free evaluation engine."""

from __future__ import annotations

import math
import random
import unittest

from face_spoofing.evaluation import (
    candidate_thresholds,
    compute_metrics,
    confusion_matrix,
    evaluate_scores,
    mean_aggregate,
    mean_aggregate_records,
    predict_labels,
    select_threshold,
)


class MetricsTest(unittest.TestCase):
    def test_metrics_match_hand_calculation(self) -> None:
        # TP=2, TN=2, FP=1, FN=1.
        result = compute_metrics(
            y_true=[1, 1, 1, 0, 0, 0],
            y_pred=[1, 1, 0, 0, 0, 1],
        )

        self.assertEqual(
            {key: result[key] for key in ("tn", "fp", "fn", "tp")},
            {"tn": 2, "fp": 1, "fn": 1, "tp": 2},
        )
        self.assertAlmostEqual(result["accuracy"], 4 / 6)
        self.assertAlmostEqual(result["precision"], 2 / 3)
        self.assertAlmostEqual(result["recall"], 2 / 3)
        self.assertAlmostEqual(result["f1"], 2 / 3)
        self.assertAlmostEqual(result["apcer"], 1 / 3)
        self.assertAlmostEqual(result["bpcer"], 1 / 3)
        self.assertAlmostEqual(result["acer"], 1 / 3)
        self.assertEqual(confusion_matrix([0, 0, 1], [0, 1, 1]), [[1, 1], [0, 1]])

    def test_score_equal_to_threshold_is_spoof(self) -> None:
        self.assertEqual(predict_labels([0.49, 0.5, 0.51], 0.5), [0, 1, 1])

        result = evaluate_scores([0, 1, 1], [0.49, 0.5, 0.51], 0.5)
        self.assertEqual(result["threshold"], 0.5)
        self.assertEqual(result["accuracy"], 1.0)
        self.assertEqual(result["acer"], 0.0)

    def test_single_class_uses_configured_zero_division(self) -> None:
        live_only = compute_metrics([0, 0], [0, 1])
        self.assertEqual(live_only["apcer"], 0.0)
        self.assertEqual(live_only["bpcer"], 0.5)
        self.assertEqual(live_only["acer"], 0.25)

        attack_only = compute_metrics([1, 1], [1, 0], zero_division=-1.0)
        self.assertEqual(attack_only["apcer"], 0.5)
        self.assertEqual(attack_only["bpcer"], -1.0)
        self.assertEqual(attack_only["acer"], -0.25)

    def test_invalid_metric_inputs_fail_loudly(self) -> None:
        with self.assertRaisesRegex(ValueError, "same length"):
            compute_metrics([0], [0, 1])
        with self.assertRaisesRegex(ValueError, "at least one"):
            compute_metrics([], [])
        with self.assertRaisesRegex(ValueError, "must be 0"):
            compute_metrics([2], [0])
        with self.assertRaisesRegex(ValueError, "finite"):
            predict_labels([math.nan])


class AggregationTest(unittest.TestCase):
    def test_mean_aggregation_preserves_video_order(self) -> None:
        videos = mean_aggregate(
            video_ids=["video_b", "video_a", "video_b", "video_a"],
            scores=[0.2, 0.8, 0.4, 0.6],
            labels=[0, 1, 0, 1],
        )

        self.assertEqual([video.video_id for video in videos], ["video_b", "video_a"])
        self.assertAlmostEqual(videos[0].score, 0.3)
        self.assertEqual(videos[0].label, 0)
        self.assertEqual(videos[0].num_frames, 2)
        self.assertAlmostEqual(videos[1].score, 0.7)
        self.assertEqual(videos[1].to_dict()["video_id"], "video_a")

    def test_record_aggregation_supports_unlabelled_inference(self) -> None:
        videos = mean_aggregate_records(
            [
                {"video_id": "v1", "score": 0.1},
                {"video_id": "v1", "score": 0.3},
            ]
        )
        self.assertEqual(len(videos), 1)
        self.assertIsNone(videos[0].label)
        self.assertAlmostEqual(videos[0].score, 0.2)

    def test_inconsistent_video_labels_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "inconsistent labels"):
            mean_aggregate(["v1", "v1"], [0.1, 0.9], [0, 1])

    def test_invalid_aggregation_inputs_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "same length"):
            mean_aggregate(["v1"], [0.1, 0.2])
        with self.assertRaisesRegex(ValueError, "at least one"):
            mean_aggregate([], [])
        with self.assertRaisesRegex(KeyError, "missing label"):
            mean_aggregate_records(
                [
                    {"video_id": "v1", "score": 0.1, "label": 0},
                    {"video_id": "v1", "score": 0.2},
                ]
            )


class ThresholdSelectionTest(unittest.TestCase):
    @staticmethod
    def _exhaustive_reference(
        labels: list[int], scores: list[float], zero_division: float = 0.0
    ) -> dict[str, int | float]:
        results = [
            evaluate_scores(
                labels,
                scores,
                threshold,
                zero_division=zero_division,
            )
            for threshold in candidate_thresholds(scores)
        ]
        return min(
            results,
            key=lambda item: (item["acer"], item["apcer"], item["threshold"]),
        )

    def test_selects_minimum_dev_acer(self) -> None:
        result = select_threshold(
            y_true=[0, 0, 1, 1],
            scores=[0.1, 0.4, 0.6, 0.9],
        )

        self.assertEqual(result["threshold"], 0.6)
        self.assertEqual(result["acer"], 0.0)
        self.assertEqual(result["apcer"], 0.0)
        self.assertEqual(result["bpcer"], 0.0)

    def test_acer_tie_prefers_lower_apcer(self) -> None:
        # At 0.2: APCER=0, BPCER=1, ACER=.5.
        # Above .8: APCER=1, BPCER=0, ACER=.5.
        result = select_threshold([1, 0], [0.2, 0.8])

        self.assertEqual(result["threshold"], 0.2)
        self.assertEqual(result["acer"], 0.5)
        self.assertEqual(result["apcer"], 0.0)

    def test_candidates_include_all_live_operating_point(self) -> None:
        candidates = candidate_thresholds([0.2, 0.8, 0.2])

        self.assertEqual(candidates[:2], [0.2, 0.8])
        self.assertGreater(candidates[-1], 0.8)
        all_live = evaluate_scores([0, 1], [0.2, 0.8], candidates[-1])
        self.assertEqual((all_live["tn"], all_live["fn"]), (1, 1))

    def test_explicit_candidate_thresholds_are_supported(self) -> None:
        result = select_threshold(
            [0, 1],
            [0.4, 0.6],
            thresholds=[0.5, 0.7],
        )
        self.assertEqual(result["threshold"], 0.5)

    def test_sweep_matches_exhaustive_reference_with_ties(self) -> None:
        rng = random.Random(42)
        score_pool = [-1.0, 0.0, 0.25, 0.5, 0.5, 1.0]
        for _ in range(250):
            size = rng.randint(1, 30)
            labels = [rng.randint(0, 1) for _ in range(size)]
            scores = [rng.choice(score_pool) for _ in range(size)]
            zero_division = rng.choice([0.0, -1.0, 0.25])
            with self.subTest(size=size, labels=sum(labels)):
                self.assertEqual(
                    select_threshold(
                        labels,
                        scores,
                        zero_division=zero_division,
                    ),
                    self._exhaustive_reference(labels, scores, zero_division),
                )

    def test_sweep_preserves_signed_zero_candidate(self) -> None:
        result = select_threshold([1, 1], [-0.0, 1.0])
        reference = self._exhaustive_reference([1, 1], [-0.0, 1.0])

        self.assertEqual(result, reference)
        self.assertEqual(math.copysign(1.0, result["threshold"]), -1.0)

    def test_threshold_input_validation(self) -> None:
        with self.assertRaisesRegex(ValueError, "same length"):
            select_threshold([0], [0.1, 0.2])
        with self.assertRaisesRegex(ValueError, "at least one"):
            select_threshold([], [])
        with self.assertRaisesRegex(ValueError, "at least one candidate"):
            select_threshold([0], [0.1], thresholds=[])


if __name__ == "__main__":
    unittest.main()
