"""Unit tests for deterministic uniform frame sampling."""

from __future__ import annotations

import unittest

from face_spoofing.data.frame_sampler import uniform_frame_indices


class UniformFrameIndicesTests(unittest.TestCase):
    def test_default_sample_is_uniform_and_includes_endpoints(self) -> None:
        self.assertEqual(
            uniform_frame_indices(100),
            [0, 11, 22, 33, 44, 55, 66, 77, 88, 99],
        )

    def test_result_is_deterministic_unique_and_strictly_increasing(self) -> None:
        first = uniform_frame_indices(37, frames_per_video=10)
        second = uniform_frame_indices(37, frames_per_video=10)

        self.assertEqual(first, second)
        self.assertEqual(len(first), 10)
        self.assertEqual(len(set(first)), 10)
        self.assertEqual((first[0], first[-1]), (0, 36))
        self.assertTrue(all(left < right for left, right in zip(first, first[1:])))

    def test_exact_length_video_selects_every_frame(self) -> None:
        self.assertEqual(
            uniform_frame_indices(5, frames_per_video=5),
            [0, 1, 2, 3, 4],
        )

    def test_two_samples_are_the_first_and_last_frames(self) -> None:
        self.assertEqual(
            uniform_frame_indices(23, frames_per_video=2),
            [0, 22],
        )

    def test_video_shorter_than_requested_sample_fails_clearly(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            r"video is too short: it has 9 frames but 10 unique frames",
        ):
            uniform_frame_indices(9)

    def test_invalid_counts_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "total_frames must be positive"):
            uniform_frame_indices(0)
        with self.assertRaisesRegex(ValueError, "must be at least 2"):
            uniform_frame_indices(10, frames_per_video=1)

    def test_non_integer_counts_are_rejected(self) -> None:
        with self.assertRaisesRegex(TypeError, "total_frames must be an integer"):
            uniform_frame_indices(10.0)  # type: ignore[arg-type]
        with self.assertRaisesRegex(
            TypeError, "frames_per_video must be an integer"
        ):
            uniform_frame_indices(10, frames_per_video=True)


if __name__ == "__main__":
    unittest.main()
