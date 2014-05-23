pygame_cffi
===========

A cffi-based SDL wrapper that copies the pygame API.

We copy various code and API ideas from pygame, so we inherit pygame's LGPL v2.1
license.

Installation
************

pygame_cffi has not been packaged yet (coming soon). So the way to install is:

1. Clone this repo.
2. Install the requirements listed below. All requirements except CFFI can be installed using `sudo apt-get build-dep pygame` on a Debian-based distro (pygame_cffi requires most of the pygame dependencies).
3. Add the pygame_cffi directory to your Python path.

Requirements
************

* libjpeg-dev
* libpng-dev
* libsdl1.2-dev
* libsdl-image1.2-dev
* libsdl-mixer1.2-dev
* libsdl-ttf2.0-dev
* python-cffi
