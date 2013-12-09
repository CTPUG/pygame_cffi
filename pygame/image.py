""" The pygame image module """

from pygame._sdl import sdl, ffi, locked
from pygame.surface import Surface
from pygame._error import SDLError


def get_extended():
    # Only correct if we always require SDL_image
    return True


def load_extended(filename, namehint=""):
    if isinstance(filename, basestring):
        c_surface = sdl.IMG_Load(filename)
        if not c_surface:
            raise SDLError.from_sdl_error()
        return Surface._from_sdl_surface(c_surface)
    raise NotImplementedError("TODO: Load from file objects")


def load_basic(filename, namehint=""):
    # Will we need this, if we're always requiring SDL_image?
    pass


def load(filename, namehint=""):
    if get_extended():
        return load_extended(filename, namehint)
    else:
        return load_basic(filename, namehint)


def fromstring(string, (w, h), format, flipped=False):
    assert format == "RGB"
    if len(string) != w * h * 3:
        raise ValueError("String length does not equal format and "
                         "resolution size")
    surf = sdl.SDL_CreateRGBSurface(0, w, h, 24, 0xff, 0xff << 8,
                                    0xff << 16, 0)
    if not surf:
        raise SDLError.from_sdl_error()
    with locked(surf):
        pixels = ffi.cast("char*", surf.pixels)
        src_byte = 0
        for y in range(h):
            dest = surf.pitch * y
            pixels[dest:dest+3*w] = string[src_byte:src_byte+3*w]
            src_byte += 3*w
    return Surface._from_sdl_surface(surf)
