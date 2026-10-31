"""
Basic RGB compositing operations for partially transparent shapes.
"""


def blend_rgb(background, foreground, opacity):
    """
    Blend one foreground color over one background color.

    The foreground contribution is controlled by opacity,
    where 0.0 is fully transparent and 1.0 is fully opaque.
    """
    if not 0.0 <= opacity <= 1.0:
        raise ValueError("Opacity must be between 0.0 and 1.0.")

    return tuple(
        int(round(
            foreground[channel] * opacity
            + background[channel] * (1.0 - opacity)
        ))
        for channel in range(3)
    )


def composite_mask(background, mask, foreground_color, opacity):
    """
    Composite a foreground color only on pixels covered by the shape mask.
    """
    height = len(background)
    width = len(background[0])

    result = [
        row.copy()
        for row in background
    ]

    for y in range(height):
        for x in range(width):
            if mask[y][x]:
                result[y][x] = blend_rgb(
                    background[y][x],
                    foreground_color,
                    opacity,
                )

    return result


def find_changed_pixels(original, result):
    """
    Return the coordinates of every pixel whose RGB value changed.
    """
    changed = []

    height = len(original)
    width = len(original[0])

    for y in range(height):
        for x in range(width):
            if original[y][x] != result[y][x]:
                changed.append((x, y))

    return changed