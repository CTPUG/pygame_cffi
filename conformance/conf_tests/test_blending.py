# blit tests
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
"""Test the various blend flags for surface.blit"""

from pygame import surface, draw
from pygame.locals import (SRCALPHA, BLEND_RGBA_ADD, BLEND_RGBA_SUB,
                           BLEND_RGBA_MULT, BLEND_RGBA_MIN, BLEND_RGBA_MAX,
                           BLEND_RGB_MULT, BLEND_MULT)

from .helpers import conformance_test_case


def _fill_surface(surface):
    """Fill the surface with lines in various colours"""
    y = 0
    for colour in [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 0),
                   (255, 255, 255, 255), (0, 0, 0, 255), (255, 255, 0, 255),
                   (0, 255, 255, 255), (255, 0, 255, 255)]:
        draw.rect(surface, colour, (0, y, 800, y + 75))
        y += 75


def _make_object():
    """Create an object of multiple colours to blit with."""
    obj = surface.Surface((100, 40), SRCALPHA, depth=32)
    draw.rect(obj, (255, 0, 0, 255), (0, 0, 10, 40))
    draw.rect(obj, (255, 255, 0, 255), (10, 0, 10, 6))
    draw.rect(obj, (255, 255, 255, 255), (20, 0, 10, 40))
    draw.rect(obj, (0, 255, 255, 255), (30, 0, 10, 40))
    draw.rect(obj, (0, 0, 255, 255), (40, 0, 10, 40))
    draw.rect(obj, (0, 255, 0, 255), (50, 0, 10, 40))
    draw.rect(obj, (128, 255, 128, 128), (60, 0, 10, 40))
    draw.rect(obj, (128, 128, 255, 128), (70, 0, 10, 40))
    draw.rect(obj, (0, 128, 255, 128), (80, 0, 10, 40))
    draw.rect(obj, (128, 255, 255, 128), (90, 0, 10, 40))
    return obj


def do_blit_test(surface, flag):
    _fill_surface(surface)
    pattern = _make_object()
    y = 0
    while y < 600:
        surface.blit(pattern, (200, y), special_flags=flag)
        y += 50


# We only test these on 32 bit surfaces, since we're
# specifically testing RGBA behaviour

@conformance_test_case('test_rgba_add', depths=(32,))
def test_rgba_add(surface):
    """Test blit with BLEND_RGBA_ADD"""
    do_blit_test(surface, BLEND_RGBA_ADD)


@conformance_test_case('test_rgba_sub', depths=(32,))
def test_rgba_sub(surface):
    """Test blit with BLEND_RGBA_ADD"""
    do_blit_test(surface, BLEND_RGBA_SUB)


@conformance_test_case('test_rgba_min', depths=(32,))
def test_rgba_min(surface):
    """Test blit with BLEND_RGBA_MIN"""
    do_blit_test(surface, BLEND_RGBA_MIN)


@conformance_test_case('test_rgba_max', depths=(32,))
def test_rgba_max(surface):
    """Test blit with BLEND_RGBA_MAX"""
    do_blit_test(surface, BLEND_RGBA_MAX)


@conformance_test_case('test_rgba_mult', depths=(32,))
def test_rgba_mult(surface):
    """Test blit with BLEND_RGBA_MULT"""
    do_blit_test(surface, BLEND_RGBA_MULT)


@conformance_test_case('test_rgb_mult', depths=(32,))
def test_rgb_mult(surface):
    """Test blit with BLEND_RGB_MULT"""
    do_blit_test(surface, BLEND_RGB_MULT)


@conformance_test_case('test_blend_mult', depths=(32,))
def test_blend_mult(surface):
    """Test blit with BLEND_MULT"""
    do_blit_test(surface, BLEND_MULT)
