# Helper functions for the conformance tests
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
from __future__ import print_function

from pygame import surface, image
from pygame.locals import SRCALPHA


def create_surface():
    """Create a suitable 800x600 pygame surface for the test cases."""
    surf = surface.Surface((800, 600), depth=32, flags=SRCALPHA)
    surf.fill((0, 0, 0, 0xff))
    return surf


def test_conformance(test_name, test_func):
    """Run the test case and compare the resulting surface to the
       existing test case."""
    test_surf = create_surface()
    try:
        test_func(test_surf)
    except NotImplementedError:
        # Don't fail completely on not implemented functions
        pass
    imgname = 'results/test_%s.png' % test_name
    image.save(test_surf, imgname)
    diffname = 'results/diff_%s.png' % test_name
    orig_name = 'results/gen_%s.png' % test_name
    orig_surf = image.load(orig_name)
    # sanity check
    assert orig_surf.get_size() == test_surf.get_size()
    differences = False
    diff_surf = create_surface()
    # Pixel by pixel comparison.
    # This is slow, but avoids extra dependancies
    from pygame.surflock import locked
    orig_surf = orig_surf.convert(test_surf)
    with locked(orig_surf._c_surface):
        with locked(test_surf._c_surface):
            for x in range(800):
                for y in range(600):
                    point = (x, y)
                    if orig_surf._get_at(x, y) != test_surf._get_at(x, y):
                        differences = True
                        # Flag as pure white for easier visual inspection
                        diff_surf.set_at(point, (255, 255, 255, 255))
    if differences:
        print("conformance test %s FAILED.\n"
              "  Difference saved to %s" % (test_name, diffname))
        image.save(diff_surf, diffname)
    else:
        print("conformance test %s passed" % test_name)


def gen_test_image(test_name, test_func):
    """Run the test case and save the resulting test_surf."""
    test_surf = create_surface()
    test_func(test_surf)
    imgname = 'results/gen_%s.png' % test_name
    image.save(test_surf, imgname)
    print('completed %s. Result saved to %s' % (test_name, imgname))
