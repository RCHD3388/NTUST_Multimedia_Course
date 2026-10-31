# renderer/image_io.py

from PIL import Image
from renderer.scanline import Canvas


def save_png(canvas: Canvas, filename: str) -> None:
    """
    Save an already-rendered pixel array as a PNG image.
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