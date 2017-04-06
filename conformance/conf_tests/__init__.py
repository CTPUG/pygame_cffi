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

import argparse

from .helpers import gen_test_image, test_conformance, conformance_test_case

from . import test_lines
from . import test_transforms
from . import test_shapes
from . import test_surface
from . import test_blending
from . import test_smoothscale


def cmd_args(description):
    """Argument parser for the gen_conformannce and test_conformance
       scripts."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--verbose', action="store_true",
                        help="Verbosely list the tests run")
    parser.add_argument('--list-tests', action="store_true",
                        help="list all the test cases")
    parser.add_argument('--run-tests', default='', type=str,
                        help="Only run the specified tests"
                             " (seperate multiple tests by commas)")
    opts = parser.parse_args()
    if opts.run_tests:
        opts.filter = set(opts.run_tests.split(','))
    else:
        opts.filter = None
    return opts


def list_tests():
    print("Known test cases")
    for test in conformance_test_case.get_tests():
        print(" * %s" % test._filename)


def conformance_tests(test_filter):
    """Return the tests to run"""
    all_tests = conformance_test_case.get_tests()
    if test_filter:
        test_names = set([x._filename for x in all_tests])
        missing = test_filter - test_names
        if missing:
            raise RuntimeError("Unrecognised tests: %s" % sorted(missing))
        return [x for x in all_tests if x._filename in test_filter]
    else:
        return all_tests


__all__ = [conformance_tests, gen_test_image, test_conformance]
