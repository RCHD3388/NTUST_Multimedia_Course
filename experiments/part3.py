"""
Experiments for Part 3: Landing on the Pixel Grid.
"""

import os
import time

from renderer.wheel import make_wedge_wheel
from renderer.image_io import save_png
from renderer.raster import draw_line_bresenham
from renderer.paths import make_five_point_star_subpath
from renderer.supersampling import (
    coverage_to_canvas,
    supersample_path,
)
from renderer.transform import (
    has_axis_aligned_edge,
    rotate_path,
)

import matplotlib.pyplot as plt
from renderer.measurement import (
    choose_measurement_row,
    find_shallowest_edge,
)


OUTPUT_DIR = "outputs/part3"


def run_part3_point1():
    """
    Render the rotated five-pointed star using
    supersampling factors 1, 2, 4, and 8.
    """
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    width = 400
    height = 400

    center_x = 200
    center_y = 200

    radius = 200
    rotation_degrees = 5.0

    sampling_factors = [1, 2, 4, 8]

    fill_color = (70, 130, 200)
    background_color = (255, 255, 255)

    # Start with the same five-vertex star used in Part 2.
    star = make_five_point_star_subpath(
        center_x,
        center_y,
        radius,
    )

    # Part 3 uses the same star after a small rotation
    # so that no edge is horizontal or vertical.
    rotated_star = rotate_path(
        [star],
        center_x,
        center_y,
        rotation_degrees,
    )

    axis_aligned = has_axis_aligned_edge(
        rotated_star
    )

    print("Part 3.I - Area Coverage")
    print(
        f"Canvas size: {width} x {height}"
    )
    print(
        f"Star rotation: "
        f"{rotation_degrees} degrees"
    )
    print(
        "Axis-aligned edge present: "
        f"{axis_aligned}"
    )
    print()

    results = {}

    for k in sampling_factors:

        # Timing covers the supersampling computation.
        # Saving the PNG is not included.
        start_time = time.perf_counter()

        coverage = supersample_path(
            rotated_star,
            width,
            height,
            k,
        )

        canvas = coverage_to_canvas(
            coverage,
            fill_color=fill_color,
            background_color=background_color,
        )

        elapsed_time = (
            time.perf_counter()
            - start_time
        )

        filename = os.path.join(
            OUTPUT_DIR,
            f"part3_1_star_k{k}.png",
        )

        save_png(
            canvas,
            filename,
        )

        results[k] = {
            "coverage": coverage,
            "canvas": canvas,
            "render_time": elapsed_time,
            "image": os.path.abspath(filename),
        }

        print(
            f"k={k}: "
            f"{k * k} samples per pixel, "
            f"{elapsed_time:.6f} seconds"
        )

    return {
        "canvas_width": width,
        "canvas_height": height,
        "center": (
            center_x,
            center_y,
        ),
        "radius": radius,
        "rotation_degrees": rotation_degrees,
        "axis_aligned_edge_present": (
            axis_aligned
        ),
        "results": results,
    }

def save_row_plot(
    x_values,
    pixel_values,
    k,
    row_y,
    filename,
):
    """
    Save the measured pixel values along one row.

    The values are plotted directly without applying
    smoothing or interpolation to the measurement data.
    """
    plt.figure(
        figsize=(8, 4.5)
    )

    plt.plot(
        x_values,
        pixel_values,
        marker="o",
        markersize=3,
        linewidth=1,
    )

    plt.xlabel(
        "Pixel x-position along selected row"
    )

    plt.ylabel(
        "Pixel value"
    )

    plt.title(
        f"Pixel values along row y={row_y}, k={k}"
    )

    plt.ylim(
        -0.05,
        1.05,
    )

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        filename,
        dpi=160,
    )

    plt.close()


def make_measurement_guide(
    rotated_star,
    shallowest_edge,
    measurement,
    width,
    height,
):
    """
    Create a guide image showing the edge and row
    used for the pixel-value measurement.
    """
    coverage = supersample_path(
        rotated_star,
        width,
        height,
        1,
    )

    canvas = coverage_to_canvas(
        coverage,
        fill_color=(70, 130, 200),
        background_color=(255, 255, 255),
    )

    edge_start = shallowest_edge["start"]
    edge_end = shallowest_edge["end"]

    row_y = measurement["row_y"]
    x_start = measurement["x_start"]
    x_end = measurement["x_end"]

    # Highlight the shallowest edge.
    draw_line_bresenham(
        canvas,
        int(round(edge_start[0])),
        int(round(edge_start[1])),
        int(round(edge_end[0])),
        int(round(edge_end[1])),
        (220, 0, 0),
    )

    # Show the full selected pixel row.
    draw_line_bresenham(
        canvas,
        0,
        row_y,
        width - 1,
        row_y,
        (0, 170, 0),
    )

    # Highlight only the stretch used in the plots.
    draw_line_bresenham(
        canvas,
        x_start,
        row_y,
        x_end,
        row_y,
        (0, 0, 0),
    )

    filename = os.path.join(
        OUTPUT_DIR,
        "part3_2a_measurement_guide.png",
    )

    save_png(
        canvas,
        filename,
    )

    return os.path.abspath(filename)

def run_part3_point2a():
    """
    Measure pixel values along the shallowest edge
    for k = 1 and k = 8.
    """
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    width = 400
    height = 400

    center_x = 200
    center_y = 200

    radius = 200
    rotation_degrees = 5.0

    # Use exactly the same inverted star geometry
    # and rotation as Point I.
    star = make_five_point_star_subpath(
        center_x,
        center_y,
        radius,
    )

    rotated_star = rotate_path(
        [star],
        center_x,
        center_y,
        rotation_degrees,
    )

    # Only the two sampling factors requested
    # for this measurement are needed here.
    coverage_k1 = supersample_path(
        rotated_star,
        width,
        height,
        1,
    )

    coverage_k8 = supersample_path(
        rotated_star,
        width,
        height,
        8,
    )

    shallowest_edge = find_shallowest_edge(
        rotated_star
    )

    measurement = choose_measurement_row(
        rotated_star,
        shallowest_edge,
        coverage_k1,
        width,
        height,
    )
    
    guide_image = make_measurement_guide(
        rotated_star,
        shallowest_edge,
        measurement,
        width,
        height,
    )

    row_y = measurement["row_y"]
    x_start = measurement["x_start"]
    x_end = measurement["x_end"]

    x_values = list(
        range(
            x_start,
            x_end + 1,
        )
    )

    values_k1 = coverage_k1[row_y][
        x_start:x_end + 1
    ]

    values_k8 = coverage_k8[row_y][
        x_start:x_end + 1
    ]

    k1_filename = os.path.join(
        OUTPUT_DIR,
        "part3_2a_row_k1.png",
    )

    k8_filename = os.path.join(
        OUTPUT_DIR,
        "part3_2a_row_k8.png",
    )

    save_row_plot(
        x_values,
        values_k1,
        1,
        row_y,
        k1_filename,
    )

    save_row_plot(
        x_values,
        values_k8,
        8,
        row_y,
        k8_filename,
    )

    print()
    print("Part 3.II.a - Measure It")

    print(
        "Shallowest edge:"
    )

    print(
        f"  start = "
        f"{shallowest_edge['start']}"
    )

    print(
        f"  end   = "
        f"{shallowest_edge['end']}"
    )

    print(
        "  absolute slope = "
        f"{shallowest_edge['absolute_slope']:.6f}"
    )

    print(
        f"Selected pixel row: "
        f"y={row_y}"
    )

    print(
        "Selected edge crossing: "
        f"x={measurement['crossing_x']:.3f}"
    )

    print(
        "Local plot stretch: "
        f"x={x_start} to x={x_end}"
    )

    print(
        "k=1 distinct pixel values: "
        f"{len(set(values_k1))}"
    )

    print(
        "k=8 distinct pixel values: "
        f"{len(set(values_k8))}"
    )

    return {
        "shallowest_edge": shallowest_edge,
        "measurement": measurement,
        "k1_values": values_k1,
        "k8_values": values_k8,
        "k1_plot": os.path.abspath(
            k1_filename
        ),
        "k8_plot": os.path.abspath(
            k8_filename
        ),
    }

def run_part3_point3():
    """
    Render the radial wedge wheel at k = 1
    and at the largest supersampling factor, k = 8.
    """
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    width = 400
    height = 400

    center_x = 200
    center_y = 200

    # Keep a small margin around the wheel.
    radius = 185

    # The assignment requires at least 40 wedges.
    # Forty-eight wedges are used here.
    wedge_count = 48

    sampling_factors = [1, 8]

    # Black and white make the loss of fine detail
    # near the center easier to observe.
    fill_color = (0, 0, 0)
    background_color = (255, 255, 255)

    wheel = make_wedge_wheel(
        center_x,
        center_y,
        radius,
        wedge_count,
    )

    print()
    print("Part 3.III - Where the Grid Loses")
    print(
        f"Canvas size: {width} x {height}"
    )
    print(
        f"Wheel center: "
        f"({center_x}, {center_y})"
    )
    print(
        f"Wheel radius: {radius}"
    )
    print(
        f"Number of wedges: {wedge_count}"
    )
    print(
        f"Number of sub-paths: {len(wheel)}"
    )

    results = {}

    for k in sampling_factors:
        coverage = supersample_path(
            wheel,
            width,
            height,
            k,
        )

        canvas = coverage_to_canvas(
            coverage,
            fill_color=fill_color,
            background_color=background_color,
        )

        filename = os.path.join(
            OUTPUT_DIR,
            f"part3_3_wheel_k{k}.png",
        )

        save_png(
            canvas,
            filename,
        )

        results[k] = {
            "coverage": coverage,
            "canvas": canvas,
            "image": os.path.abspath(filename),
        }

        print(
            f"k={k}: "
            f"{k * k} samples per output pixel"
        )

    return {
        "canvas_width": width,
        "canvas_height": height,
        "center": (
            center_x,
            center_y,
        ),
        "radius": radius,
        "wedge_count": wedge_count,
        "results": results,
    }

if __name__ == "__main__":
    run_part3_point1()