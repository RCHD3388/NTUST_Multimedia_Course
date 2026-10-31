"""
Geometry helpers for measuring pixel values along a selected edge.
"""

import math
from typing import Dict, Tuple

from renderer.paths import Path
from renderer.scanline import collect_scanline_crossings


Point = Tuple[float, float]


def find_shallowest_edge(path: Path) -> Dict:
    """
    Find the edge with the smallest absolute slope.

    A smaller absolute slope means that the edge is closer
    to horizontal.
    """
    best_edge = None
    best_slope = float("inf")

    for subpath_index, subpath in enumerate(path):
        point_count = len(subpath)

        for edge_index in range(point_count):
            start = subpath[edge_index]
            end = subpath[
                (edge_index + 1) % point_count
            ]

            dx = end[0] - start[0]
            dy = end[1] - start[1]

            # A vertical edge cannot be the shallowest edge.
            if abs(dx) < 1e-12:
                continue

            slope = abs(dy / dx)

            if slope < best_slope:
                best_slope = slope

                best_edge = {
                    "subpath_index": subpath_index,
                    "edge_index": edge_index,
                    "start": start,
                    "end": end,
                    "absolute_slope": slope,
                }

    if best_edge is None:
        raise RuntimeError(
            "No suitable edge was found."
        )

    return best_edge


def edge_x_at_y(
    start: Point,
    end: Point,
    scan_y: float,
):
    """
    Find where an edge crosses a horizontal pixel row.
    """
    x0, y0 = start
    x1, y1 = end

    dy = y1 - y0

    if abs(dy) < 1e-12:
        return None

    t = (scan_y - y0) / dy

    if t < 0.0 or t > 1.0:
        return None

    return x0 + t * (x1 - x0)


def choose_measurement_row(
    path: Path,
    edge_info: Dict,
    coverage_k1,
    width: int,
    height: int,
    half_width: int = 50,
) -> Dict:
    """
    Choose a pixel row that crosses the shallowest edge
    near one of its ends.

    The selected local stretch must contain both outside
    and inside pixels at k = 1 so that there is a visible
    transition to measure.
    """
    start = edge_info["start"]
    end = edge_info["end"]

    x0, y0 = start
    x1, y1 = end

    # Try positions close to either end of the edge.
    fractions = (
        0.15,
        0.20,
        0.25,
        0.30,
    )

    candidate_positions = []

    for fraction in fractions:
        candidate_positions.append(fraction)
        candidate_positions.append(1.0 - fraction)

    for t in candidate_positions:
        candidate_y = y0 + t * (y1 - y0)
        row_y = int(round(candidate_y))

        if row_y < 0 or row_y >= height:
            continue

        predicted_x = edge_x_at_y(
            start,
            end,
            float(row_y),
        )

        if predicted_x is None:
            continue

        crossings = collect_scanline_crossings(
            path,
            float(row_y),
        )

        if not crossings:
            continue

        crossing_x_values = [
            crossing[0]
            for crossing in crossings
        ]

        # Select the scanline crossing belonging to
        # the shallowest edge.
        target_index = min(
            range(len(crossing_x_values)),
            key=lambda index: abs(
                crossing_x_values[index]
                - predicted_x
            ),
        )

        target_x = crossing_x_values[
            target_index
        ]

        local_start = max(
            0,
            int(math.floor(
                target_x - half_width
            )),
        )

        local_end = min(
            width - 1,
            int(math.ceil(
                target_x + half_width
            )),
        )

        # If another edge crosses the same row,
        # stop the local stretch before reaching it.
        if target_index > 0:
            left_crossing = crossing_x_values[
                target_index - 1
            ]

            midpoint = (
                left_crossing + target_x
            ) / 2.0

            local_start = max(
                local_start,
                int(math.ceil(midpoint)),
            )

        if target_index + 1 < len(
            crossing_x_values
        ):
            right_crossing = crossing_x_values[
                target_index + 1
            ]

            midpoint = (
                target_x + right_crossing
            ) / 2.0

            local_end = min(
                local_end,
                int(math.floor(midpoint)),
            )

        if local_end <= local_start:
            continue

        values = coverage_k1[row_y][
            local_start:local_end + 1
        ]

        has_outside = any(
            value < 0.5
            for value in values
        )

        has_inside = any(
            value >= 0.5
            for value in values
        )

        # Near the correct end of the edge,
        # the row should contain an outside-to-inside
        # or inside-to-outside transition.
        if has_outside and has_inside:
            return {
                "row_y": row_y,
                "crossing_x": target_x,
                "x_start": local_start,
                "x_end": local_end,
                "edge_fraction": t,
            }

    raise RuntimeError(
        "Could not find a suitable row near "
        "either end of the shallowest edge."
    )