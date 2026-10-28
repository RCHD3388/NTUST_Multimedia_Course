import numpy as np


def bezier_point(b0, b1, b2, b3, t):
    """
    Evaluate one point on a cubic Bezier curve using the explicit
    cubic Bezier formula.

    Parameters
    ----------
    b0, b1, b2, b3 : array-like
        The four control points of the cubic Bezier curve.
        b0 and b3 are the endpoints, while b1 and b2 are
        the direction/control points.

    t : float
        Curve parameter in the range [0, 1].

    Returns
    -------
    numpy.ndarray
        The two-dimensional coordinate of the curve at parameter t.
    """

    # Convert all control points to NumPy arrays so that vector
    # arithmetic can be performed directly on their coordinates.
    b0 = np.asarray(b0, dtype=float)
    b1 = np.asarray(b1, dtype=float)
    b2 = np.asarray(b2, dtype=float)
    b3 = np.asarray(b3, dtype=float)

    # Cubic Bezier formula from Chapter 4:
    # C(t) = (1-t)^3 b0
    #      + 3t(1-t)^2 b1
    #      + 3t^2(1-t) b2
    #      + t^3 b3
    point = (
        ((1.0 - t) ** 3) * b0
        + 3.0 * t * ((1.0 - t) ** 2) * b1
        + 3.0 * (t ** 2) * (1.0 - t) * b2
        + (t ** 3) * b3
    )

    return point


def sample_bezier_formula(b0, b1, b2, b3, num_samples=1000):
    """
    Sample a cubic Bezier curve using the explicit formula.

    This function does not use any built-in Bezier or curve routine.
    Every curve coordinate is computed using bezier_point().

    Parameters
    ----------
    b0, b1, b2, b3 : array-like
        The four Bezier control points.

    num_samples : int
        Number of parameter values sampled between t=0 and t=1.

    Returns
    -------
    numpy.ndarray
        An array of shape (num_samples, 2) containing sampled
        curve coordinates.
    """

    # Generate evenly spaced parameter values from the start
    # to the end of the Bezier curve.
    t_values = np.linspace(0.0, 1.0, num_samples)

    # Compute every point ourselves using the cubic formula.
    points = np.array(
        [bezier_point(b0, b1, b2, b3, t) for t in t_values]
    )

    return points


def split_bezier_midpoint(b0, b1, b2, b3):
    """
    Split a cubic Bezier curve at t = 0.5 using midpoint construction.

    The construction repeatedly takes midpoints between neighboring
    control points. This is the de Casteljau construction evaluated
    specifically at t = 0.5.

    Parameters
    ----------
    b0, b1, b2, b3 : array-like
        The four control points of the original cubic Bezier curve.

    Returns
    -------
    tuple
        Two tuples containing the four control points of the
        left and right Bezier sub-curves.
    """

    b0 = np.asarray(b0, dtype=float)
    b1 = np.asarray(b1, dtype=float)
    b2 = np.asarray(b2, dtype=float)
    b3 = np.asarray(b3, dtype=float)

    # First level: midpoints of the original control polygon.
    b01 = (b0 + b1) / 2.0
    b12 = (b1 + b2) / 2.0
    b23 = (b2 + b3) / 2.0

    # Second level: midpoints between the first-level midpoints.
    b012 = (b01 + b12) / 2.0
    b123 = (b12 + b23) / 2.0

    # Third level: this point lies on the original Bezier curve
    # exactly at t = 0.5 and becomes the shared endpoint of the
    # two resulting sub-curves.
    midpoint = (b012 + b123) / 2.0

    # Control points for the left half of the original curve.
    left_curve = (
        b0,
        b01,
        b012,
        midpoint,
    )

    # Control points for the right half of the original curve.
    right_curve = (
        midpoint,
        b123,
        b23,
        b3,
    )

    return left_curve, right_curve


def midpoint_polyline(b0, b1, b2, b3, depth):
    """
    Approximate a cubic Bezier curve using recursive midpoint subdivision.

    At every recursion level, the curve is divided into two Bezier
    sub-curves at t = 0.5. Once the requested subdivision depth is
    reached, the approximation uses the endpoints of the resulting
    sub-curves.

    Connecting those endpoints produces the polyline required by
    Part 1 of the assignment.

    Parameters
    ----------
    b0, b1, b2, b3 : array-like
        Four control points of the cubic Bezier curve.

    depth : int
        Number of recursive subdivision levels.

    Returns
    -------
    numpy.ndarray
        Ordered polyline vertices approximating the Bezier curve.
        At depth d, the polyline contains 2^d + 1 vertices.
    """

    if depth < 0:
        raise ValueError("Subdivision depth must be non-negative.")

    b0 = np.asarray(b0, dtype=float)
    b1 = np.asarray(b1, dtype=float)
    b2 = np.asarray(b2, dtype=float)
    b3 = np.asarray(b3, dtype=float)

    # Base case:
    # At depth 0, no further subdivision is performed.
    # The approximation of this sub-curve is simply the straight
    # segment connecting its two endpoints.
    if depth == 0:
        return np.array([b0, b3])

    # Split the current curve into two Bezier curves at t = 0.5.
    left_curve, right_curve = split_bezier_midpoint(
        b0, b1, b2, b3
    )

    # Recursively subdivide both halves.
    left_points = midpoint_polyline(*left_curve, depth - 1)
    right_points = midpoint_polyline(*right_curve, depth - 1)

    # Both recursive results contain the shared midpoint.
    # Remove the first point of the right half to avoid duplicating it.
    return np.vstack(
        [left_points, right_points[1:]]
    )
    

def sample_bezier_by_max_spacing(
    b0,
    b1,
    b2,
    b3,
    max_spacing=0.1,
    initial_intervals=1024,
):
    """
    Sample the cubic Bezier formula curve densely enough that the
    Euclidean distance between every pair of consecutive sampled
    points is strictly smaller than max_spacing.

    The assignment requires consecutive formula-curve samples to
    be less than 0.1 pixel apart. Instead of assuming that a fixed
    sample count is sufficient, this function verifies the spacing
    and doubles the number of intervals until the requirement is met.

    Parameters
    ----------
    b0, b1, b2, b3 : array-like
        The four control points of the cubic Bezier curve.

    max_spacing : float
        Maximum allowed distance, in pixels, between consecutive
        sampled points.

    initial_intervals : int
        Initial number of equal parameter intervals over [0, 1].

    Returns
    -------
    points : numpy.ndarray
        Sampled points on the formula curve.

    t_values : numpy.ndarray
        Parameter values used to generate the sampled points.

    actual_max_spacing : float
        Largest Euclidean distance between consecutive sampled points.
    """

    if max_spacing <= 0:
        raise ValueError("max_spacing must be positive.")

    if initial_intervals < 1:
        raise ValueError("initial_intervals must be at least 1.")

    intervals = initial_intervals

    while True:
        # Generate uniformly spaced parameter values over [0, 1].
        t_values = np.linspace(0.0, 1.0, intervals + 1)

        # Compute every curve point using our own cubic Bezier formula.
        points = np.array([
            bezier_point(b0, b1, b2, b3, t)
            for t in t_values
        ])

        # Measure the actual Euclidean distance between every pair
        # of consecutive samples.
        consecutive_distances = np.linalg.norm(
            np.diff(points, axis=0),
            axis=1,
        )

        actual_max_spacing = float(
            np.max(consecutive_distances)
        )

        # The assignment explicitly requires the spacing to be
        # strictly smaller than 0.1 pixel.
        if actual_max_spacing < max_spacing:
            return points, t_values, actual_max_spacing

        # Increase sampling density and verify the condition again.
        intervals *= 2