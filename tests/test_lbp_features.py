"""Unit tests for the spatial uniform-LBP descriptor."""

from __future__ import annotations

import unittest

import numpy as np

from face_spoofing.features import extract_lbp, extract_rgb_lbp
from face_spoofing.features.lbp import _uniform_lbp_bins


class UniformLbpMappingTest(unittest.TestCase):
    def test_impulse_histogram_matches_hand_calculation(self) -> None:
        # The bright centre has zero set bits (bin 0).  Every surrounding
        # zero-valued pixel has eight neighbours >= itself (bin 8).
        image = np.zeros((3, 3), dtype=np.uint8)
        image[1, 1] = 255

        feature = extract_lbp(image, grid_rows=1, grid_cols=1)
        expected = np.zeros(10, dtype=np.float32)
        expected[0] = np.float32(1 / 9)
        expected[8] = np.float32(8 / 9)

        np.testing.assert_allclose(feature, expected, rtol=0.0, atol=1e-7)

    def test_alternating_ring_maps_to_non_uniform_bin(self) -> None:
        image = np.array(
            [
                [255, 0, 255],
                [0, 128, 0],
                [255, 0, 255],
            ],
            dtype=np.uint8,
        )

        bins = _uniform_lbp_bins(image)

        # Around the centre the circular pattern is 10101010: eight
        # transitions, so it belongs to the catch-all non-uniform bin 9.
        self.assertEqual(int(bins[1, 1]), 9)

    def test_constant_image_occupies_bin_eight_in_every_cell(self) -> None:
        feature = extract_lbp(np.full((8, 8), 73, dtype=np.uint8))
        cells = feature.reshape(16, 10)

        expected = np.zeros_like(cells)
        expected[:, 8] = 1.0
        np.testing.assert_array_equal(cells, expected)


class SpatialLbpDescriptorTest(unittest.TestCase):
    def test_default_shape_dtype_and_per_cell_normalisation(self) -> None:
        image = np.arange(8 * 12, dtype=np.uint8).reshape(8, 12)

        feature = extract_lbp(image)

        self.assertEqual(feature.shape, (160,))
        self.assertEqual(feature.dtype, np.float32)
        np.testing.assert_allclose(
            feature.reshape(16, 10).sum(axis=1),
            np.ones(16, dtype=np.float32),
            rtol=0.0,
            atol=1e-7,
        )

    def test_descriptor_is_invariant_to_safe_brightness_offset(self) -> None:
        rng = np.random.default_rng(2026)
        image = rng.integers(20, 200, size=(13, 17), dtype=np.uint8)
        brighter = image + np.uint8(30)

        np.testing.assert_array_equal(extract_lbp(image), extract_lbp(brighter))

    def test_non_divisible_image_is_split_without_losing_pixels(self) -> None:
        image = np.full((7, 11), 10, dtype=np.uint8)

        feature = extract_lbp(image, grid_rows=3, grid_cols=4)

        self.assertEqual(feature.shape, (120,))
        np.testing.assert_array_equal(
            feature.reshape(12, 10)[:, 8], np.ones(12, dtype=np.float32)
        )


class RgbLbpDescriptorTest(unittest.TestCase):
    def test_rgb_descriptor_concatenates_r_g_b_in_channel_major_order(self) -> None:
        red = np.arange(6 * 7, dtype=np.uint8).reshape(6, 7)
        green = np.flipud(red)
        blue = np.fliplr(red)
        rgb = np.stack((red, green, blue), axis=2)

        feature = extract_rgb_lbp(rgb, grid_rows=2, grid_cols=3)
        expected = np.concatenate(
            [
                extract_lbp(red, grid_rows=2, grid_cols=3),
                extract_lbp(green, grid_rows=2, grid_cols=3),
                extract_lbp(blue, grid_rows=2, grid_cols=3),
            ]
        )

        self.assertEqual(feature.shape, (180,))
        self.assertEqual(feature.dtype, np.float32)
        np.testing.assert_array_equal(feature, expected)

    def test_rgb_descriptor_normalises_every_cell_of_every_channel(self) -> None:
        rng = np.random.default_rng(42)
        image = rng.integers(0, 256, size=(16, 16, 3), dtype=np.uint8)

        feature = extract_rgb_lbp(image, grid_rows=4, grid_cols=4)

        self.assertEqual(feature.shape, (480,))
        np.testing.assert_allclose(
            feature.reshape(3, 16, 10).sum(axis=2),
            np.ones((3, 16), dtype=np.float32),
            rtol=0.0,
            atol=1e-7,
        )

    def test_rgb_image_contract_is_enforced(self) -> None:
        with self.assertRaisesRegex(ValueError, "HxWx3 RGB"):
            extract_rgb_lbp(np.zeros((4, 4), dtype=np.uint8))
        with self.assertRaisesRegex(ValueError, "HxWx3 RGB"):
            extract_rgb_lbp(np.zeros((4, 4, 4), dtype=np.uint8))
        with self.assertRaisesRegex(TypeError, "uint8"):
            extract_rgb_lbp(np.zeros((4, 4, 3), dtype=np.float32))
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            extract_rgb_lbp(np.empty((0, 4, 3), dtype=np.uint8))


class LbpValidationTest(unittest.TestCase):
    def test_image_contract_is_enforced(self) -> None:
        with self.assertRaisesRegex(TypeError, "numpy.ndarray"):
            extract_lbp([[0, 1], [2, 3]])  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "2D grayscale"):
            extract_lbp(np.zeros((4, 4, 3), dtype=np.uint8))
        with self.assertRaisesRegex(TypeError, "uint8"):
            extract_lbp(np.zeros((4, 4), dtype=np.float32))
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            extract_lbp(np.empty((0, 4), dtype=np.uint8))

    def test_only_fixed_eight_neighbour_configuration_is_supported(self) -> None:
        image = np.zeros((4, 4), dtype=np.uint8)
        with self.assertRaisesRegex(ValueError, "radius=1 and points=8"):
            extract_lbp(image, radius=2)
        with self.assertRaisesRegex(ValueError, "radius=1 and points=8"):
            extract_lbp(image, points=16)
        with self.assertRaisesRegex(TypeError, "radius must be an integer"):
            extract_lbp(image, radius=1.0)  # type: ignore[arg-type]

    def test_grid_must_be_positive_and_fit_the_image(self) -> None:
        image = np.zeros((4, 5), dtype=np.uint8)
        with self.assertRaisesRegex(ValueError, "must be positive"):
            extract_lbp(image, grid_rows=0)
        with self.assertRaisesRegex(TypeError, "grid_cols must be an integer"):
            extract_lbp(image, grid_cols=True)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "must not exceed"):
            extract_lbp(image, grid_cols=6)


if __name__ == "__main__":
    unittest.main()
