# pygame_cffi

[![Build Status](https://img.shields.io/travis/CTPUG/pygame_cffi.svg)](https://travis-ci.org/CTPUG/pygame_cffi)
[![PyPI](https://img.shields.io/pypi/v/pygame_cffi.svg)](https://pypi.python.org/pypi/pygame_cffi)

A cffi-based SDL wrapper that copies the pygame API.

We copy various code and API ideas from pygame, so we inherit pygame's
LGPL v2.1, or later license.

## Discussion

We have a Google Group: https://groups.google.com/forum/#!forum/pygame-cffi.
Any pygame-cffi discussion welcome!

## Installation

1. Install the requirements listed below. On a Debian-based system, all
   requirements can be installed using `sudo apt-get build-dep pygame`
   (pygame_cffi requires most of the pygame dependencies).
2. `pip install pygame_cffi`

## Requirements

* libjpeg-dev
* libpng-dev
* libsdl1.2-dev
* libsdl-image1.2-dev
* libsdl-mixer1.2-dev
* libsdl-ttf2.0-dev

## Local Development

1. Install dependencies (probably in a virtualenv)
2. Run `cffi_builders/build.py`
3. Hack

## Running Tests

* Upstream pygame unit tests: `python -m test`
 * Tests that are known to fail on pygame_cffi are marked as expected
   failures. To see these failures, pass the `--expected-failures`
   argument.
* Conformance between pygame and pygame_cffi: See `conformance/README`
* pygame_cffi functionality example apps are in the `demos` directory
