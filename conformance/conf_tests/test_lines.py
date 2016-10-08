# Test lines

from pygame import draw


def test_horz_line(test_surf):
    """Draw several horizonatl lines."""
    y = 10
    for length in range(100):
        y += 5
        draw.line(test_surf, (255, 255, 255, 255), (y, y), (y + length, y))


def test_vert_line(test_surf):
    """Draw several vertical lines."""
    x = 10
    for length in range(100):
        x += 5
        draw.line(test_surf, (255, 255, 255, 255),
                  (x, length), (x, 2 * length))


def test_horz_line_width(test_surf):
    """Draw several horizontal lines, varying in width."""
    y = 10
    for width in range(20):
        y += 5 + 2*width
        length = 10 * width
        draw.line(test_surf, (255, 255, 255, 255), (y, y),
                  (y + length, y), width)


def test_vert_line_width(test_surf):
    """Draw several vertical lines, varying in width."""
    x = 10
    for width in range(20):
        x += 5 + 2*width
        length = 10 * width
        draw.line(test_surf, (255, 255, 255, 255), (x, 2*width),
                  (x, 2*width + length), width)


def test_lines(test_surf):
    """Draw a collection of angled and overlapping lines."""

    start = [(10, 10), (20, 20), (30, 30), (10, 40), (20, 80),
             (20, 100), (200, 10), (200, 200)]
    end = [(10, 100), (20, 100), (30, 300), (40, 400), (50, 500)]
    for p1 in start:
        for p2 in end:
            draw.line(test_surf, (255, 255, 255, 255), p1, p2)


def test_lines_width(test_surf):
    """Draw a collection of angled and overlapping lines of varying widths."""
    start = [(10, 10), (20, 20), (30, 30), (10, 40), (20, 80),
             (20, 100), (200, 10), (200, 200)]
    end = [(10, 100), (20, 100), (30, 300), (40, 400), (50, 500)]
    width = 2
    for p1 in start:
        for p2 in end:
            draw.line(test_surf, (255, 255, 255, 255), p1, p2, width)
            width = width + 1
            if width > 18:
                width = 2

    draw.line(test_surf, (255, 255, 255, 255), (346, 134), (368, 146), 2)
    draw.line(test_surf, (255, 255, 255, 255), (368, 146), (362, 144), 2)
    draw.line(test_surf, (255, 255, 255, 255), (362, 144), (371, 81), 2)
    draw.line(test_surf, (255, 255, 255, 255), (371, 81), (304, 116), 2)
    draw.line(test_surf, (255, 255, 255, 255), (304, 116), (343, 102), 2)
    draw.line(test_surf, (255, 255, 255, 255), (343, 102),  (375, 150), 2)
    draw.line(test_surf, (255, 255, 255, 255), (375, 150), (334, 82), 2)
    draw.line(test_surf, (255, 255, 255, 255), (334, 82), (331, 94), 2)
    draw.line(test_surf, (255, 255, 255, 255), (331, 94), (317, 134), 2)
    draw.line(test_surf, (255, 255, 255, 255), (331, 94), (312, 99), 2)
    draw.line(test_surf, (255, 255, 255, 255), (312, 99), (337, 96), 2)
    draw.line(test_surf, (255, 255, 255, 255), (337, 96), (346, 134), 2)


def test_lines_function(test_surf):
    """Test the draw.lines function"""
    points = [(10, 10), (20, 20), (30, 30), (10, 40), (20, 80),
              (20, 100), (200, 10), (200, 200), (10, 100), (20, 100),
              (30, 300), (40, 400), (50, 500)]
    draw.lines(test_surf, (255, 255, 255, 255), 0, points)
    points2 = [(x[0] + 5, x[1] + 5) for x in points]
    draw.lines(test_surf, (255, 255, 0, 255), 0, points2, 2)
    points2 = [(x[0] + 10, x[1] + 10) for x in points]
    draw.lines(test_surf, (255, 0, 0, 255), 0, points2, 3)
    points2 = [(x[0] + 30, x[1] + 30) for x in points]
    draw.lines(test_surf, (0, 255, 0, 255), 0, points2, 5)
    draw.lines(test_surf, (255, 255, 255, 255), 1, [(346, 134), (368, 146),
                                                    (362, 144), (371, 81),
                                                    (304, 116), (343, 102),
                                                    (375, 150), (334, 82),
                                                    (331, 94), (317, 134),
                                                    (312, 99), (337, 96)], 2)
