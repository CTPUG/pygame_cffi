# pygame_cffi - a cffi implementation of the pygame library
# Copyright (C) 2013  Simon Cross
# Copyright (C) 2013  Maciej Fijalkowski
# Copyright (C) 2013  Jeremy Thurgood
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

from pygame._sdl_c import ffi
from pygame._sdl_c import lib as sdl


def get_sdl_version():
    """ get_sdl_version() -> major, minor, patch
    get the version number of SDL
    """
    v = sdl.SDL_Linked_Version()
    return (v.major, v.minor, v.patch)


def get_sdl_byteorder():
    return sdl.SDL_BYTEORDER
