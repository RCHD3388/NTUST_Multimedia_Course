"""
Geometry for the radial wheel used in Part 3.
"""

import math

from renderer.paths import Path


def make_wedge_wheel(
    center_x: float,
    center_y: float,
    radius: float,
    wedge_count: int,
    start_angle_degrees: float = 0.0,
) -> Path:
    """
    Build a wheel from triangular sub-paths.

    Each wedge and the gap following it have the same
    angular width. Every triangle uses the wheel center
    and two points on the outer circle.
    """
    if wedge_count < 1:
        raise ValueError(
            "The wheel must contain at least one wedge."
        )

    wheel: Path = []

    # One wedge-gap pair occupies an equal part
    # of the full 360-degree circle.
    pair_angle = 360.0 / wedge_count

    # The pair is divided equally between
    # one wedge and one gap.
    wedge_angle = pair_angle / 2.0

    for index in range(wedge_count):
        wedge_start = (
            start_angle_degrees
            + index * pair_angle
        )

        wedge_end = (
            wedge_start
            + wedge_angle
        )

        start_radians = math.radians(
            wedge_start
        )

        end_radians = math.radians(
            wedge_end
        )

        outer_start = (
            center_x
            + radius * math.cos(start_radians),
            center_y
            + radius * math.sin(start_radians),
        )

        outer_end = (
            center_x
            + radius * math.cos(end_radians),
            center_y
            + radius * math.sin(end_radians),
        )

        # Each wedge is one closed triangular sub-path.
        wedge = [
            (center_x, center_y),
            outer_start,
            outer_end,
        ]

        wheel.append(wedge)

    return wheel