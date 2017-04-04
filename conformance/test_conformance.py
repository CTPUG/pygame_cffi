#!/usr/bin/env python
# test_conformance - conformance testing for pygame_cffi
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

from conf_tests import conformance_tests, test_conformance
import os
import sys
import pygame

if not os.path.exists('results'):
    print("results dir doesn't exist - please generate the "
          "test images")
    sys.exit(1)

# Far from the smartest test for this, but good enough for my purposes
if not hasattr(pygame, '_sdl'):
    # If you want to override this, do so manually
    print("This looks like the pygame module. Please test the images"
          " with pygame_cffi.")
    sys.exit(1)

if '--verbose' in sys.argv:
    verbose = True
else:
    verbose = False

passed = True
failed = 0
run = 0
for test_func in conformance_tests:
    run += 1
    if not test_conformance(test_func, verbose):
        failed += 1
        passed = False

if not passed:
    print("FAILURE: %d out of %d tests failed" % (failed, run))
    sys.exit(1)
else:
    print("SUCCESS: %d tests succeeded" % run)

sys.exit(0)
