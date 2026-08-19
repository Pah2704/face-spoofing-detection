"""Deterministic, dependency-free frame sampling utilities."""

from __future__ import annotations


def uniform_frame_indices(
    total_frames: int,
    frames_per_video: int = 10,
) -> list[int]:
    """Return evenly spaced frame indices, including both video endpoints.

    The calculation uses integer arithmetic so repeated runs and platforms
    produce identical indices.  A video must contain at least as many frames
    as requested; silently returning duplicate indices would otherwise give
    some frames more weight than others.

    Args:
        total_frames: Number of frames in the video.
        frames_per_video: Number of unique indices to return.  This must be at
            least two so the first and last frames can both be represented.

    Raises:
        TypeError: If either argument is not an integer.
        ValueError: If an argument is outside its valid range or the video is
            too short for the requested sample count.
    """

    if isinstance(total_frames, bool) or not isinstance(total_frames, int):
        raise TypeError(
            "total_frames must be an integer, "
            f"got {type(total_frames).__name__}"
        )
    if isinstance(frames_per_video, bool) or not isinstance(
        frames_per_video, int
    ):
        raise TypeError(
            "frames_per_video must be an integer, "
            f"got {type(frames_per_video).__name__}"
        )
    if total_frames <= 0:
        raise ValueError(
            f"total_frames must be positive, got {total_frames}"
        )
    if frames_per_video < 2:
        raise ValueError(
            "frames_per_video must be at least 2 to include the first "
            f"and last frames, got {frames_per_video}"
        )
    if total_frames < frames_per_video:
        raise ValueError(
            f"video is too short: it has {total_frames} frames but "
            f"{frames_per_video} unique frames were requested"
        )

    final_index = total_frames - 1
    intervals = frames_per_video - 1

    # Nearest-integer positions on [0, final_index].  Adding half of the
    # denominator implements deterministic half-up rounding without floats.
    return [
        (sample_number * final_index + intervals // 2) // intervals
        for sample_number in range(frames_per_video)
    ]


__all__ = ["uniform_frame_indices"]
