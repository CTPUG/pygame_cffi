""" The pygame rwobject module for IO using SDL_RWops """

from pygame._sdl import sdl
from pygame._error import SDLError
from pygame.compat import bytes_, filesystem_encode, unicode_


def rwops_encode_file_path(filepath):
    if isinstance(filepath, unicode_):
        filepath = filesystem_encode(filepath)
    if isinstance(filepath, bytes_):
        if b'\x00' in filepath:
            raise SDLError("File path '%.1024s' contains null "
                           "characters" % filepath)
        return filepath
    raise SDLError("filepath argument needs to be a unicode or str value")


def rwops_from_file(fileobj):
    rwops = sdl.SDL_RWFromFP(fileobj, 0)
    if not rwops:
        raise SDLError.from_sdl_error()
    return rwops


def rwops_from_file_path(filename, mode='r'):
    mode = mode.encode('ascii')
    rwops = sdl.SDL_RWFromFile(filename, mode)
    if not rwops:
        raise SDLError.from_sdl_error()
    return rwops
