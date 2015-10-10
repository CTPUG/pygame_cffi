""" SDL errors.def
"""

from pygame._sdl import sdl, ffi


class SDLError(Exception):
    """SDL error."""

    @classmethod
    def from_sdl_error(cls):
        return cls(ffi.string(sdl.SDL_GetError()))


def unpack_rect(rect):
    """Unpack the size and raise a type error if needed."""
    if (not hasattr(rect, '__iter__') or
            len(rect) != 2 or
            not isinstance(rect[0], int) or
            not isinstance(rect[1], int)):
        raise TypeError("expected tuple of two integers but got %r"
                        % type(rect))
    return rect


def get_error():
    err = ffi.string(sdl.SDL_GetError())
    if not isinstance(err, str):
        return err.decode('utf8')
    return err


def set_error(errmsg):
    if not isinstance(errmsg, bytes):
        errmsg = errmsg.encode('utf8')
    sdl.SDL_SetError(errmsg)
