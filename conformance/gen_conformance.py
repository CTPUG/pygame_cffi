#!/usr/bin/env python
from __future__ import print_function

from conf_tests import conformance_tests, gen_test_image
import os
import sys
import pygame

if hasattr(pygame, '_sdl'):
    # If you want to override this, do so manually
    print ("This looks like the pygame_cffi module. Please generate the images"
           "with pygame.")
    sys.exit(1)

if not os.path.exists('results'):
   os.makedirs('results')

for test_name, test_func in conformance_tests.items():
   gen_test_image(test_name, test_func)
