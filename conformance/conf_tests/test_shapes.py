# Test the draw module
# Copyright (C) 2014  Neil Muller
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301  USA

from pygame import draw, rect

from .helpers import conformance_test_case


@conformance_test_case('rect')
def test_rect(test_surf):
    """Draw several rectangles."""
    for y in range(10, 200, 45):
        x = 10
        for width in range(10, 30, 3):
            for height in range(10, 40, 7):
                r = rect.Rect(x, y, width, height)
                x += width + 2
                draw.rect(test_surf, (255, 255, 255, 255), r)


@conformance_test_case('polygon')
def test_polygon(test_surf):
    """Draw several polygons."""
    # triangle
    draw.polygon(test_surf, (255, 255, 255, 255), [(10, 10), (30, 30),
                                                   (45, 30)])
    draw.polygon(test_surf, (255, 0, 255, 255), [(50, 10), (80, 30), (95, 20)],
                 3)
    # overlap
    draw.polygon(test_surf, (255, 0, 128, 255), [(50, 15), (80, 25),
                                                 (105, 25)],
                 0)
    # square
    draw.polygon(test_surf, (255, 255, 255, 255), [(150, 10), (150, 50),
                                                   (190, 50), (190, 10)])
    draw.polygon(test_surf, (0, 255, 255, 255), [(220, 10), (220, 50),
                                                 (260, 50), (260, 10)], 1)
    # hexagon
    draw.polygon(test_surf, (0, 0, 255, 255), [(310, 10), (320, 25),
                                               (320, 50), (310, 65),
                                               (300, 50), (300, 25)])
    # Funky
    draw.polygon(test_surf, (255, 255, 255, 255), [(246, 134), (268, 146),
                                                   (262, 144), (271, 81),
                                                   (204, 116), (243, 102),
                                                   (275, 150), (234, 82),
                                                   (231, 94), (217, 134),
                                                   (212, 99), (237, 96)], 2)
    draw.polygon(test_surf, (255, 255, 255, 255), [(369, 158), (342, 193),
                                                   (319, 205), (316, 217),
                                                   (356, 183), (312, 169),
                                                   (333, 212), (358, 200),
                                                   (310, 168), (301, 151),
                                                   (300, 145), (307, 214)], 0)
    # Odd colour, for bit depth tests
    draw.polygon(test_surf, (123, 46, 223, 255), [(369, 458), (342, 593),
                                                  (319, 505), (316, 417),
                                                  (356, 483), (312, 469),
                                                  (333, 512), (358, 500),
                                                  (310, 468), (301, 451),
                                                  (300, 445), (307, 514)], 0)



@conformance_test_case('hollow_circles')
def test_hollow_circles(test_surf):
    """Draw several circles of different thicknesses and sizes"""
    for thickness in range(1, 7):
        cent_x = 100 + thickness * 50
        cent_y = 10
        for radius in range(10, 200, 10):
            cent_y += radius + 1
            draw.circle(test_surf, (255, 255, 255, 255), (cent_x, cent_y),
                        radius, thickness)


@conformance_test_case('filled_circles')
def test_filled_circles(test_surf):
    """Draw several filled circles"""
    for cent_x, color in ((100, (0, 0, 255, 255)), (400, (0, 255, 255, 255)),
                          (600, (255, 0, 255, 255))):
        cent_y = 10
        for radius in range(10, 100, 10):
            cent_y += radius + 1
            draw.circle(test_surf, color, (cent_x, cent_y),
                        radius)


@conformance_test_case('filled_ellipses_1')
def test_filled_ellipses_1(test_surf):
    """Draw several filled circles"""
    for cent_x, color in ((50, (0, 0, 255, 255)), (200, (0, 255, 255, 255)),
                          (350, (255, 0, 255, 255)),
                          (500, (123, 46, 223, 255))):
        cent_y = 10
        div = 8
        offset = 0
        for radius in range(10, 100, 10):
            if div > 2:
                div = div // 2
            else:
                div = div * 2
            cent_y += radius // div + 1
            offset += 35
            e_rect = rect.Rect(cent_x - radius + offset,
                               cent_y - radius // div,
                               radius, div * radius)
            draw.ellipse(test_surf, color, e_rect)


@conformance_test_case('filled_ellipses_2')
def test_filled_ellipses_2(test_surf):
    """Draw several filled circles"""
    for cent_x, color in ((50, (0, 0, 255, 255)), (210, (0, 255, 255, 255)),
                          (420, (255, 0, 255, 255)),
                          (600, (123, 23, 235, 255))):
        cent_y = 10
        div = 9
        for radius in range(10, 100, 10):
            cent_y += radius + 1
            if div > 3:
                div = div // 3
            else:
                div = div * 3
            e_rect = rect.Rect(cent_x - radius // div, cent_y - radius,
                               div * radius, radius)
            draw.ellipse(test_surf, color, e_rect)


@conformance_test_case('hollow_ellipses')
def test_hollow_ellipses(test_surf):
    for cent_x, cent_y, color in ((70, 130, (255, 0, 0, 255)),
                                  (150, 450, (255, 255, 255, 255)),
                                  (200, 200, (0, 255, 0, 255)),
                                  (500, 500, (255, 128, 128, 255))):
        for r1, r2 in ((30, 20), (50, 10), (10, 40), (15, 90)):
            for thickness in range(1, 9, 3):
                e_rect = (cent_x - r1 + 30 * thickness,
                          cent_y - r2 - 30 * thickness,
                          2 * r1, 2 * r2)
                draw.ellipse(test_surf, color, e_rect, thickness)


@conformance_test_case('limit_circles')
def test_filled_circles_limits(test_surf):
    """Draw several filled circles that wrap the limits in various ways"""
    for cent_x, color in ((100, (0, 0, 255, 255)), (400, (0, 255, 255, 255)),
                          (600, (255, 0, 255, 255))):
        cent_y = 10
        for radius in range(10, 100, 10):
            cent_y += radius + 1
            o_x = 2**16 + cent_x
            o_y = 2**16 + cent_y
            # This should appear
            draw.circle(test_surf, color, (o_x, o_y),
                        radius)
            # This shouldn't appear, but not crash
            o_x = 2**15 + cent_x
            o_y = 2**17 + cent_x
            draw.circle(test_surf, color, (o_x, o_y),
                        radius)
