"""Simple tests for surfaces"""

from pygame import draw


def test_scroll(surface):
    """Simple scroll test"""

    draw.line(surface, (200, 200, 200, 200), (100, 100), (700, 100), 1)
    draw.line(surface, (200, 200, 200, 200), (700, 100), (700, 500), 1)
    draw.line(surface, (200, 200, 200, 200), (700, 500), (100, 500), 1)
    draw.line(surface, (200, 200, 200, 200), (100, 500), (100, 100), 1)

    draw.line(surface, (123, 234, 213, 64), (777, 0), (0, 591), 6)
    draw.line(surface, (213, 233, 231, 214), (0, 0), (800, 600), 15)

    surface.scroll(-11, -10)
    surface.scroll(0, 0)
    surface.scroll(96, 200)
    surface.scroll(0, -1)
    surface.scroll(-1, -1)
    surface.scroll(800, 600)
    surface.scroll(8000, 6000)
