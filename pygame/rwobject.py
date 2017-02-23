""" The pygame rwobject module for IO using SDL_RWops """
import sys

from pygame._sdl import ffi, sdl
from pygame._error import SDLError
from pygame.compat import bytes_, filesystem_encode, unicode_

# Can't use weakref, since we need to hold a reference to
# the handle until all the operations are done.
__localhandles = set()


# Callback helpers for rwops_from_file
@ffi.def_extern()
def obj_seek(context, offset, whence):
    fileobj = ffi.from_handle(context.hidden.unknown.data1)
    if not hasattr(fileobj, 'tell') or not hasattr(fileobj, 'seek'):
        return -1
    # whence = 1 => SEEK_CUR, from python docs
    if offset != 0 or whence != 1:
        # We're actually being called to do a seek
        fileobj.seek(offset, whence)
    return fileobj.tell()


@ffi.def_extern()
def obj_read(context, output, size, maxnum):
    fileobj = ffi.from_handle(context.hidden.unknown.data1)
    if not hasattr(fileobj, 'read'):
        return -1
    data = fileobj.read(size * maxnum)
    if not data:
        return -1
    retval = len(data)
    ffi.memmove(output, data, retval)
    retval = retval // size
    return retval


@ffi.def_extern()
def obj_write(context, input, size, maxnum):
    fileobj = ffi.from_handle(context.hidden.unknown.data1)
    if not hasattr(fileobj, 'write'):
        return -1
    data = ffi.buffer(input, size*maxnum)
    try:
        fileobj.write(data)
    except IOError:
        return -1
    return size*maxnum


@ffi.def_extern()
def obj_close(context):
    fileobj = ffi.from_handle(context.hidden.unknown.data1)
    retval = 0
    if hasattr(fileobj, 'close'):
        if fileobj.close():
            retval = -1
    __localhandles.discard(context.hidden.unknown.data1)
    sdl.SDL_FreeRW(context)
    return retval


def rwops_encode_file_path(filepath):
    if isinstance(filepath, unicode_):
        filepath = filesystem_encode(filepath)
    if isinstance(filepath, bytes_):
        if b'\x00' in filepath:
            raise SDLError("File path '%.1024s' contains null "
                           "characters" % filepath)
        return filepath
    raise SDLError("filepath argument needs to be a unicode or str value")


def _lib_rwops_from_file(fileobj):
    """create rwops from file usings our helper functions."""
    rwops = sdl.SDL_AllocRW()
    handle = ffi.new_handle(fileobj)
    rwops.hidden.unknown.data1 = handle
    __localhandles.add(handle)
    rwops.seek = sdl.obj_seek
    rwops.read = sdl.obj_read
    rwops.write = sdl.obj_write
    rwops.close = sdl.obj_close
    return rwops


def _win_rwops_from_file(fileobj):
    """Windows compatible implementation of rwops_from_file."""
    # sdl.SDL_RWFromFP doesn't setup the correct handlers on
    # windows, so we fall back to our helpers
    rwops = _lib_rwops_from_file(fileobj)
    if not rwops:
        raise SDLError.from_sdl_error()
    return rwops


def _unix_rwops_from_file(fileobj):
    """Non-windows implementation of rwops_from_file."""
    try:
        # We try use the SDL helper first, since
        # it's the simplest code path
        rwops = sdl.SDL_RWFromFP(fileobj, 0)
    except (TypeError, IOError):
        # Construct a suitable rwops object
        rwops = _lib_rwops_from_file(fileobj)
    if not rwops:
        raise SDLError.from_sdl_error()
    return rwops


if sys.platform.startswith('win'):
    rwops_from_file = _win_rwops_from_file
else:
    rwops_from_file = _unix_rwops_from_file


def rwops_from_file_path(filename, mode='r'):
    mode = mode.encode('ascii')
    rwops = sdl.SDL_RWFromFile(filename, mode)
    if not rwops:
        raise SDLError.from_sdl_error()
    return rwops
