""" The pygame image module """

from pygame._sdl import sdl, ffi
from pygame.surface import Surface
from pygame.error import SDLError


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
