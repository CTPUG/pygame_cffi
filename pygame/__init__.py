""" XXX: fish """

from pygame.color import Color
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.constants import *
from pygame import (
    display, color, surface, time, event, constants, sprite,
    mouse, locals, image, transform, pkgdata, font, mixer,
    cursors, key, draw
)
from pygame.base import (
    init, quit, HAVE_NEWBUF, get_sdl_version, get_sdl_byteorder,
    register_quit
)
from pygame._error import get_error, set_error, SDLError

# map our exceptions on pygame's default
error = SDLError
