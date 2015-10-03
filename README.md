pygame_cffi
===========

A cffi-based SDL wrapper that copies the pygame API.

We copy various code and API ideas from pygame, so we inherit pygame's
LGPL v2.1, or later license.

Discussion
**********

We have a Google Group: https://groups.google.com/forum/#!forum/pygame-cffi.
Any pygame-cffi discussion welcome!

Installation
************

1. Install the requirements listed below. On a Debian-based system, all
   requirements can be installed using `sudo apt-get build-dep pygame`
   (pygame_cffi requires most of the pygame dependencies).
2. `pip install pygame_cffi`

Requirements
************

* libjpeg-dev
* libpng-dev
* libsdl1.2-dev
* libsdl-image1.2-dev
* libsdl-mixer1.2-dev
* libsdl-ttf2.0-dev

Local Development
*****************

1. Install dependencies (probably in a virtualenv)
2. Run cffi_builders/build.py
3. Hack

Running Tests
*************

* Upstream pygame unit tests: `python -m test`
* Conformance between pygame and pygame_cffi: See `conformance/README`
* pygame_cffi functionality tests are apps in the `tests` directory
