# pygame_cffi - a cffi implementation of the pygame library
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

""" XXX """

from pygame._error import SDLError
from pygame._sdl import sdl


# TODO: prep and unprep surface


class locked(object):

    def __init__(self, c_surface):
        self.c_surface = c_surface

    def __enter__(self):
        res = sdl.SDL_LockSurface(self.c_surface)
        if res == -1:
            raise SDLError.from_sdl_error()

    def __exit__(self, *args):
        sdl.SDL_UnlockSurface(self.c_surface)
