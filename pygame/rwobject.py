""" The pygame rwobject module for IO using SDL_RWops """

from pygame._sdl import ffi, sdl
from pygame._error import SDLError
from pygame.compat import bytes_, filesystem_encode, unicode_

# Can't use weakref, since we need to hold a reference to
# the handle until all the operations are done.
__localhandles = set()


# Callback helpers for rwops_from_file
@ffi.callback("int (SDL_RWops* context, int offset, int whence)")
def obj_seek(context, offset, whence):
    fileobj = ffi.from_handle(context.hidden.unknown.data1)
    if not hasattr(fileobj, 'tell') or not hasattr(fileobj, 'seek'):
        return -1
    # whence = 1 => SEEK_CUR, from python docs
    if offset != 0 or whence != 1:
        # We're actually being called to do a seek
        fileobj.seek(offset, whence)
    return fileobj.tell()


@ffi.callback("int (SDL_RWops* context, void* output, int size, int maxnum)")
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


@ffi.callback(
    "int (SDL_RWops* context, const void* input, int size, int maxnum)")
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


@ffi.callback("int (SDL_RWops* context)")
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


def rwops_from_file(fileobj):
    try:
        # We try use the SDL helper first, since
        # it's the simplest code path
        rwops = sdl.SDL_RWFromFP(fileobj, 0)
    except (TypeError, IOError):
        # Construct a suitable rwops object
        rwops = sdl.SDL_AllocRW()
        handle = ffi.new_handle(fileobj)
        rwops.hidden.unknown.data1 = handle
        __localhandles.add(handle)
        rwops.seek = obj_seek
        rwops.read = obj_read
        rwops.write = obj_write
        rwops.close = obj_close
    if not rwops:
        raise SDLError.from_sdl_error()
    return rwops


def rwops_from_file_path(filename, mode='r'):
    mode = mode.encode('ascii')
    rwops = sdl.SDL_RWFromFile(filename, mode)
    if not rwops:
        raise SDLError.from_sdl_error()
    return rwops
