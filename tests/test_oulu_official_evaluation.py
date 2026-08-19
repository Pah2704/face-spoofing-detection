from __future__ import annotations

import unittest

from face_spoofing.evaluation.oulu_official import (
    evaluate_oulu_attack_types,
    select_oulu_eer_threshold,
)


class OuluEerCompatibilityTests(unittest.TestCase):
    def test_vlfeat_staircase_threshold_and_eer_are_reproduced(self) -> None:
        result = select_oulu_eer_threshold(
            [0, 0, 1, 1],
            [0.1, 0.4, 0.6, 0.9],
        )

        self.assertEqual(result["eer"], 0.0)
        self.assertEqual(result["threshold"], 0.4)
        self.assertEqual(result["selection_split"], "dev")

    def test_crossing_on_attack_step_uses_live_miss_rate(self) -> None:
        result = select_oulu_eer_threshold(
            [0, 1, 0, 1],
            [0.1, 0.2, 0.8, 0.9],
        )

        self.assertEqual(result["eer"], 0.5)
        self.assertEqual(result["threshold"], 0.2)

    def test_input_contract_requires_both_classes_and_equal_lengths(self) -> None:
        with self.assertRaisesRegex(ValueError, "both live and spoof"):
            select_oulu_eer_threshold([0, 0], [0.1, 0.2])
        with self.assertRaisesRegex(ValueError, "same length"):
            select_oulu_eer_threshold([0, 1], [0.1])


class OuluAttackTypeReportingTests(unittest.TestCase):
    def test_print_replay_and_worst_case_match_hand_calculation(self) -> None:
        result = evaluate_oulu_attack_types(
            ["1_1_01_1", "1_1_02_1", "1_1_03_2", "1_1_04_4", "1_1_05_5"],
            [0, 0, 1, 1, 1],
            [0.2, 0.8, 0.4, 0.3, 0.9],
            0.5,
        )

        self.assertEqual(result["groups"]["print"]["apcer"], 1.0)
        self.assertEqual(result["groups"]["replay"]["apcer"], 0.5)
        self.assertEqual(result["groups"]["print"]["bpcer"], 0.5)
        self.assertEqual(result["groups"]["print"]["acer"], 0.75)
        self.assertEqual(result["worst_case"]["acer"], 0.75)

    def test_invalid_video_id_is_rejected_for_attacks(self) -> None:
        with self.assertRaisesRegex(ValueError, "video_id"):
            evaluate_oulu_attack_types(
                ["1_1_01_1", "bad", "1_1_04_4"],
                [0, 1, 1],
                [0.1, 0.2, 0.3],
                0.5,
            )


if __name__ == "__main__":
    unittest.main()
