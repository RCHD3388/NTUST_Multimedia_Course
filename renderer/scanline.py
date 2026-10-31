# renderer/scanline.py

"""
Manual scanline fill using the non-zero winding number rule.
No drawing or built-in fill functions are used.
"""

from typing import List, Optional, Tuple

from renderer.paths import Path, Point, build_all_edges

Color = Tuple[int, int, int]
Edge = Tuple[Point, Point]
Crossing = Tuple[float, int]
Canvas = List[List[Color]]


def edge_scanline_crossing(
    start: Point,
    end: Point,
    scan_y: float,
) -> Optional[Crossing]:
    """
    Find where one edge crosses a horizontal scanline.

    Winding convention:
    - top to bottom -> +1
    - bottom to top -> -1
    """
    x0, y0 = start
    x1, y1 = end

    # Horizontal edges do not cross the scanline vertically.
    if y0 == y1:
        return None

    min_y = min(y0, y1)
    max_y = max(y0, y1)

    # Count each shared vertex only once.
    if not (min_y <= scan_y < max_y):
        return None

    # Linear interpolation gives the x-coordinate of the crossing.
    t = (scan_y - y0) / (y1 - y0)
    crossing_x = x0 + t * (x1 - x0)

    winding_delta = 1 if y1 > y0 else -1

    return crossing_x, winding_delta


def collect_edge_crossings(
    edges: List[Edge],
    scan_y: float,
) -> List[Crossing]:
    """
    Collect and sort all crossings for one scanline.
    """
    crossings: List[Crossing] = []

    for start, end in edges:
        crossing = edge_scanline_crossing(start, end, scan_y)

        if crossing is not None:
            crossings.append(crossing)

    crossings.sort(key=lambda item: item[0])
    return crossings


def collect_scanline_crossings(
    path: Path,
    scan_y: float,
) -> List[Crossing]:
    """
    Collect crossings from all sub-paths.
    """
    return collect_edge_crossings(
        build_all_edges(path),
        scan_y,
    )


def create_canvas(
    width: int,
    height: int,
    background: Color = (255, 255, 255),
) -> Canvas:
    """
    Create a pixel array filled with one background color.
    """
    return [
        [background for _ in range(width)]
        for _ in range(height)
    ]


def fill_path_nonzero(
    path: Path,
    width: int,
    height: int,
    fill_color: Color = (0, 0, 0),
    background: Color = (255, 255, 255),
) -> Canvas:
    """
    Fill a path row by row using the non-zero winding rule.
    """
    canvas = create_canvas(width, height, background)

    # Build the edges once and reuse them for every row.
    edges = build_all_edges(path)

    for y in range(height):
        # Test through the center of this pixel row.
        scan_y = float(y)
        crossings = collect_edge_crossings(edges, scan_y)

        winding = 0
        crossing_index = 0

        for x in range(width):
            # Test the center of the current pixel.
            pixel_x = float(x)

            # Apply every crossing passed before this pixel center.
            while (
                crossing_index < len(crossings)
                and crossings[crossing_index][0] <= pixel_x
            ):
                winding += crossings[crossing_index][1]
                crossing_index += 1

            # Non-zero winding means the pixel is inside.
            if winding != 0:
                canvas[y][x] = fill_color

    return canvas

def winding_number_at_point(
    path: Path,
    x: float,
    y: float,
) -> int:
    """
    Compute the winding number at one point.

    The winding convention is the same as the scanline fill:
    - top to bottom -> +1
    - bottom to top -> -1
    """
    edges = build_all_edges(path)
    crossings = collect_edge_crossings(edges, y)

    winding = 0

    # Start from the far left and move toward the tested point.
    for crossing_x, winding_delta in crossings:
        if crossing_x <= x:
            winding += winding_delta
        else:
            break

    return winding


def fill_path_nonzero_on_canvas(
    canvas: Canvas,
    path: Path,
    fill_color: Color,
    preserve_color: Optional[Color] = None,
) -> Canvas:
    """
    Fill an existing canvas using the non-zero winding rule.

    Pixels with preserve_color are not overwritten.
    """
    height = len(canvas)
    width = len(canvas[0])

    edges = build_all_edges(path)

    for y in range(height):
        # Match the integer coordinates used by Bresenham.
        scan_y = float(y)
        crossings = collect_edge_crossings(edges, scan_y)

        winding = 0
        crossing_index = 0

        for x in range(width):
            pixel_x = float(x)

            while (
                crossing_index < len(crossings)
                and crossings[crossing_index][0] <= pixel_x
            ):
                winding += crossings[crossing_index][1]
                crossing_index += 1

            if winding != 0:
                if (
                    preserve_color is None
                    or canvas[y][x] != preserve_color
                ):
                    canvas[y][x] = fill_color

    return canvas