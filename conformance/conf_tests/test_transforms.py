# Simple transform tests
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

@conformance_test_case('flip')
def test_flip(surface):
    """Simple flip tests"""
    obj = _make_object()

    surface.blit(obj, (20, 20))
    obj1 = transform.flip(obj, True, False)
    surface.blit(obj1, (80, 80))
    obj1 = transform.flip(obj, False, True)
    surface.blit(obj1, (160, 160))
    obj1 = transform.flip(obj, True, True)
    surface.blit(obj1, (320, 320))


@conformance_test_case('flip_subsurface')
def test_flip_subsurface(surface):
    """Test transform.flip with a subsurface as the source"""
    obj = _make_object()

    surface.blit(obj, (20, 20))
    obj_sub = obj.subsurface((20, 20, 15, 25))
    surface.blit(obj_sub, (20, 190))
    obj1 = transform.flip(obj_sub, True, False)
    surface.blit(obj1, (60, 190))
    obj1 = transform.flip(obj_sub, False, True)
    surface.blit(obj1, (20, 390))
    obj1 = transform.flip(obj_sub, False, False)
    surface.blit(obj1, (60, 390))


@conformance_test_case('scale')
def test_scale(surface):
    """Simple scale tests"""
    obj = _make_object()

    surface.blit(obj, (20, 20))
    obj1 = transform.scale(obj, (100, 100))
    surface.blit(obj1, (80, 80))
    obj2 = transform.scale(obj1, (60, 60))
    surface.blit(obj2, (160, 160))
    obj3 = transform.scale(obj, (60, 60))
    surface.blit(obj3, (240, 160))
    obj1 = transform.scale2x(obj)
    surface.blit(obj1, (240, 240))
    obj1 = transform.scale2x(obj2)
    surface.blit(obj1, (320, 320))


@conformance_test_case('rotate')
def test_rotate(surface):
    """Simple rotation tests"""
    obj = _make_object()

    surface.blit(obj, (20, 20))
    obj1 = transform.rotate(obj, 90)
    surface.blit(obj1, (80, 20))
    obj1 = transform.rotate(obj, 180)
    surface.blit(obj1, (160, 20))
    obj1 = transform.rotate(obj, 270)
    surface.blit(obj1, (240, 20))
    obj1 = transform.rotate(obj, -90)
    surface.blit(obj1, (320, 20))
    obj1 = transform.rotate(obj, -180)
    surface.blit(obj1, (480, 20))
    x = 20
    y = 100
    for angle in range(1, 200, 7):
        obj1 = transform.rotate(obj, angle)
        surface.blit(obj1, (x, y))
        x += obj1.get_width() + 5
        if x > 650:
            y += 2*obj.get_height() + 5
            x = 20


@conformance_test_case('chop')
def test_chop(surface):
    """Simple tests of transform.chop"""
    obj = _make_object()
    obj1 = transform.chop(obj, (10, 10, 10, 10))
    obj2 = transform.chop(obj, (10, 10, 20, 20))
    obj3 = transform.chop(obj, (0, 0, 100, 100))
    obj4 = transform.chop(obj, (5, 5, 50, 50))

    surface.blit(obj, (20, 20))
    surface.blit(obj1, (80, 20))
    surface.blit(obj2, (160, 20))
    surface.blit(obj3, (240, 20))
    surface.blit(obj4, (320, 20))

    obj_sub = obj.subsurface((20, 20, 20, 15))
    obj1 = transform.chop(obj_sub, (10, 10, 10, 10))
    obj2 = transform.chop(obj_sub, (10, 10, 0, 0))
    # Chop out everything
    obj3 = transform.chop(obj_sub, (0, 0, 20, 15))
    surface.blit(obj_sub, (20, 190))
    surface.blit(obj1, (80, 190))
    surface.blit(obj2, (160, 190))
    surface.blit(obj3, (190, 190))


@conformance_test_case('chop_subsurface')
def test_chop_subsurface(surface):
    """Test transform.chop with a subsurface as the source"""
    obj = _make_object()
    surface.blit(obj, (20, 20))
    obj_sub = obj.subsurface((20, 20, 20, 15))
    obj1 = transform.chop(obj_sub, (10, 10, 10, 10))
    obj2 = transform.chop(obj_sub, (10, 10, 0, 0))
    # Chop out everything
    obj3 = transform.chop(obj_sub, (0, 0, 20, 15))
    surface.blit(obj_sub, (20, 190))
    surface.blit(obj1, (80, 190))
    surface.blit(obj2, (160, 190))
    surface.blit(obj3, (190, 190))


# rotozoom only works with 32-bit surfaces.
@conformance_test_case('rotozoom', depths=(32,))
def test_rotozoom(surface):
    obj = _make_object()
    x = 20
    y = 20
    space = obj.get_height()
    for angle in range(1, 200, 14):
        for scale in range(5, 20, 3):
            obj1 = transform.rotozoom(obj, angle, scale / 10.0)
            surface.blit(obj1, (x, y))
            x += obj1.get_width() + 5
            space = max(space, obj1.get_height())
            if x > 650:
                y += space + 5
                x = 20
