import numpy as np


def max_curve_to_polyline_error(
    curve_points,
    polyline_points,
):
    """
    Measure the directed maximum gap from sampled formula-curve
    points to the nearest segments of a polyline.

    For every point on the sampled formula curve, the function finds
    its Euclidean distance to every polyline segment and keeps the
    smallest distance. The largest of those minimum distances is the
    directed error required by Part 1 Point 2.

    The direction is intentionally:

        formula curve -> nearest polyline segment

    and not the reverse.

    Parameters
    ----------
    curve_points : numpy.ndarray
        Densely sampled points from the cubic Bezier formula.

    polyline_points : numpy.ndarray
        Ordered vertices of the midpoint-subdivision polyline.

    Returns
    -------
    max_error : float
        Largest distance from a formula-curve point to its nearest
        polyline segment.

    worst_curve_point : numpy.ndarray
        Formula-curve point where the maximum measured gap occurs.

    nearest_polyline_point : numpy.ndarray
        Closest point on the polyline to worst_curve_point.
    """

    curve_points = np.asarray(curve_points, dtype=float)
    polyline_points = np.asarray(polyline_points, dtype=float)

    if len(curve_points) == 0:
        raise ValueError("curve_points must not be empty.")

    if len(polyline_points) < 2:
        raise ValueError(
            "A polyline must contain at least two vertices."
        )

    # For each formula-curve sample, store the smallest squared
    # distance found so far to any polyline segment.
    minimum_squared_distances = np.full(
        len(curve_points),
        np.inf,
    )

    # Store the corresponding closest point on the polyline.
    nearest_points = np.zeros_like(curve_points)

    # Examine every straight segment of the midpoint polyline.
    for i in range(len(polyline_points) - 1):
        segment_start = polyline_points[i]
        segment_end = polyline_points[i + 1]

        segment_vector = segment_end - segment_start
        segment_length_squared = float(
            np.dot(segment_vector, segment_vector)
        )

        if segment_length_squared == 0.0:
            # Degenerate segment: both endpoints are identical.
            closest_points = np.repeat(
                segment_start[None, :],
                len(curve_points),
                axis=0,
            )

        else:
            # Project every formula-curve point onto the infinite
            # line containing this segment.
            projection = (
                (curve_points - segment_start)
                @ segment_vector
            ) / segment_length_squared

            # Restrict the projection parameter to [0, 1]
            # so the closest point lies on the finite segment.
            projection = np.clip(
                projection,
                0.0,
                1.0,
            )
            # Compute the closest point coordinates on the current segment
            # for every formula-curve point.
            closest_points = (
                segment_start
                + projection[:, None] * segment_vector
            )

        difference = curve_points - closest_points

        squared_distances = np.sum(
            difference * difference,
            axis=1,
        )

        # Update only the curve samples for which this segment is
        # closer than every previously examined segment.
        better = (
            squared_distances
            < minimum_squared_distances
        )

        minimum_squared_distances[better] = (
            squared_distances[better]
        )

        nearest_points[better] = closest_points[better]

    # The assignment asks for the largest distance after taking
    # the nearest polyline segment for every formula-curve point.
    worst_index = int(
        np.argmax(minimum_squared_distances)
    )

    max_error = float(
        np.sqrt(
            minimum_squared_distances[worst_index]
        )
    )

    return (
        max_error,
        curve_points[worst_index],
        nearest_points[worst_index],
    )