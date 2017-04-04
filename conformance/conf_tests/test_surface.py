# test surfaces
# Copyright (C) 2014  Gert Burger
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
"""Simple tests for surfaces"""

from pygame import draw

from .helpers import conformance_test_case


@conformance_test_case('scroll')
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
