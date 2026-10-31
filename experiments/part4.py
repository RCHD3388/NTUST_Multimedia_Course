import os

from PIL import Image

from renderer.circle_bezier import (
    make_circle_bezier_segments,
    flatten_circle,
)
from renderer.supersampling import render_binary_mask
from renderer.compositing import (
    composite_mask,
    find_changed_pixels,
)


OUTPUT_DIR = os.path.join("outputs", "part4")


def make_solid_canvas(width, height, color):
    """Create a canvas filled with one fixed RGB background color."""
    return [
        [color for _ in range(width)]
        for _ in range(height)
    ]


def save_canvas(canvas, filename):
    """
    Save an already-computed RGB pixel canvas.
    Pillow is used only for writing the pixel array to a PNG file.
    """
    height = len(canvas)
    width = len(canvas[0])

    image = Image.new("RGB", (width, height))

    pixels = [
        pixel
        for row in canvas
        for pixel in row
    ]

    image.putdata(pixels)
    image.save(filename)


def make_changed_pixel_image(width, height, changed_pixels):
    """
    Visualize exactly which pixels changed.
    Changed pixels are black and unchanged pixels are white.
    """
    canvas = make_solid_canvas(
        width,
        height,
        (255, 255, 255),
    )

    for x, y in changed_pixels:
        canvas[y][x] = (0, 0, 0)

    return canvas


def rgb_distance(color_a, color_b):
    """
    Measure the distance between two RGB colors.
    """
    total = 0.0

    for channel in range(3):
        difference = color_a[channel] - color_b[channel]
        total += difference * difference

    return total ** 0.5


def color_change_percentage(
    background_color,
    current_color,
    foreground_color,
):
    """
    Measure how far the current RGB value has moved from
    the original background toward the fully opaque foreground.

    0% means the original background color.
    100% means the fully opaque foreground color.
    """
    full_distance = rgb_distance(
        background_color,
        foreground_color,
    )

    if full_distance == 0:
        return 0.0

    current_distance = rgb_distance(
        background_color,
        current_color,
    )

    return (
        current_distance
        / full_distance
        * 100.0
    )


def run_part4_pointA():
    """
    Measure how different opacity values affect one foreground
    shape placed over a fixed background.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    width = 400
    height = 400

    center_x = 200.0
    center_y = 200.0
    radius = 150.0

    background_color = (255, 255, 255)
    foreground_color = (0, 100, 220)

    opacity_values = [
        0.00,
        0.25,
        0.50,
        0.75,
        1.00,
    ]

    # Use exactly the same circle construction as Part 2:
    # four cubic Bézier segments followed by midpoint subdivision.
    circle_subpath = flatten_circle(
        center_x,
        center_y,
        radius,
        6,
    )

    # The Part 2 non-zero winding fill is reused to determine
    # exactly which output pixels belong to the circle.
    circle_mask = render_binary_mask(
        [circle_subpath],
        width,
        height,
    )

    background = make_solid_canvas(
        width,
        height,
        background_color,
    )

    save_canvas(
        background,
        os.path.join(
            OUTPUT_DIR,
            "part4_a_background.png",
        ),
    )

    # Representative pixels are deliberately chosen well inside
    # the circle so their RGB values are not affected by the boundary.
    representative_pixels = [
        ("center", 200, 200),
    ]

    print()
    print("Part 4.A - Effect of Opacity on Pixel Changes")
    print(f"Canvas size: {width} x {height}")
    print(f"Circle center: ({center_x}, {center_y})")
    print(f"Circle radius: {radius}")
    print(f"Background RGB: {background_color}")
    print(f"Foreground RGB: {foreground_color}")

    table_results = []

    for opacity in opacity_values:
        result = composite_mask(
            background,
            circle_mask,
            foreground_color,
            opacity,
        )

        changed_pixels = find_changed_pixels(
            background,
            result,
        )

        center_rgb = result[200][200]
        
        change_percentage = color_change_percentage(
            background_color,
            center_rgb,
            foreground_color,
        )

        table_results.append({
            "opacity": opacity,
            "changed_pixels": len(changed_pixels),
            "center_rgb": center_rgb,
            "color_change_percentage": change_percentage,
        })

        label = str(opacity).replace(".", "_")

        result_filename = os.path.join(
            OUTPUT_DIR,
            f"part4_a_opacity_{label}.png",
        )

        save_canvas(
            result,
            result_filename,
        )

        changed_image = make_changed_pixel_image(
            width,
            height,
            changed_pixels,
        )

        changed_filename = os.path.join(
            OUTPUT_DIR,
            f"part4_a_changed_pixels_{label}.png",
        )

        save_canvas(
            changed_image,
            changed_filename,
        )

        print()
        print(f"Opacity: {opacity:.2f}")
        print(
            f"Changed pixels: {len(changed_pixels)}"
        )

        for name, x, y in representative_pixels:
            print(
                f"{name}: "
                f"({x}, {y}) -> {result[y][x]}"
            )


    print()
    print("Opacity Measurement Summary")
    print("-" * 82)
    print(
        f"{'Opacity':>10} "
        f"{'Changed Pixels':>18} "
        f"{'Center RGB':>22}"
        f"{'Color Change (%)':>20}"
    )
    print("-" * 82)

    for row in table_results:
        print(
            f"{row['opacity']:>10.2f} "
            f"{row['changed_pixels']:>18} "
            f"{str(row['center_rgb']):>22}"
            f"{row['color_change_percentage']:>19.2f}%"
        )

    print("-" * 82)
    print()
    print("Part 4.A completed.")
    
def run_part4_pointB():
    """
    Measure how opacity accumulates when the same partially
    transparent circle is composited repeatedly at the same position.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    width = 400
    height = 400

    center_x = 200.0
    center_y = 200.0
    radius = 150.0

    background_color = (255, 255, 255)
    foreground_color = (0, 100, 220)

    fixed_opacity = 0.50
    layer_counts = [1, 2, 4, 8]

    # Use the same circle construction as Part 2.
    circle_subpath = flatten_circle(
        center_x,
        center_y,
        radius,
        6,
    )

    # Reuse the non-zero winding fill.
    circle_mask = render_binary_mask(
        [circle_subpath],
        width,
        height,
    )

    background = make_solid_canvas(
        width,
        height,
        background_color,
    )

    table_results = []

    print()
    print("Part 4.B - Opacity Accumulation")
    print(f"Canvas size: {width} x {height}")
    print(f"Circle center: ({center_x}, {center_y})")
    print(f"Circle radius: {radius}")
    print(f"Fixed opacity per layer: {fixed_opacity:.2f}")
    print(f"Background RGB: {background_color}")
    print(f"Foreground RGB: {foreground_color}")

    for layer_count in layer_counts:
        # Start every experiment from the same background.
        result = [
            row.copy()
            for row in background
        ]

        # Composite the same circle repeatedly at the same position.
        for _ in range(layer_count):
            result = composite_mask(
                result,
                circle_mask,
                foreground_color,
                fixed_opacity,
            )

        center_rgb = result[200][200]

        effective_opacity = (
            color_change_percentage(
                background_color,
                center_rgb,
                foreground_color,
            )
            / 100.0
        )

        table_results.append({
            "layers": layer_count,
            "center_rgb": center_rgb,
            "effective_opacity": effective_opacity,
        })

        filename = os.path.join(
            OUTPUT_DIR,
            f"part4_b_layers_{layer_count}.png",
        )

        save_canvas(
            result,
            filename,
        )

    print()
    print("Opacity Accumulation Summary")
    print("-" * 62)
    print(
        f"{'Layers':>8} "
        f"{'Center RGB':>22} "
        f"{'Effective Opacity (%)':>26}"
    )
    print("-" * 62)

    for row in table_results:
        print(
            f"{row['layers']:>8} "
            f"{str(row['center_rgb']):>22} "
            f"{row['effective_opacity'] * 100:>25.2f}%"
        )

    print("-" * 62)

    return table_results

def compare_pixel_colors(first, second):
    """
    Compare two rendered canvases pixel by pixel.

    The returned image is black where the final RGB colors differ
    and white where the two results are identical.
    """
    height = len(first)
    width = len(first[0])

    difference_image = make_solid_canvas(
        width,
        height,
        (255, 255, 255),
    )

    different_pixel_count = 0

    for y in range(height):
        for x in range(width):
            if first[y][x] != second[y][x]:
                difference_image[y][x] = (0, 0, 0)
                different_pixel_count += 1

    return difference_image, different_pixel_count

def run_part4_pointC():
    """
    Compare two overlapping transparent shapes when only
    their layer order is changed.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    width = 400
    height = 400

    background_color = (255, 255, 255)

    # Two different foreground colors.
    color_a = (220, 70, 70)
    color_b = (50, 120, 220)

    # Both shapes use exactly the same opacity.
    opacity = 0.50

    # The two circles have the same size but different positions,
    # producing a clear overlap around the center of the canvas.
    radius = 120.0

    center_a = (140.0, 200.0)
    center_b = (260.0, 200.0)

    # Use the same circle construction as Part 2:
    # four cubic Bezier segments flattened by midpoint subdivision.
    circle_a = flatten_circle(
        center_a[0],
        center_a[1],
        radius,
        6,
    )

    circle_b = flatten_circle(
        center_b[0],
        center_b[1],
        radius,
        6,
    )

    # Reuse the non-zero winding fill to determine the pixels
    # covered by each circle.
    mask_a = render_binary_mask(
        [circle_a],
        width,
        height,
    )

    mask_b = render_binary_mask(
        [circle_b],
        width,
        height,
    )

    background = make_solid_canvas(
        width,
        height,
        background_color,
    )

    # ---------------------------------------------------------
    # Shape A over Shape B
    #
    # B must be composited first because A is the upper layer.
    # ---------------------------------------------------------
    a_over_b = composite_mask(
        background,
        mask_b,
        color_b,
        opacity,
    )

    a_over_b = composite_mask(
        a_over_b,
        mask_a,
        color_a,
        opacity,
    )

    # ---------------------------------------------------------
    # Shape B over Shape A
    #
    # A is composited first because B is now the upper layer.
    # ---------------------------------------------------------
    b_over_a = composite_mask(
        background,
        mask_a,
        color_a,
        opacity,
    )

    b_over_a = composite_mask(
        b_over_a,
        mask_b,
        color_b,
        opacity,
    )

    save_canvas(
        a_over_b,
        os.path.join(
            OUTPUT_DIR,
            "part4_c_a_over_b.png",
        ),
    )

    save_canvas(
        b_over_a,
        os.path.join(
            OUTPUT_DIR,
            "part4_c_b_over_a.png",
        ),
    )

    # Compare the two final images pixel by pixel.
    difference_image, different_pixel_count = (
        compare_pixel_colors(
            a_over_b,
            b_over_a,
        )
    )

    save_canvas(
        difference_image,
        os.path.join(
            OUTPUT_DIR,
            "part4_c_order_difference.png",
        ),
    )

    # Count the pixels geometrically covered by both shapes.
    overlap_pixel_count = 0

    for y in range(height):
        for x in range(width):
            if mask_a[y][x] and mask_b[y][x]:
                overlap_pixel_count += 1

    # The canvas center lies inside the overlap, so it is used
    # as a representative pixel for comparing the final colors.
    sample_x = 200
    sample_y = 200

    rgb_a_over_b = a_over_b[sample_y][sample_x]
    rgb_b_over_a = b_over_a[sample_y][sample_x]

    print()
    print("Part 4.C - Effect of Layer Order")
    print(f"Canvas size: {width} x {height}")
    print(f"Shape A center: {center_a}")
    print(f"Shape B center: {center_b}")
    print(f"Circle radius: {radius}")
    print(f"Shape A RGB: {color_a}")
    print(f"Shape B RGB: {color_b}")
    print(f"Opacity: {opacity:.2f}")

    print()
    print("Layer Order Comparison")
    print("-" * 60)
    print(f"Overlap pixels: {overlap_pixel_count}")
    print(
        f"Pixels changed by layer order: "
        f"{different_pixel_count}"
    )

    print()
    print(
        f"Overlap pixel ({sample_x}, {sample_y})"
    )
    print(
        f"A over B RGB: {rgb_a_over_b}"
    )
    print(
        f"B over A RGB: {rgb_b_over_a}"
    )

    print()
    print(
        "Layer order changes final color:",
        rgb_a_over_b != rgb_b_over_a,
    )

    return {
        "overlap_pixels": overlap_pixel_count,
        "different_pixels": different_pixel_count,
        "a_over_b_rgb": rgb_a_over_b,
        "b_over_a_rgb": rgb_b_over_a,
    }