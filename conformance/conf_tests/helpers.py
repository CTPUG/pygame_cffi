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


DEPTHS = (8, 16, 24, 32)


class conformance_test_case(object):
    """Tacks the appropriate attributes onto the test function"""

    registry = {}

    def __init__(self, test_file_name, depths=DEPTHS):
        self.test_file_name = test_file_name
        self.depths = depths

    def __call__(self, f):
        def wrapper(surface):
            return f(surface)
        wrapper._filename = self.test_file_name
        wrapper._supported_depths = self.depths
        if self.test_file_name in self.registry:
            raise RuntimeError('Duplicate file name %s. Used by %s and %s' %
                               (self.test_file_name, f,
                                self.registry[self.test_file_name]))
        else:
            self.registry[self.test_file_name] = f
        return wrapper


def create_surface(depth):
    """Create a suitable 800x600 pygame surface for the test cases."""
    if depth == 32:
        surf = surface.Surface((800, 600), depth=32, flags=SRCALPHA)
        surf.fill((0, 0, 0, 0xff))
    elif depth in (16, 24):
        surf = surface.Surface((800, 600), depth=24)
        surf.fill((0, 0, 0, 0xff))
    elif depth == 8:
        surf = surface.Surface((800, 600), depth=8)
        surf.fill(0)
    else:
        raise RuntimeError('Unsupported bit depth for tests: %d' % depth)
    return surf


def test_conformance(test_func, verbose=False):
    """Run the test case and compare the resulting surface to the
       existing test case."""
    test_name = test_func._filename
    passed = True
    for depth in DEPTHS:
        if depth not in test_func._supported_depths:
            continue
        test_surf = create_surface(depth)
        try:
            test_func(test_surf)
        except NotImplementedError:
            # Don't fail completely on not implemented functions
            pass
        except Exception as e:
            # Fail on other exceptions
            print('%s at depth %d Failed with exception %s' % (test_name,
                                                               depth,
                                                               e))
            passed = False
            continue
        imgname = 'results/test_%d_%s.png' % (depth, test_name)
        image.save(test_surf, imgname)
        diffname = 'results/diff_%d_%s.png' % (depth, test_name)
        orig_name = 'results/gen_%d_%s.png' % (depth, test_name)
        orig_surf = image.load(orig_name)
        # sanity check
        assert orig_surf.get_size() == test_surf.get_size()
        differences = False
        diff_surf = create_surface(depth)
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
            if verbose:
                print("conformance test %s FAILED for depth %d.\n"
                      "  Difference saved to %s" % (test_name, depth,
                                                    diffname))
            image.save(diff_surf, diffname)
            passed = False
        else:
            if verbose:
                print("conformance test %s passed for depth %d" % (test_name,
                                                                   depth))
    return passed


def gen_test_image(test_func, verbose=False):
    """Run the test case and save the resulting test_surf."""
    test_name = test_func._filename
    for depth in DEPTHS:
        if depth not in test_func._supported_depths:
            continue
        test_surf = create_surface(depth)
        test_func(test_surf)
        imgname = 'results/gen_%d_%s.png' % (depth, test_name)
        image.save(test_surf, imgname)
        if verbose:
            print('completed %s at depth %d. Result saved to %s' % (test_name,
                                                                    depth,
                                                                    imgname))
