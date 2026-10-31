# renderer/raster.py

"""
Manual rasterization helpers for Part 2.

This file draws path outlines onto a pixel array
without using any drawing-library line function.
"""

from typing import Tuple

from renderer.paths import Path, build_all_edges
from renderer.scanline import Canvas

Color = Tuple[int, int, int]


def put_pixel(
    canvas: Canvas,
    x: int,
    y: int,
    color: Color,
) -> None:
    """
    Set one pixel if it lies inside the canvas.
    """
    height = len(canvas)
    width = len(canvas[0])

    if 0 <= x < width and 0 <= y < height:
        canvas[y][x] = color


def draw_line_bresenham(
    canvas: Canvas,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: Color,
) -> None:
    """
    Draw one line using Bresenham's line algorithm.
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    step_x = 1 if x0 < x1 else -1
    step_y = 1 if y0 < y1 else -1

    error = dx - dy

    while True:
        put_pixel(canvas, x0, y0, color)

        if x0 == x1 and y0 == y1:
            break

        double_error = 2 * error

        if double_error > -dy:
            error -= dy
            x0 += step_x

        if double_error < dx:
            error += dx
            y0 += step_y


def draw_path_outline(
    canvas: Canvas,
    path: Path,
    color: Color,
) -> None:
    """
    Draw all edges of a path onto the canvas.
    """
    for start, end in build_all_edges(path):
        x0 = round(start[0])
        y0 = round(start[1])
        x1 = round(end[0])
        y1 = round(end[1])

        draw_line_bresenham(
            canvas,
            x0,
            y0,
            x1,
            y1,
            color,
        )