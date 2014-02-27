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
