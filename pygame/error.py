""" SDL errors.def
"""

from pygame._sdl import sdl, ffi


class SDLError(Exception):
    """SDL error."""

    @classmethod
    def from_sdl_error(cls):
        return cls(ffi.string(sdl.SDL_GetError()))
