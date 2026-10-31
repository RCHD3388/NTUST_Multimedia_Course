# renderer/paths.py

"""
Basic path helpers for Part 2.

A path is represented as a list of sub-paths.
Each sub-path is a list of 2D points: [(x0, y0), (x1, y1), ...].

The last point is connected back to the first point automatically.
"""

import math
from typing import List, Tuple

Point = Tuple[float, float]
SubPath = List[Point]
Path = List[SubPath]


def build_closed_edges(subpath: SubPath) -> List[Tuple[Point, Point]]:
    """
    Build edges for one closed sub-path.

    The sub-path must contain at least 3 points.
    Each consecutive pair forms an edge, and the last point
    is connected back to the first point.
    """
    if len(subpath) < 3:
        raise ValueError("A closed sub-path must contain at least 3 points.")

    edges: List[Tuple[Point, Point]] = []

    for index in range(len(subpath)):
        start = subpath[index]
        end = subpath[(index + 1) % len(subpath)]
        edges.append((start, end))

    return edges


def build_all_edges(path: Path) -> List[Tuple[Point, Point]]:
    """
    Build a flat list of edges from all sub-paths in a path.
    """
    all_edges: List[Tuple[Point, Point]] = []

    for subpath in path:
        all_edges.extend(build_closed_edges(subpath))

    return all_edges


def make_rectangle_subpath(
    x_min: float,
    y_min: float,
    x_max: float,
    y_max: float,
) -> SubPath:
    """
    Create a simple rectangle sub-path in clockwise order.
    """
    return [
        (x_min, y_min),
        (x_max, y_min),
        (x_max, y_max),
        (x_min, y_max),
    ]

def make_five_point_star_subpath(
    center_x: float,
    center_y: float,
    radius: float,
) -> SubPath:
    """
    Create the five-pointed star in the same orientation
    as Figure 2 of the assignment.

    Visiting order:
    P0 bottom
    P1 upper-right
    P2 lower-left
    P3 lower-right
    P4 upper-left
    """
    geometric_vertices: List[Point] = []

    # Five outer vertices around the circle.
    for index in range(5):
        angle = math.radians(90 + index * 72)

        x = round(
            center_x + radius * math.cos(angle)
        )
        y = round(
            center_y + radius * math.sin(angle)
        )

        geometric_vertices.append((x, y))

    # Every-other-one traversal matching Figure 2.
    visiting_order = [0, 3, 1, 4, 2]

    return [
        geometric_vertices[index]
        for index in visiting_order
    ]