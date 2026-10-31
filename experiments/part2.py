# experiments/part2.py

import os

from renderer.circle_bezier import make_two_circle_subpaths
from renderer.image_io import save_png
from renderer.paths import make_five_point_star_subpath, make_rectangle_subpath
from renderer.raster import draw_path_outline
from renderer.scanline import (
    create_canvas,
    fill_path_nonzero_on_canvas,
    winding_number_at_point,
    fill_path_nonzero,
)


OUTPUT_DIR = "outputs/part2"


def count_color(canvas, color):
    """
    Count pixels that exactly match one color.
    """
    return sum(
        pixel == color
        for row in canvas
        for pixel in row
    )


def run_part2_point1():
    """
    Test the non-zero scanline fill with multiple sub-paths.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    width = 400
    height = 300

    background = (255, 255, 255)
    fill_color = (0, 0, 0)

    rectangle_1 = make_rectangle_subpath(
        40, 50,
        140, 150,
    )

    rectangle_2 = make_rectangle_subpath(
        220, 100,
        320, 200,
    )

    # One path containing two separate closed sub-paths.
    path = [
        rectangle_1,
        rectangle_2,
    ]

    canvas = fill_path_nonzero(
        path,
        width,
        height,
        fill_color,
        background,
    )

    filled_pixels = count_color(canvas, fill_color)

    expected_pixels = (
        (140 - 40) * (150 - 50)
        + (320 - 220) * (200 - 100)
    )

    print("Part 2.1 - Multiple Sub-path Test")
    print("Filled pixels:", filled_pixels)
    print("Expected pixels:", expected_pixels)
    print("Match:", filled_pixels == expected_pixels)

    save_png(
        canvas,
        os.path.join(
            OUTPUT_DIR,
            "part2_1_multiple_subpaths.png",
        ),
    )


def run_part2_point2():
    """
    Render and fill the five-pointed self-intersecting star.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    width = 800
    height = 800

    center_x = 400
    center_y = 400
    radius = 290

    background_color = (255, 255, 255)
    outline_color = (0, 0, 0)
    fill_color = (70, 130, 200)

    # Create the five-vertex self-intersecting star path.
    star_subpath = make_five_point_star_subpath(
        center_x,
        center_y,
        radius,
    )

    path = [star_subpath]

    # Create the pixel array.
    canvas = create_canvas(
        width,
        height,
        background_color,
    )

    # Step 1: rasterize the star outline manually.
    draw_path_outline(
        canvas,
        path,
        outline_color,
    )

    # Save the outline-only result.
    outline_filename = os.path.join(
        OUTPUT_DIR,
        "part2_2_star_outline.png",
    )

    save_png(
        canvas,
        outline_filename,
    )

    # Step 2: fill the star using non-zero winding.
    fill_path_nonzero_on_canvas(
        canvas,
        path,
        fill_color,
        preserve_color=outline_color,
    )

    # Compute the winding number at the star center.
    center_winding = winding_number_at_point(
        path,
        center_x,
        center_y,
    )

    # Save the final filled result.
    filled_filename = os.path.join(
        OUTPUT_DIR,
        "part2_2_star_filled.png",
    )

    save_png(
        canvas,
        filled_filename,
    )

    print("Part 2.2 - Five-Pointed Star")
    print(f"Number of vertices: {len(star_subpath)}")
    print(f"Center winding number: {center_winding}")
    print(f"Outline output: {outline_filename}")
    print(f"Filled output: {filled_filename}")
    
    return {
        "outline_image": os.path.abspath(outline_filename),
        "filled_image": os.path.abspath(filled_filename),
        "center_winding": center_winding,
    }


def render_circle_direction_case(
    path,
    width,
    height,
    center_x,
    center_y,
    output_filename,
):
    """
    Render one two-subpath circle case and return
    the winding number at the center.
    """
    background_color = (255, 255, 255)
    outline_color = (0, 0, 0)
    fill_color = (70, 130, 200)

    canvas = create_canvas(
        width,
        height,
        background_color,
    )

    # Draw both sub-path outlines manually.
    draw_path_outline(
        canvas,
        path,
        outline_color,
    )

    # Fill using the non-zero winding rule.
    fill_path_nonzero_on_canvas(
        canvas,
        path,
        fill_color,
        preserve_color=outline_color,
    )

    center_winding = winding_number_at_point(
        path,
        center_x,
        center_y,
    )

    save_png(
        canvas,
        output_filename,
    )

    return center_winding

def run_part2_point3():
    """
    Render the two-circle path twice.

    Only the traversal direction of the inner
    sub-path changes between the two cases.
    """
    os.makedirs("outputs/part2", exist_ok=True)

    width = 800
    height = 800

    center_x = 400
    center_y = 400

    outer_radius = 290
    inner_radius = 145

    depth = 6

    # Build both circles from four cubic Bezier segments
    # and flatten them using the Part 1 construction.
    outer, inner = make_two_circle_subpaths(
        center_x,
        center_y,
        outer_radius,
        inner_radius,
        depth,
    )

    # Reverse only the traversal order.
    inner_reversed = list(reversed(inner))

    # Verify that no geometric point moved.
    same_points = (
        len(inner) == len(inner_reversed)
        and all(
            original == reversed_point
            for original, reversed_point
            in zip(inner, reversed(inner_reversed))
        )
    )

    if not same_points:
        raise RuntimeError(
            "Inner circle points changed when reversing direction."
        )

    # Case 1: outer and inner use the same direction.
    same_direction_path = [
        outer,
        inner,
    ]

    same_direction_filename = os.path.join(
        "outputs",
        "part2",
        "part2_3_same_direction.png",
    )

    same_direction_winding = render_circle_direction_case(
        same_direction_path,
        width,
        height,
        center_x,
        center_y,
        same_direction_filename,
    )

    # Case 2: only the inner circle direction is reversed.
    opposite_direction_path = [
        outer,
        inner_reversed,
    ]

    opposite_direction_filename = os.path.join(
        "outputs",
        "part2",
        "part2_3_opposite_direction.png",
    )

    opposite_direction_winding = render_circle_direction_case(
        opposite_direction_path,
        width,
        height,
        center_x,
        center_y,
        opposite_direction_filename,
    )

    print("Part 2.3 - Path Direction Test")
    print(f"Outer flattened points: {len(outer)}")
    print(f"Inner flattened points: {len(inner)}")
    print(f"Inner points unchanged: {same_points}")

    print()
    print("Case 1 - Same direction")
    print(
        f"Center winding number: "
        f"{same_direction_winding}"
    )
    print(
        f"Output: "
        f"{same_direction_filename}"
    )

    print()
    print("Case 2 - Inner direction reversed")
    print(
        f"Center winding number: "
        f"{opposite_direction_winding}"
    )
    print(
        f"Output: "
        f"{opposite_direction_filename}"
    )
    
    return {
        "same_direction_image": os.path.abspath(
            same_direction_filename
        ),
        "opposite_direction_image": os.path.abspath(
            opposite_direction_filename
        ),
        "same_direction_winding": same_direction_winding,
        "opposite_direction_winding": opposite_direction_winding,
        "points_unchanged": same_points,
    }
    