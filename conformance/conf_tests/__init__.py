# The conf_tests module
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

from .helpers import gen_test_image, test_conformance, conformance_test_case

import test_lines
import test_transforms
import test_shapes
import test_surface
import test_blending
import test_smoothscale


class dummy(object):
    def __init__(self):
        self.filter = None
        self.verbose = True


def cmd_args(argv):
    """Argument parser for the gen_conformannce and test_conformance
       scripts."""
    return dummy()


def conformance_tests(test_filter):
    """Return the tests to run"""
    return conformance_test_case.get_tests()


__all__ = [conformance_tests, gen_test_image, test_conformance]
