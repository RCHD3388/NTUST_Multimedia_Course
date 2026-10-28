from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from renderer.bezier import (
    midpoint_polyline,
    sample_bezier_formula,
    sample_bezier_by_max_spacing,
)

from renderer.geometry import (
    max_curve_to_polyline_error,
)


# ============================================================
# Shared configuration for Part 1
# ============================================================

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Four control points shared by Part 1 Point 1 and Point 2.
# B0 and B3 are the lower endpoints.
# B1 and B2 are the upper direction/control points.
B0 = np.array([80.0, 80.0])
B1 = np.array([150.0, 500.0])
B2 = np.array([650.0, 500.0])
B3 = np.array([720.0, 80.0])

OUTPUT_DIRECTORY = Path("outputs/part1")


# ============================================================
# Part 1 - Point 1
# Two Roads to the Same Curve
# ============================================================

POINT1_SUBDIVISION_DEPTH = 2


def run_part1_point1():
    """
    Run Part 1 Point 1.

    Compare:
    1. The cubic Bezier formula.
    2. Recursive midpoint subdivision.

    Both constructions are shown in one overlaid figure at a
    shallow subdivision depth so that their difference remains
    clearly visible.
    """

    print("\n" + "=" * 70)
    print("PART 1 - POINT 1")
    print("=" * 70)

    # Method A:
    # Sample the cubic Bezier curve using our own formula.
    formula_points = sample_bezier_formula(
        B0,
        B1,
        B2,
        B3,
        num_samples=1000,
    )

    # Method B:
    # Approximate the same curve using midpoint subdivision.
    subdivision_points = midpoint_polyline(
        B0,
        B1,
        B2,
        B3,
        depth=POINT1_SUBDIVISION_DEPTH,
    )

    control_points = np.array([B0, B1, B2, B3])

    fig, ax = plt.subplots(figsize=(10, 7.5))

    # Show the control polygon.
    ax.plot(
        control_points[:, 0],
        control_points[:, 1],
        "--",
        marker="o",
        label="Control polygon",
    )

    # Show Method A.
    ax.plot(
        formula_points[:, 0],
        formula_points[:, 1],
        linewidth=2,
        label="Method A: Cubic formula",
    )

    # Show Method B.
    ax.plot(
        subdivision_points[:, 0],
        subdivision_points[:, 1],
        marker="o",
        linewidth=2,
        label=(
            "Method B: Midpoint subdivision "
            f"(depth={POINT1_SUBDIVISION_DEPTH})"
        ),
    )

    # Label the four Bezier control points.
    for index, point in enumerate(control_points):
        ax.annotate(
            f"B{index}",
            (point[0], point[1]),
            xytext=(8, 8),
            textcoords="offset points",
        )

    ax.set_xlim(0, CANVAS_WIDTH)
    ax.set_ylim(0, CANVAS_HEIGHT)
    ax.set_aspect("equal", adjustable="box")

    ax.set_title(
        "Part 1.1 - Cubic Formula vs. Midpoint Subdivision"
    )
    ax.set_xlabel("x coordinate (pixels)")
    ax.set_ylabel("y coordinate (pixels)")
    ax.grid(True)
    ax.legend()

    output_path = (
        OUTPUT_DIRECTORY
        / "part1_1_overlay.png"
    )

    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        f"Subdivision depth : "
        f"{POINT1_SUBDIVISION_DEPTH}"
    )
    print(
        f"Formula samples   : "
        f"{len(formula_points)}"
    )
    print(
        f"Polyline vertices : "
        f"{len(subdivision_points)}"
    )
    print(
        f"Figure saved to   : "
        f"{output_path}"
    )


# ============================================================
# Part 1 - Point 2
# Convergence
# ============================================================

MAX_FORMULA_SAMPLE_SPACING = 0.1
ERROR_THRESHOLD = 0.5

# Use depth 2 again for the visual gap illustration.
POINT2_OVERLAY_DEPTH = 2

# Continue for two additional depths after the error first
# becomes smaller than 0.5 px. This gives enough data to inspect
# the deeper convergence pattern.
EXTRA_DEPTHS_AFTER_THRESHOLD = 2

MAX_SEARCH_DEPTH = 15


def run_part1_point2():
    """
    Run Part 1 Point 2.

    Measure the directed gap from the formula curve to the nearest
    segment of the midpoint-subdivision polyline for increasing
    subdivision depths.
    """

    print("\n" + "=" * 70)
    print("PART 1 - POINT 2: CONVERGENCE")
    print("=" * 70)

    # --------------------------------------------------------
    # Sample Method A densely enough to satisfy the assignment.
    # --------------------------------------------------------

    (
        formula_points,
        t_values,
        actual_max_spacing,
    ) = sample_bezier_by_max_spacing(
        B0,
        B1,
        B2,
        B3,
        max_spacing=MAX_FORMULA_SAMPLE_SPACING,
    )

    print("\nFormula-curve sampling")
    print("----------------------")

    print(
        f"Number of formula samples  : "
        f"{len(formula_points)}"
    )

    print(
        f"Maximum consecutive spacing: "
        f"{actual_max_spacing:.6f} px"
    )

    print(
        f"Required spacing            : "
        f"< {MAX_FORMULA_SAMPLE_SPACING:.1f} px"
    )

    if actual_max_spacing >= MAX_FORMULA_SAMPLE_SPACING:
        raise RuntimeError(
            "Formula sampling does not satisfy "
            "the < 0.1 px requirement."
        )

    # --------------------------------------------------------
    # Measure convergence at increasing subdivision depths.
    # --------------------------------------------------------

    results = []

    first_below_threshold = None
    previous_error = None

    depth = 0

    while depth <= MAX_SEARCH_DEPTH:

        polyline_points = midpoint_polyline(
            B0,
            B1,
            B2,
            B3,
            depth=depth,
        )

        (
            max_error,
            worst_curve_point,
            nearest_point,
        ) = max_curve_to_polyline_error(
            formula_points,
            polyline_points,
        )

        if previous_error is None:
            reduction_factor = None
        else:
            reduction_factor = (
                previous_error / max_error
            )

        results.append({
            "depth": depth,
            "vertices": len(polyline_points),
            "segments": len(polyline_points) - 1,
            "max_error": max_error,
            "reduction_factor": reduction_factor,
        })

        # Record the first depth whose error is below 0.5 px.
        if (
            first_below_threshold is None
            and max_error < ERROR_THRESHOLD
        ):
            first_below_threshold = depth

        previous_error = max_error

        # Collect a few deeper measurements after reaching
        # the required threshold.
        if (
            first_below_threshold is not None
            and depth >= first_below_threshold + EXTRA_DEPTHS_AFTER_THRESHOLD
        ):
            break

        depth += 1

    if first_below_threshold is None:
        raise RuntimeError(
            "Error did not fall below 0.5 px."
        )

    # --------------------------------------------------------
    # Print convergence table.
    # --------------------------------------------------------

    print("\nConvergence results")
    print("-------------------")

    print(
        f"{'Depth':>5} "
        f"{'Segments':>10} "
        f"{'Max Error (px)':>16} "
        f"{'Reduction':>12}"
    )

    for result in results:

        if result["reduction_factor"] is None:
            reduction_text = "-"
        else:
            reduction_text = (
                f"{result['reduction_factor']:.6f}"
            )

        print(
            f"{result['depth']:>5} "
            f"{result['segments']:>10} "
            f"{result['max_error']:>16.6f} "
            f"{reduction_text:>12}"
        )

    print(
        "\nFirst subdivision depth with "
        f"maximum error < {ERROR_THRESHOLD} px: "
        f"{first_below_threshold}"
    )

    # --------------------------------------------------------
    # Save the numerical convergence results.
    # --------------------------------------------------------

    csv_path = (
        OUTPUT_DIRECTORY
        / "part1_2_convergence_results.csv"
    )

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow([
            "Subdivision Depth",
            "Polyline Vertices",
            "Polyline Segments",
            "Maximum Error (px)",
            "Previous Error / Current Error",
        ])

        for result in results:
            writer.writerow([
                result["depth"],
                result["vertices"],
                result["segments"],
                f"{result['max_error']:.10f}",
                (
                    ""
                    if result["reduction_factor"] is None
                    else
                    f"{result['reduction_factor']:.10f}"
                ),
            ])

    # --------------------------------------------------------
    # Create an overlay showing the measured maximum gap.
    # --------------------------------------------------------

    overlay_polyline = midpoint_polyline(
        B0,
        B1,
        B2,
        B3,
        depth=POINT2_OVERLAY_DEPTH,
    )

    (
        overlay_error,
        worst_curve_point,
        nearest_polyline_point,
    ) = max_curve_to_polyline_error(
        formula_points,
        overlay_polyline,
    )

    fig, ax = plt.subplots(figsize=(10, 7.5))

    ax.plot(
        formula_points[:, 0],
        formula_points[:, 1],
        linewidth=2,
        label="Method A: Cubic formula",
    )

    ax.plot(
        overlay_polyline[:, 0],
        overlay_polyline[:, 1],
        marker="o",
        linewidth=2,
        label=(
            "Method B: Midpoint subdivision "
            f"(depth={POINT2_OVERLAY_DEPTH})"
        ),
    )

    ax.scatter(
        [worst_curve_point[0]],
        [worst_curve_point[1]],
        s=60,
        label="Formula point at maximum gap",
    )

    ax.scatter(
        [nearest_polyline_point[0]],
        [nearest_polyline_point[1]],
        s=60,
        label="Nearest point on polyline",
    )

    ax.plot(
        [
            worst_curve_point[0],
            nearest_polyline_point[0],
        ],
        [
            worst_curve_point[1],
            nearest_polyline_point[1],
        ],
        linewidth=2,
        label=f"Maximum gap = {overlay_error:.3f} px",
    )

    ax.set_xlim(0, CANVAS_WIDTH)
    ax.set_ylim(0, CANVAS_HEIGHT)
    ax.set_aspect("equal", adjustable="box")

    ax.set_title(
        "Part 1.2 - Directed Gap from Formula Curve "
        "to Midpoint Polyline"
    )

    ax.set_xlabel("x coordinate (pixels)")
    ax.set_ylabel("y coordinate (pixels)")
    ax.grid(True)
    ax.legend()

    overlay_path = (
        OUTPUT_DIRECTORY
        / "part1_2_gap_overlay.png"
    )

    fig.savefig(
        overlay_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    # --------------------------------------------------------
    # Plot maximum error as a function of subdivision depth.
    # --------------------------------------------------------

    depths = [
        result["depth"]
        for result in results
    ]

    errors = [
        result["max_error"]
        for result in results
    ]

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.plot(
        depths,
        errors,
        marker="o",
        linewidth=2,
    )

    # A logarithmic y-axis makes the rapid error decrease easier
    # to inspect.
    ax.set_yscale("log")

    ax.axhline(
        ERROR_THRESHOLD,
        linestyle="--",
        label="0.5 px threshold",
    )

    ax.set_title(
        "Part 1.2 - Maximum Gap vs. Subdivision Depth"
    )

    ax.set_xlabel("Subdivision depth")
    ax.set_ylabel(
        "Maximum gap (pixels, log scale)"
    )

    ax.grid(True)
    ax.legend()

    convergence_plot_path = (
        OUTPUT_DIRECTORY
        / "part1_2_convergence.png"
    )

    fig.savefig(
        convergence_plot_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print("\nFiles generated")
    print("---------------")
    print(f"CSV results      : {csv_path}")
    print(f"Gap overlay      : {overlay_path}")
    print(
        f"Convergence plot : "
        f"{convergence_plot_path}"
    )


def _plot_bezier_segment(ax, control_points, label=None):
    """Plot one cubic Bezier segment using our own formula implementation."""
    points = sample_bezier_formula(
        *control_points,
        num_samples=300,
    )

    ax.plot(
        points[:, 0],
        points[:, 1],
        linewidth=2,
        label=label,
    )


def run_part1_point3():
    """Run Part 1 Point 3: Bezier joins."""

    # ========================================================
    # Experiment 1: three-segment open path
    # ========================================================
    
    print("\n" + "=" * 70)
    print("PART 1 - POINT 3: JOINS")
    print("=" * 70)

    # Segment 1 ends at J1.
    segment1 = (
        np.array([80.0, 180.0]),
        np.array([140.0, 300.0]),
        np.array([220.0, 380.0]),
        np.array([300.0, 380.0]),
    )

    # J1 is smooth:
    # (220, 380), J1, and (380, 380) are collinear,
    # and both direction lines have length 80 px.
    segment2 = (
        np.array([300.0, 380.0]),
        np.array([380.0, 380.0]),
        np.array([500.0, 380.0]),
        np.array([580.0, 300.0]),
    )

    # J2 is a corner because the direction lines on its two
    # sides are not collinear.
    segment3 = (
        np.array([580.0, 300.0]),
        np.array([660.0, 300.0]),
        np.array([700.0, 220.0]),
        np.array([720.0, 150.0]),
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    _plot_bezier_segment(ax, segment1, "Bezier segment 1")
    _plot_bezier_segment(ax, segment2, "Bezier segment 2")
    _plot_bezier_segment(ax, segment3, "Bezier segment 3")
    
    # Show the control polygons for each Bezier segment.
    for segment in (segment1, segment2, segment3):
        control = np.array(segment)
        ax.plot(
            control[:, 0],
            control[:, 1],
            "--",
            marker="o",
            linewidth=1,
            alpha=0.6,
        )

    j1 = segment1[3]
    j2 = segment2[3]

    # Show the direction lines around the smooth join.
    ax.plot(
        [segment1[2][0], j1[0], segment2[1][0]],
        [segment1[2][1], j1[1], segment2[1][1]],
        "--",
        label="Smooth-join direction lines",
    )

    # Show the direction lines around the corner join.
    ax.plot(
        [segment2[2][0], j2[0]],
        [segment2[2][1], j2[1]],
        "--",
    )
    ax.plot(
        [j2[0], segment3[1][0]],
        [j2[1], segment3[1][1]],
        "--",
        label="Corner direction lines",
    )

    ax.scatter(
        [j1[0], j2[0]],
        [j1[1], j2[1]],
        s=60,
    )

    ax.annotate("Smooth join", j1, xytext=(8, 10),
                textcoords="offset points")
    ax.annotate("Corner join", j2, xytext=(8, 10),
                textcoords="offset points")

    ax.set_xlim(0, CANVAS_WIDTH)
    ax.set_ylim(0, CANVAS_HEIGHT)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Part 1.3 - Three-Segment Open Path")
    ax.set_xlabel("x coordinate (pixels)")
    ax.set_ylabel("y coordinate (pixels)")
    ax.grid(True)
    ax.legend()

    fig.savefig(
        OUTPUT_DIRECTORY / "part1_3_open_path.png",
        dpi=200,
        bbox_inches="tight",
    )
    plt.close(fig)

    # ========================================================
    # Experiment 2: equal vs. unequal direction-line lengths
    # ========================================================

    left_segment = (
        np.array([80.0, 180.0]),
        np.array([140.0, 300.0]),
        np.array([220.0, 380.0]),
        np.array([300.0, 380.0]),
    )

    # Equal-length case:
    # both direction lines have length 80 px.
    right_equal = (
        np.array([300.0, 380.0]),
        np.array([380.0, 380.0]),
        np.array([470.0, 300.0]),
        np.array([540.0, 180.0]),
    )

    # Unequal-length case:
    # the direction points remain collinear, but the right
    # direction line is twice as long (160 px).
    right_unequal = (
        np.array([300.0, 380.0]),
        np.array([460.0, 380.0]),
        np.array([470.0, 300.0]),
        np.array([540.0, 180.0]),
    )

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(12, 5),
        sharex=True,
        sharey=True,
    )

    cases = [
        ("Equal direction-line lengths", right_equal),
        ("Unequal direction-line lengths", right_unequal),
    ]

    for ax, (title, right_segment) in zip(axes, cases):
        _plot_bezier_segment(ax, left_segment, "Left segment")
        _plot_bezier_segment(ax, right_segment, "Right segment")
        
        # Show the control polygons of both Bezier segments.
        for segment in (left_segment, right_segment):
            control = np.array(segment)
            ax.plot(
                control[:, 0],
                control[:, 1],
                "--",
                marker="o",
                linewidth=1,
                alpha=0.6,
            )

        join = left_segment[3]

        # Display the two direction lines around the join.
        ax.plot(
            [
                left_segment[2][0],
                join[0],
                right_segment[1][0],
            ],
            [
                left_segment[2][1],
                join[1],
                right_segment[1][1],
            ],
            "--",
            marker="o",
            label="Direction lines",
        )

        ax.set_title(title)
        ax.set_xlim(50, 570)
        ax.set_ylim(120, 450)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x coordinate (pixels)")
        ax.grid(True)
        ax.legend()

    axes[0].set_ylabel("y coordinate (pixels)")

    fig.savefig(
        OUTPUT_DIRECTORY / "part1_3_equal_vs_unequal.png",
        dpi=200,
        bbox_inches="tight",
    )
    plt.close(fig)
    
    print("\nFiles generated")
    print("---------------")
    print( "Open path figure      : " f"{OUTPUT_DIRECTORY / 'part1_3_open_path.png'}")
    print( "Join comparison figure: " f"{OUTPUT_DIRECTORY / 'part1_3_equal_vs_unequal.png'}")

# ============================================================
# Main program
# ============================================================

def run_part1():
    """
    Run all currently implemented items in Part 1.
    """
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )
    run_part1_point1()
    run_part1_point2()
    run_part1_point3()