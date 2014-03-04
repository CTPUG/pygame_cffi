""" The pygame imageext module """

from os import path

from pygame._sdl import sdl, ffi
from pygame._error import SDLError
from pygame.rwobject import (rwops_encode_file_path, rwops_from_file,
                             rwops_from_file_path)
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
            raise TypeError("file argument must be a valid path "
                            "string or file object")
    if not c_surface:
        raise SDLError(ffi.string(sdl.IMG_GetError()))
    return Surface._from_sdl_surface(c_surface)


def save_extended(surface, filename):
    """ save(Surface, filename) -> None
    save an image to disk
    """
    surf = surface._c_surface
    if surf.flags & sdl.SDL_OPENGL:
        raise NotImplementedError()
    if not isinstance(filename, basestring):
        raise TypeError("Expected a string for the file arugment: got %s"
                        % type(filename).__name__)

    filename = rwops_encode_file_path(filename)
    fn_normalized = filename.lower()
    # TODO: prep/unprep surface
    if fn_normalized.endswith('jpg') or fn_normalized.endswith('jpeg'):
        # save as JPEG
        result = save_jpg(surf, filename)
    elif fn_normalized.endswith('png'):
        # save as PNG
        result = save_png(surf, filename)
    else:
        raise SDLError("Unrecognized image type")
    if result == -1:
        raise SDLError.from_sdl_error()


def save_jpg(surf, filename):
    raise SDLError("No support for jpg compiled in")


def save_png(surf, filename):
    raise SDLError("No support for png compiled in")
