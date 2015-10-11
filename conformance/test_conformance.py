#!/usr/bin/env python
from __future__ import print_function

from conf_tests import conformance_tests, test_conformance
import os
import sys
import pygame

if not os.path.exists('results'):
   print ("results dir doesn't exist - please generate the "
          "test images")
   sys.exit(1)

# Far from the smartest test for this, but good enough for my purposes
if not hasattr(pygame, '_sdl'):
    # If you want to override this, do so manually
    print ("This looks like the pygame module. Please test the images"
           "with pygame_cffi.")
    sys.exit(1)

for test_name, test_func in conformance_tests.items():
   test_conformance(test_name, test_func)
