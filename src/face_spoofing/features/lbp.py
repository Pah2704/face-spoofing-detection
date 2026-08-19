"""Uniform Local Binary Pattern (LBP) spatial histograms.

The E01 baseline uses the rotation-invariant uniform LBP mapping for the eight
immediate neighbours of each pixel.  Uniform patterns (at most two circular
bit transitions) map to bins 0--8 according to their number of set bits;
all other patterns map to bin 9.  Histograms are computed independently in a
row-major spatial grid and L1-normalised before concatenation.

Only ``radius=1`` and ``points=8`` are intentionally supported.  Border pixels
use edge replication so the descriptor does not introduce an artificial dark
frame around the image.

The E05 RGB-LBP ablation applies the exact same descriptor independently to
the R, G, and B channels, then concatenates the results in channel-major RGB
order.  Keeping the grayscale primitive shared makes colour representation the
only feature-extraction factor changed between E01 and E05.
"""

from __future__ import annotations

from numbers import Integral

import numpy as np
from numpy.typing import NDArray


_NUM_BINS = 10
_SUPPORTED_RADIUS = 1
_SUPPORTED_POINTS = 8


def _validate_integer(value: object, *, name: str) -> int:
    """Return an integer parameter while rejecting booleans and floats."""

    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer, got {value!r}")
    return int(value)


def _validate_image(image: object) -> NDArray[np.uint8]:
    """Validate the strict grayscale-uint8 input contract."""

    if not isinstance(image, np.ndarray):
        raise TypeError("image must be a numpy.ndarray")
    if image.ndim != 2:
        raise ValueError(
            f"image must be a 2D grayscale array, got shape {image.shape}"
        )
    if image.dtype != np.uint8:
        raise TypeError(f"image dtype must be uint8, got {image.dtype}")
    if image.size == 0:
        raise ValueError("image must not be empty")
    return image


def _validate_rgb_image(image: object) -> NDArray[np.uint8]:
    """Validate the strict RGB-uint8 input contract."""

    if not isinstance(image, np.ndarray):
        raise TypeError("image must be a numpy.ndarray")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(
            f"image must be an HxWx3 RGB array, got shape {image.shape}"
        )
    if image.dtype != np.uint8:
        raise TypeError(f"image dtype must be uint8, got {image.dtype}")
    if image.size == 0:
        raise ValueError("image must not be empty")
    return image


def _uniform_lbp_bins(image: NDArray[np.uint8]) -> NDArray[np.uint8]:
    """Map every pixel to one of the ten uniform-LBP bins.

    Neighbours are visited clockwise starting at the top-left pixel.  A bit is
    one when the neighbour is greater than or equal to the centre.  Replicating
    the edge provides all eight neighbours for border pixels.
    """

    padded = np.pad(image, pad_width=1, mode="edge")
    height, width = image.shape
    neighbours = np.stack(
        (
            padded[0:height, 0:width],  # top-left
            padded[0:height, 1 : width + 1],  # top
            padded[0:height, 2 : width + 2],  # top-right
            padded[1 : height + 1, 2 : width + 2],  # right
            padded[2 : height + 2, 2 : width + 2],  # bottom-right
            padded[2 : height + 2, 1 : width + 1],  # bottom
            padded[2 : height + 2, 0:width],  # bottom-left
            padded[1 : height + 1, 0:width],  # left
        ),
        axis=0,
    )
    centre = image[np.newaxis, :, :]
    bits = neighbours >= centre

    ones = bits.sum(axis=0, dtype=np.uint8)
    transitions = np.count_nonzero(bits != np.roll(bits, shift=1, axis=0), axis=0)
    return np.where(transitions <= 2, ones, _NUM_BINS - 1).astype(
        np.uint8, copy=False
    )


def extract_lbp(
    image: NDArray[np.uint8],
    radius: int = 1,
    points: int = 8,
    grid_rows: int = 4,
    grid_cols: int = 4,
) -> NDArray[np.float32]:
    """Extract a spatial uniform-LBP descriptor from a grayscale image.

    Args:
        image: Non-empty 2D ``uint8`` grayscale image.
        radius: Neighbourhood radius.  Only ``1`` is supported.
        points: Number of neighbours.  Only ``8`` is supported.
        grid_rows: Number of spatial cells along the image height.
        grid_cols: Number of spatial cells along the image width.

    Returns:
        Row-major concatenation of one L1-normalised, 10-bin histogram per
        cell.  The default 4x4 grid therefore returns a float32 vector with
        160 elements.

    Raises:
        TypeError: If the image or a parameter has the wrong type.
        ValueError: If dimensions or parameter values are unsupported.
    """

    grayscale = _validate_image(image)
    radius_value = _validate_integer(radius, name="radius")
    points_value = _validate_integer(points, name="points")
    rows = _validate_integer(grid_rows, name="grid_rows")
    cols = _validate_integer(grid_cols, name="grid_cols")

    if radius_value != _SUPPORTED_RADIUS or points_value != _SUPPORTED_POINTS:
        raise ValueError("only radius=1 and points=8 are supported")
    if rows <= 0 or cols <= 0:
        raise ValueError("grid_rows and grid_cols must be positive")

    height, width = grayscale.shape
    if rows > height or cols > width:
        raise ValueError(
            "grid dimensions must not exceed image dimensions "
            f"(grid={rows}x{cols}, image={height}x{width})"
        )

    lbp_bins = _uniform_lbp_bins(grayscale)
    row_cells = np.array_split(lbp_bins, rows, axis=0)
    histograms: list[NDArray[np.float32]] = []
    for row_cell in row_cells:
        for cell in np.array_split(row_cell, cols, axis=1):
            histogram = np.bincount(cell.ravel(), minlength=_NUM_BINS).astype(
                np.float32
            )
            histogram /= np.float32(cell.size)
            histograms.append(histogram)

    return np.concatenate(histograms).astype(np.float32, copy=False)


def extract_rgb_lbp(
    image: NDArray[np.uint8],
    radius: int = 1,
    points: int = 8,
    grid_rows: int = 4,
    grid_cols: int = 4,
) -> NDArray[np.float32]:
    """Extract and concatenate spatial uniform-LBP from R, G, and B.

    Args:
        image: Non-empty ``uint8`` image with shape ``H x W x 3`` in RGB
            channel order.
        radius: Neighbourhood radius forwarded to :func:`extract_lbp`.
        points: Number of neighbours forwarded to :func:`extract_lbp`.
        grid_rows: Spatial cells along the image height.
        grid_cols: Spatial cells along the image width.

    Returns:
        ``[LBP(R), LBP(G), LBP(B)]`` as a contiguous float32 vector.  With an
        8x8 grid the descriptor has ``3 * 8 * 8 * 10 = 1920`` values.
    """

    rgb = _validate_rgb_image(image)
    channel_features = [
        extract_lbp(
            rgb[:, :, channel],
            radius=radius,
            points=points,
            grid_rows=grid_rows,
            grid_cols=grid_cols,
        )
        for channel in range(3)
    ]
    return np.concatenate(channel_features).astype(np.float32, copy=False)


__all__ = ["extract_lbp", "extract_rgb_lbp"]
