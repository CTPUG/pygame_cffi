# pygame_cffi - a cffi implementation of the pygame library
# Copyright (C) 2013  Maciej Fijalkowski
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

""" Mouse routines
"""

from pygame._error import SDLError
from pygame._sdl import sdl, ffi
from pygame.display import check_video


def get_pos():
    check_video()
    x = ffi.new("int[1]")
    y = ffi.new("int[1]")
    sdl.SDL_GetMouseState(x, y)
    return x[0], y[0]


def set_visible(toggle):
    check_video()
    if not isinstance(toggle, int):
        raise TypeError("expected int, got %s" % (toggle,))
    return sdl.SDL_ShowCursor(toggle)


def get_pressed():
    """ get_pressed() -> (button1, button2, button3)
    get the state of the mouse buttons
    """
    check_video()
    state = sdl.SDL_GetMouseState(ffi.NULL, ffi.NULL)
    return (int((state & sdl._pygame_SDL_BUTTON(1)) != 0),
            int((state & sdl._pygame_SDL_BUTTON(2)) != 0),
            int((state & sdl._pygame_SDL_BUTTON(3)) != 0))


def get_rel():
    """ get_rel() -> (x, y)
    get the amount of mouse movement
    """
    check_video()
    x, y = ffi.new('int*'), ffi.new('int*')
    sdl.SDL_GetRelativeMouseState(x, y)
    return x[0], y[0]


def set_pos(pos):
    """ set_pos([x, y]) -> None
    set the mouse cursor position
    """
    x, y = pos
    check_video()
    try:
        x = int(x)
        y = int(y)
        sdl.SDL_WarpMouse(x, y)
    except (ValueError, TypeError):
        raise "invalid position argument for set_pos"


def get_focused():
    """ get_focused() -> bool
    check if the display is receiving mouse input
    """
    check_video()
    return int(sdl.SDL_GetAppState() & sdl.SDL_APPMOUSEFOCUS != 0)


def set_cursor(size, hotspot, xormasks, andmasks):
    """ set_cursor(size, hotspot, xormasks, andmasks) -> None
    set the image for the system mouse cursor
    """
    check_video()

    spotx, spoty = int(hotspot[0]), int(hotspot[1])
    w, h = int(size[0]), int(size[1])
    if w % 8 != 0:
        raise ValueError("Cursor width must be divisible by 8")

    if not hasattr(xormasks, '__iter__') or not hasattr(andmasks, '__iter__'):
        raise TypeError("xormask and andmask must be sequences")
    if len(xormasks) != w * h / 8.0 or len(andmasks) != w * h / 8.0:
        raise ValueError("bitmasks must be sized width*height/8")
    try:
        xordata = ffi.new('uint8_t[]', [int(m) for m in xormasks])
        anddata = ffi.new('uint8_t[]', [int(andmasks[i]) for i
                                        in range(len(xormasks))])
    except (ValueError, TypeError):
        raise TypeError("Invalid number in mask array")
    except OverflowError:
        raise TypeError("Number in mask array is larger than 8 bits")

    cursor = sdl.SDL_CreateCursor(xordata, anddata, w, h, spotx, spoty)
    if not cursor:
        raise SDLError.from_sdl_error()
    lastcursor = sdl.SDL_GetCursor()
    sdl.SDL_SetCursor(cursor)
    sdl.SDL_FreeCursor(lastcursor)


def get_cursor():
    """ get_cursor() -> (size, hotspot, xormasks, andmasks)
    get the image for the system mouse cursor
    """
    check_video()
    cursor = sdl.SDL_GetCursor()
    if not cursor:
        raise SDLError.from_sdl_error()

    w = cursor.area.w
    h = cursor.area.h
    size = w * h / 8
    xordata = [int(cursor.data[i]) for i in range(size)]
    anddata = [int(cursor.mask[i]) for i in range(size)]
    return (w, h), (cursor.hot_x, cursor.hot_y), xordata, anddata
