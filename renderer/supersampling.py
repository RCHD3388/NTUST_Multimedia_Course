"""
Supersampling functions used for area-coverage rendering.
"""

import math
from typing import List, Tuple

from renderer.paths import Path
from renderer.scanline import collect_scanline_crossings
from renderer.transform import scale_path


Color = Tuple[int, int, int]
CoverageImage = List[List[float]]
BinaryMask = List[bytearray]
Canvas = List[List[Color]]


def render_binary_mask(
    path: Path,
    width: int,
    height: int,
) -> BinaryMask:
    """
    Fill a path using the non-zero winding rule.

    Each pixel in the mask stores:
        0 = outside the path
        1 = inside the path

    The scanline convention is the same one used in Part 2.
    """
    mask = [
        bytearray(width)
        for _ in range(height)
    ]

    for y in range(height):
        scan_y = float(y)

        crossings = collect_scanline_crossings(
            path,
            scan_y,
        )

        if not crossings:
            continue

        winding = 0
        previous_x = 0.0
        crossing_index = 0
        row = mask[y]

        while crossing_index < len(crossings):
            crossing_x = crossings[crossing_index][0]

            # Pixels before this crossing use the winding
            # number accumulated from earlier crossings.
            start_x = max(
                0,
                math.ceil(previous_x),
            )

            end_x = min(
                width,
                math.ceil(crossing_x),
            )

            if winding != 0 and end_x > start_x:
                row[start_x:end_x] = (
                    b"\x01" * (end_x - start_x)
                )

            # More than one edge can cross at the same x.
            # Their signed contributions are applied together.
            while (
                crossing_index < len(crossings)
                and abs(
                    crossings[crossing_index][0]
                    - crossing_x
                ) < 1e-12
            ):
                winding += crossings[
                    crossing_index
                ][1]

                crossing_index += 1

            previous_x = crossing_x

        # This normally remains unused for a closed path,
        # but keeps the scanline handling complete.
        if winding != 0:
            start_x = max(
                0,
                math.ceil(previous_x),
            )

            if start_x < width:
                row[start_x:width] = (
                    b"\x01"
                    * (width - start_x)
                )

    return mask

def downsample_mask(
    high_mask: BinaryMask,
    width: int,
    height: int,
    k: int,
) -> CoverageImage:
    """
    Average each k x k block into one coverage value.

    A coverage of 0.0 means that none of the high-resolution
    samples are inside the shape.

    A coverage of 1.0 means that all of them are inside.
    """
    coverage = [
        [0.0 for _ in range(width)]
        for _ in range(height)
    ]

    samples_per_pixel = k * k

    for y in range(height):
        high_y = y * k

        for x in range(width):
            high_x = x * k
            inside_count = 0

            for offset_y in range(k):
                row = high_mask[
                    high_y + offset_y
                ]

                for offset_x in range(k):
                    inside_count += row[
                        high_x + offset_x
                    ]

            coverage[y][x] = (
                inside_count
                / samples_per_pixel
            )

    return coverage

def supersample_path(
    path: Path,
    width: int,
    height: int,
    k: int,
) -> CoverageImage:
    """
    Render a path at k times the output resolution,
    then average each k x k block back to one pixel.
    """
    if k < 1:
        raise ValueError(
            "Supersampling factor must be at least 1."
        )

    high_width = width * k
    high_height = height * k

    # The geometry and canvas must be enlarged
    # by the same factor.
    high_path = scale_path(
        path,
        k,
    )

    high_mask = render_binary_mask(
        high_path,
        high_width,
        high_height,
    )

    return downsample_mask(
        high_mask,
        width,
        height,
        k,
    )
    
def coverage_to_canvas(
    coverage: CoverageImage,
    fill_color: Color = (70, 130, 200),
    background_color: Color = (255, 255, 255),
) -> Canvas:
    """
    Convert fractional coverage values into RGB pixels.
    """
    height = len(coverage)
    width = len(coverage[0])

    canvas = []

    for y in range(height):
        row = []

        for x in range(width):
            amount = coverage[y][x]

            red = round(
                fill_color[0] * amount
                + background_color[0]
                * (1.0 - amount)
            )

            green = round(
                fill_color[1] * amount
                + background_color[1]
                * (1.0 - amount)
            )

            blue = round(
                fill_color[2] * amount
                + background_color[2]
                * (1.0 - amount)
            )

            row.append(
                (red, green, blue)
            )

        canvas.append(row)

    return canvas