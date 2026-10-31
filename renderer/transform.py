# renderer/transform.py

"""
Geometric transformations for paths.
"""

import math

from renderer.paths import Path


def rotate_path(
    path: Path,
    center_x: float,
    center_y: float,
    angle_degrees: float,
) -> Path:
    """
    Rotate every point in a path around one center.
    """
    angle = math.radians(angle_degrees)

    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)

    rotated_path: Path = []

    for subpath in path:
        rotated_subpath = []

        for x, y in subpath:
            dx = x - center_x
            dy = y - center_y

            rotated_x = (
                center_x
                + dx * cos_angle
                - dy * sin_angle
            )

            rotated_y = (
                center_y
                + dx * sin_angle
                + dy * cos_angle
            )

            rotated_subpath.append(
                (rotated_x, rotated_y)
            )

        rotated_path.append(rotated_subpath)

    return rotated_path


def scale_path(
    path: Path,
    scale: int,
) -> Path:
    """
    Scale all path coordinates by one factor.
    """
    scaled_path: Path = []

    for subpath in path:
        scaled_subpath = [
            (x * scale, y * scale)
            for x, y in subpath
        ]

        scaled_path.append(scaled_subpath)

    return scaled_path


def has_axis_aligned_edge(
    path: Path,
    tolerance: float = 1e-9,
) -> bool:
    """
    Check whether any closed-path edge is exactly
    horizontal or vertical.
    """
    for subpath in path:
        point_count = len(subpath)

        for index in range(point_count):
            x0, y0 = subpath[index]
            x1, y1 = subpath[
                (index + 1) % point_count
            ]

            horizontal = abs(y1 - y0) < tolerance
            vertical = abs(x1 - x0) < tolerance

            if horizontal or vertical:
                return True

    return False