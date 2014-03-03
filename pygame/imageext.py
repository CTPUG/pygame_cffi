""" The pygame imageext module """

from pygame._sdl import sdl, ffi
from pygame.surface import Surface, locked
from pygame._error import SDLError


def load_extended(filename, namehint=""):
    if isinstance(filename, basestring):
        c_surface = sdl.IMG_Load(filename)
        if not c_surface:
            raise SDLError.from_sdl_error()
        return Surface._from_sdl_surface(c_surface)
    raise NotImplementedError("TODO: Load from file objects")


def save_extended(surf, filename):
    """ save(Surface, filename) -> None
    save an image to disk
    """
    raise NotImplementedError()
