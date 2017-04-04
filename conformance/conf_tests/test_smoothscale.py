# Simple transform tests
# Copyright (C) 2015  Neil Muller
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

from pygame import transform, surface, draw
from .helpers import conformance_test_case


def _make_object():
    """Create a vaguely interesting object to transform."""
    obj = surface.Surface((40, 80), depth=32)
    draw.line(obj, (255, 0, 0, 255), (10, 10), (10, 40), 3)
    draw.line(obj, (255, 255, 0, 255), (10, 10), (40, 10), 3)
    draw.line(obj, (255, 128, 128, 255), (40, 10), (40, 40), 2)
    draw.lines(obj, (255, 255, 255, 255), 1, [(20, 20), (20, 30), (30, 30)])
    return obj

# Pygame officially only supports smoothscale for 24-bit and 32-bit surfaces.
@conformance_test_case('smooth_subsurface', depths=(24, 32))
def test_subsurface_smoothscale(surface):
    """Test scaling a small subsurface"""
    obj = _make_object()

    transform.set_smoothscale_backend('GENERIC')

    obj_sub = obj.subsurface((20, 20, 20, 25))

    surface.blit(obj, (20, 20))
    surface.blit(obj_sub, (60, 20))
    obj1 = transform.smoothscale(obj_sub,
                                 (obj_sub.get_width(), obj_sub.get_height()))
    surface.blit(obj1, (120, 20))
    obj1 = transform.smoothscale(obj_sub, (20, 20))
    surface.blit(obj1, (60, 60))
    obj1 = transform.smoothscale(obj_sub, (40, 40))
    surface.blit(obj1, (80, 80))
    obj1 = transform.smoothscale(obj_sub, (60, 60))
    surface.blit(obj1, (160, 160))
    obj1 = transform.smoothscale(obj_sub, (120, 120))
    surface.blit(obj1, (220, 220))


@conformance_test_case('smooth_int', depths=(24, 32))
def test_int_smoothscale(surface):
    """Simple integer scaling tests"""
    obj = _make_object()

    transform.set_smoothscale_backend('GENERIC')

    surface.blit(obj, (20, 20))
    obj1 = transform.smoothscale(obj, (obj.get_width(), obj.get_height()))
    surface.blit(obj1, (120, 20))
    obj1 = transform.smoothscale(obj, (20, 20))
    surface.blit(obj1, (60, 60))
    obj1 = transform.smoothscale(obj, (40, 40))
    surface.blit(obj1, (80, 80))
    obj1 = transform.smoothscale(obj, (60, 60))
    surface.blit(obj1, (160, 160))
    obj1 = transform.smoothscale(obj, (120, 120))
    surface.blit(obj1, (320, 320))


@conformance_test_case('smooth_x', depths=(24, 32))
def test_x_smoothscale(surface):
    """Scale x axis only"""
    obj = _make_object()

    transform.set_smoothscale_backend('GENERIC')

    surface.blit(obj, (20, 20))
    obj1 = transform.smoothscale(obj, (25, 20))
    surface.blit(obj1, (80, 80))
    obj2 = transform.smoothscale(obj, (35, 20))
    surface.blit(obj2, (160, 160))
    obj3 = transform.smoothscale(obj, (55, 20))
    surface.blit(obj3, (240, 160))
    obj4 = transform.smoothscale(obj, (15, 20))
    surface.blit(obj4, (240, 240))
    obj5 = transform.smoothscale(obj, (100, 20))
    surface.blit(obj5, (320, 320))


@conformance_test_case('smooth_y', depths=(24, 32))
def test_y_smoothscale(surface):
    """Scale y axis only"""
    obj = _make_object()

    transform.set_smoothscale_backend('GENERIC')

    surface.blit(obj, (20, 20))
    obj1 = transform.smoothscale(obj, (20, 25))
    surface.blit(obj1, (80, 80))
    obj2 = transform.smoothscale(obj, (20, 35))
    surface.blit(obj2, (160, 160))
    obj3 = transform.smoothscale(obj, (20, 55))
    surface.blit(obj3, (240, 160))
    obj4 = transform.smoothscale(obj, (20, 15))
    surface.blit(obj4, (240, 240))
    obj5 = transform.smoothscale(obj, (20, 100))
    surface.blit(obj5, (320, 320))


@conformance_test_case('smooth_varied', depths=(24, 32))
def test_varied_smoothscale(surface):
    """Scale with more varies factors"""
    obj = _make_object()

    transform.set_smoothscale_backend('GENERIC')

    surface.blit(obj, (20, 20))
    obj1 = transform.smoothscale(obj, (25, 55))
    surface.blit(obj1, (80, 80))
    obj1 = transform.smoothscale(obj, (14, 13))
    surface.blit(obj1, (160, 160))
    obj1 = transform.smoothscale(obj, (72, 68))
    surface.blit(obj1, (320, 320))
