# pygame_cffi - a cffi implementation of the pygame library
# Copyright (C) 2013  Maciej Fijalkowski
# Copyright (C) 2013  Simon Cross
# Copyright (C) 2013  Neil Muller
# Copyright (C) 2014  Rizmari Versfeld
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

""" XXX: fish """

from pygame.color import Color
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.constants import *
from pygame import (
    display, color, surface, time, event, constants, sprite,
    mouse, locals, image, transform, pkgdata, font, mixer,
    cursors, key, draw, joystick, math
)
from pygame.base import (
    init, quit, HAVE_NEWBUF, get_sdl_version, get_sdl_byteorder,
    register_quit
)
from pygame._error import get_error, set_error, SDLError
from pygame.mask import Mask
from pygame.version import ver, vernum, pygame_cffi_version

__version__ = ver

# map our exceptions on pygame's default
error = SDLError
