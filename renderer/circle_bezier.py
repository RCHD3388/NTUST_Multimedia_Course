# renderer/circle_bezier.py

"""
Build a circle from four cubic Bezier segments
and flatten it using the Part 1 midpoint construction.
"""

from typing import List, Tuple

from renderer.bezier import midpoint_polyline

Point = Tuple[float, float]
BezierSegment = Tuple[Point, Point, Point, Point]
SubPath = List[Point]


def make_circle_bezier_segments(
    center_x: float,
    center_y: float,
    radius: float,
) -> List[BezierSegment]:
    """
    Create one clockwise circle using four cubic Bezier segments.

    Each tangent control point is 0.5523 * radius
    from its corresponding endpoint.
    """
    k = 0.5523 * radius

    top = (center_x, center_y - radius)
    right = (center_x + radius, center_y)
    bottom = (center_x, center_y + radius)
    left = (center_x - radius, center_y)

    segments: List[BezierSegment] = [
        # Top -> Right
        (
            top,
            (center_x + k, center_y - radius),
            (center_x + radius, center_y - k),
            right,
        ),

        # Right -> Bottom
        (
            right,
            (center_x + radius, center_y + k),
            (center_x + k, center_y + radius),
            bottom,
        ),

        # Bottom -> Left
        (
            bottom,
            (center_x - k, center_y + radius),
            (center_x - radius, center_y + k),
            left,
        ),

        # Left -> Top
        (
            left,
            (center_x - radius, center_y - k),
            (center_x - k, center_y - radius),
            top,
        ),
    ]

    return segments

def flatten_circle(
    center_x: float,
    center_y: float,
    radius: float,
    depth: int,
) -> SubPath:
    """
    Flatten all four Bezier segments using
    the Part 1 midpoint subdivision construction.
    """
    segments = make_circle_bezier_segments(
        center_x,
        center_y,
        radius,
    )

    flattened: SubPath = []

    for segment_index, segment in enumerate(segments):
        p0, p1, p2, p3 = segment

        polyline = midpoint_polyline(
            p0,
            p1,
            p2,
            p3,
            depth,
        )

        # Convert Part 1 NumPy points into standard tuples.
        polyline_points = [
            (float(point[0]), float(point[1]))
            for point in polyline
        ]

        if segment_index == 0:
            flattened.extend(polyline_points)
        else:
            # Skip the duplicated segment joint.
            flattened.extend(polyline_points[1:])

    # The final endpoint repeats the first point.
    # Closing is handled automatically by the path system.
    flattened.pop()

    return flattened

def make_two_circle_subpaths(
    center_x: float,
    center_y: float,
    outer_radius: float,
    inner_radius: float,
    depth: int,
) -> Tuple[SubPath, SubPath]:
    """
    Build the outer and inner circle sub-paths.
    Both initially use the same traversal direction.
    """
    outer = flatten_circle(
        center_x,
        center_y,
        outer_radius,
        depth,
    )

    inner = flatten_circle(
        center_x,
        center_y,
        inner_radius,
        depth,
    )

    return outer, inner