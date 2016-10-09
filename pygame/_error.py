""" SDL errors.def
"""

from pygame._sdl import sdl, ffi
from numbers import Number


class SDLError(Exception):
    """SDL error."""

    @classmethod
    def from_sdl_error(cls):
        return cls(ffi.string(sdl.SDL_GetError()))


def unpack_rect(rect):
    """Unpack the size and raise a type error if needed."""
    # This is as liberal as pygame when used for pygame.surface, but
    # more liberal for pygame.display. I don't think the inconsistency
    # matters
    if (not hasattr(rect, '__iter__') or
            len(rect) != 2 or
            not isinstance(rect[0], Number) or
            not isinstance(rect[1], Number)):
        raise TypeError("expected tuple of two integers but got %r"
                        % type(rect))
    # We'll throw a conversion TypeError here if someone is using a
    # complex number, but so does pygame.
    return int(rect[0]), int(rect[1])


def get_error():
    err = ffi.string(sdl.SDL_GetError())
    if not isinstance(err, str):
        return err.decode('utf8')
    return err


def set_error(errmsg):
    if not isinstance(errmsg, bytes):
        errmsg = errmsg.encode('utf8')
    sdl.SDL_SetError(errmsg)
