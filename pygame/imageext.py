""" The pygame imageext module """

from os import path

from pygame._sdl import sdl, ffi
from pygame._error import SDLError
from pygame.rwobject import rwops_encode_file_path, rwops_from_file
from pygame.surface import Surface, locked


def load_extended(filename, namehint=""):
    try:
        filename = rwops_encode_file_path(filename)
        c_surface = sdl.IMG_Load(filename)
    except TypeError:
        # filename is not a string, try as file object
        try:
            rwops = rwops_from_file(filename)
            if namehint:  
                name, ext = path.splitext(namehint)
            else:
                name, ext = path.splitext(filename.name)
            if len(ext) == 0:
                ext = name
            c_surface = sdl.IMG_LoadTyped_RW(rwops, 1, ext)
        except TypeError:
            raise TypeError("file argument must be a valid path string or file object")
    if not c_surface:
        raise SDLError(sdl.IMG_GetError())
    return Surface._from_sdl_surface(c_surface)


def save_extended(surf, filename):
    """ save(Surface, filename) -> None
    save an image to disk
    """
    raise NotImplementedError()
