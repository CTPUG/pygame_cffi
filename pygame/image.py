""" The pygame image module """

from os import path

from pygame._error import SDLError
from pygame._sdl import sdl, ffi, get_sdl_byteorder
from pygame._jpg import jpglib
from pygame._png import pnglib
from pygame.rwobject import (rwops_encode_file_path, rwops_from_file,
                             rwops_from_file_path)
from pygame.surface import Surface, locked, BYTE0, BYTE1, BYTE2


def load(filename, namehint=""):
    try:
        filename = rwops_encode_file_path(filename)
        c_surface = sdl.IMG_Load(filename)
    except SDLError:
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


def save(surface, filename):
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
    result = 0
    # TODO: prep/unprep surface
    if fn_normalized.endswith('bmp'):
        # save as BMP
        result = sdl.SDL_SaveBMP(surf, filename)
    elif fn_normalized.endswith('jpg') or fn_normalized.endswith('jpeg'):
        # save as JPEG
        result = save_jpg(surf, filename)
    elif fn_normalized.endswith('png'):
        # save as PNG
        result = save_png(surf, filename)
    else:
        # save as TGA
        result = save_tga(surf, filename, True)
    if result == -1:
        raise SDLError.from_sdl_error()


class opaque(object):
    '''
    Removes color key and alpha from surface so that
    copies are opaque.
    '''
    def __init__(self, c_surface):
        self.c_surface = c_surface
        self.flags = 0
        self.alpha = 0
        self.colorkey = 0

    def __enter__(self):
        self.flags = self.c_surface.flags & (sdl.SDL_SRCALPHA |
                                             sdl.SDL_SRCCOLORKEY)
        self.alpha = self.c_surface.format.alpha
        self.colorkey = self.c_surface.format.colorkey
        if self.flags & sdl.SDL_SRCALPHA:
            sdl.SDL_SetAlpha(self.c_surface, 0, 255)
        if self.flags & sdl.SDL_SRCCOLORKEY:
            sdl.SDL_SetColorKey(self.c_surface, 0,
                                self.c_surface.format.colorkey)

    def __exit__(self, *args):
        if self.flags & sdl.SDL_SRCALPHA:
            sdl.SDL_SetAlpha(self.c_surface, sdl.SDL_SRCALPHA, self.alpha)
        if self.flags & sdl.SDL_SRCCOLORKEY:
            sdl.SDL_SetColorKey(self.c_surface, sdl.SDL_SRCCOLORKEY,
                                self.colorkey)


def save_tga(surf, filename, rle=False):
    rwops = rwops_from_file_path(filename, 'wb')
    result = sdl._pygame_SaveTGA_RW(surf, rwops, 1 if rle else 0)
    sdl.SDL_RWclose(rwops)
    return result


def save_jpg(surf, filename):
    if (surf.format.BytesPerPixel == 3
            and not (surf.flags & sdl.SDL_SRCALPHA)
            and surf.format.Rshift == 0):
        ss_surf = surf
    else:
        if get_sdl_byteorder() == sdl.SDL_LIL_ENDIAN:
            rmask, gmask, bmask, amask = 0xff, 0xff00, 0xff0000, 0xff000000
        else:
            rmask, gmask, bmask, amask = 0xff00, 0xff, 0xff0000, 0xff000000
        ss_surf = sdl.SDL_CreateRGBSurface(sdl.SDL_SWSURFACE, surf.w, surf.h,
                                           24, rmask, gmask, bmask, amask)
        if not ss_surf:
            return -1
        rect = ffi.new('SDL_Rect*')
        rect.w = surf.w
        rect.h = surf.h
        sdl.SDL_BlitSurface(surf, rect, ss_surf, ffi.NULL)

    ss_rows = ffi.new('unsigned char*[]', surf.h)
    ss_pixels = ffi.cast('unsigned char*', ss_surf.pixels)
    for i in range(surf.h):
        ss_rows[i] = ss_pixels + i * ss_surf.pitch
    err_msg = ffi.new('char**')
    result = jpglib.write_jpeg(filename, ss_rows, surf.w, surf.h, 85, err_msg)

    if ss_surf is not surf:
        sdl.SDL_FreeSurface(ss_surf)
    if result == -1:
        raise IOError("JPGError: %s" % ffi.string(err_msg[0]))
    return result


def save_png(surf, filename):
    alpha = bool(surf.format.Amask)
    if get_sdl_byteorder() == sdl.SDL_LIL_ENDIAN:
        rmask, gmask, bmask, amask = 0xff, 0xff00, 0xff0000, 0xff000000
    else:
        rmask, gmask, bmask, amask = 0xff00, 0xff0000, 0xff, 0x000000ff
    ss_surf = sdl.SDL_CreateRGBSurface(sdl.SDL_SWSURFACE | sdl.SDL_SRCALPHA,
                                       surf.w, surf.h, 32 if alpha else 24,
                                       rmask, gmask, bmask, amask)
    if not ss_surf:
        return -1
    with opaque(surf):
        rect = ffi.new('SDL_Rect*')
        rect.w = surf.w
        rect.h = surf.h
        sdl.SDL_BlitSurface(surf, rect, ss_surf, ffi.NULL)

    ss_rows = ffi.new('unsigned char*[]', surf.h)
    ss_pixels = ffi.cast('unsigned char*', ss_surf.pixels)
    for i in range(surf.h):
        ss_rows[i] = ss_pixels + i * ss_surf.pitch
    err_msg = ffi.new('char**')
    result = pnglib.write_png(filename, ss_rows, surf.w, surf.h,
                              (pnglib.PNG_COLOR_TYPE_RGB_ALPHA if alpha else
                               pnglib.PNG_COLOR_TYPE_RGB), 8, err_msg)

    sdl.SDL_FreeSurface(ss_surf)
    if result == -1:
        raise IOError("PNGError: %s" % ffi.string(err_msg[0]))
    return result


def fromstring(string, (w, h), format, flipped=False):
    if w < 1 or h < 1:
        raise ValueError("Resolution must be positive values")

    if format == "P":
        if len(string) != w * h:
            raise ValueError("String length does not equal format and "
                             "resolution size")
        surf = sdl.SDL_CreateRGBSurface(0, w, h, 8, 0, 0, 0, 0)
        if not surf:
            raise SDLError.from_sdl_error()
        with locked(surf):
            pixels = ffi.cast('char*', surf.pixels)
            for y in range(h):
                dest =  surf.pitch * y
                src_start = (h - 1 - y) * w if flipped else y * w
                pixels[dest:dest + w] = string[src_start:src_start + w]

    elif format == "RGB":
        if len(string) != w * h * 3:
            raise ValueError("String length does not equal format and "
                             "resolution size")
        surf = sdl.SDL_CreateRGBSurface(0, w, h, 24, 0xff, 0xff << 16,
                                        0xff << 8, 0)
        if not surf:
            raise SDLError.from_sdl_error()
        with locked(surf):
            pixels = ffi.cast("char*", surf.pixels)
            for y in range(h):
                dest = surf.pitch * y
                src_start = (h - 1 - y) * w * 3 if flipped else y * w * 3
                row = string[src_start:src_start + w * 3]
                for x in range(0, w * 3, 3):
                    # BYTE0, BYTE1 and BYTE2 are determined by byte order
                    pixels[dest + x + BYTE0] = row[x + BYTE0]
                    pixels[dest + x + BYTE1] = row[x + BYTE1]
                    pixels[dest + x + BYTE2] = row[x + BYTE2]

    elif format in ("RGBA", "RGBAX", "ARGB"):
        if len(string) != w * h * 4:
            raise ValueError("String length does not equal format and "
                             "resolution size")
        if format == "ARGB":
            if get_sdl_byteorder() == sdl.SDL_LIL_ENDIAN:
                rmask, gmask, bmask, amask = (0xff << 8, 0xff << 16,
                                              0xff << 24, 0xff)
            else:
                rmask, gmask, bmask, amask = (0xff << 16, 0xff << 8,
                                              0xff, 0xff << 24)
            surf = sdl.SDL_CreateRGBSurface(sdl.SDL_SRCALPHA, w, h, 32,
                                            rmask, gmask, bmask, amask)
        else:
            alphamult = format == "RGBA"
            if get_sdl_byteorder() == sdl.SDL_LIL_ENDIAN:
                rmask, gmask, bmask = 0xff, 0xff << 8, 0xff << 16
                amask = 0xff << 24 if alphamult else 0
            else:
                rmask, gmask, bmask = 0xff << 24, 0xff << 16, 0xff << 8
                amask = 0xff if alphamult else 0
            surf = sdl.SDL_CreateRGBSurface(sdl.SDL_SRCALPHA if alphamult
                                            else 0, w, h, 32, rmask, gmask,
                                            bmask, amask)
        if not surf:
            raise SDLError.from_sdl_error()
        with locked(surf):
            pixels = ffi.cast("char*", surf.pixels)
            for y in range(h):
                dest = surf.pitch * y
                src_start = (h - 1 - y) * w * 4 if flipped else y * w * 4
                pixels[dest:dest + w * 4]  = string[src_start:src_start + w * 4]

    else:
        raise ValueError("Unrecognized type of format")

    return Surface._from_sdl_surface(surf)


def tostring(surface, format, flipped=False):
    """ tostring(Surface, format, flipped=False) -> string
    transfer image to string buffer
    """
    surf = surface._c_surface
    if surf.flags & sdl.SDL_OPENGL:
        raise NotImplementedError()

    if format == "P":
        if surf.format.BytesPerPixel != 1:
            raise ValueError("Can only create \"P\" format data with "
                             "8bit Surfaces")
        with locked(surf):
            string = ffi.buffer(ffi.cast('char*', surf.pixels))[:]
    else:
        _tostring = globals().get('_tostring_%s' % format, None)
        if _tostring is None:
            raise ValueError("Unrecognized type of format")
        with locked(surf):
            string = _tostring(surf, flipped)
    return string


def _tostring_RGBA(surf, flipped, has_colorkey=True, argb=False):
    rmask, gmask, bmask, amask = (surf.format.Rmask,
                                  surf.format.Gmask,
                                  surf.format.Bmask,
                                  surf.format.Amask)
    rshift, gshift, bshift, ashift = (surf.format.Rshift,
                                      surf.format.Gshift,
                                      surf.format.Bshift,
                                      surf.format.Ashift)
    rloss, gloss, bloss, aloss = (surf.format.Rloss,
                                  surf.format.Gloss,
                                  surf.format.Bloss,
                                  surf.format.Aloss)
    bpp = surf.format.BytesPerPixel
    h, w = surf.h, surf.w
    colorkey = surf.format.colorkey
    if argb:
        has_colorkey = False
        ri, gi, bi, ai = 1, 2, 3, 0
    else:
        has_colorkey = (has_colorkey and surf.flags & sdl.SDL_SRCCOLORKEY
                        and not amask)
        ri, gi, bi, ai = 0, 1, 2, 3

    data = ffi.new('char[]', w * h * 4)
    if bpp == 1:
        pixels = ffi.cast('uint8_t*', surf.pixels)
        colors = surf.format.palette.colors
        for y in range(h):
            src_start = (h - 1 - y) * w if flipped \
                        else y * w
            for x in range(w):
                dest = 4 * (y * w + x)
                color = pixels[src_start + x]
                data[dest + ri] = chr(colors[color].r)
                data[dest + gi] = chr(colors[color].g)
                data[dest + bi] = chr(colors[color].b)
                if has_colorkey:
                    data[dest + ai] = chr(ffi.cast('char', color != colorkey) * 255)
                else:
                    data[dest + ai] = chr(255)
    elif bpp == 2:
        pixels = ffi.cast('uint16_t*', surf.pixels)
        for y in range(h):
            src_start = (h - 1 - y) * w if flipped \
                        else y * w
            for x in range(w):
                dest = 4 * (y * w + x)
                color = pixels[src_start + x]
                data[dest + ri] = chr(((color & rmask) >> rshift) << rloss)
                data[dest + gi] = chr(((color & gmask) >> gshift) << gloss)
                data[dest + bi] = chr(((color & bmask) >> bshift) << bloss)
                if has_colorkey:
                    data[dest + ai] = chr(ffi.cast('char', color != colorkey) * 255)
                else:
                    data[dest + ai] = chr((((color & amask) >> ashift) << aloss)
                                          if amask else 255)
    elif bpp == 3:
        pixels = ffi.cast('uint8_t*', surf.pixels)
        for y in range(h):
            src_start = (h - 1 - y) * surf.pitch if flipped \
                        else y * surf.pitch
            for x in range(w):
                dest = 4 * (y * w + x)
                color = (pixels[src_start + x * 3 + BYTE0] +
                         (pixels[src_start + x * 3 + BYTE1] << 8) +
                         (pixels[src_start + x * 3 + BYTE2] << 16))
                data[dest + ri] = chr(((color & rmask) >> rshift) << rloss)
                data[dest + gi] = chr(((color & gmask) >> gshift) << gloss)
                data[dest + bi] = chr(((color & bmask) >> bshift) << bloss)
                if has_colorkey:
                    data[dest + ai] = chr(ffi.cast('char', color != colorkey) * 255)
                else:
                    data[dest + ai] = chr((((color & amask) >> ashift) << aloss)
                                          if amask else 255)
    elif bpp == 4:
        pixels = ffi.cast('uint32_t*', surf.pixels)
        for y in range(h):
            src_start = (h - 1 - y) * w if flipped \
                        else y * w
            for x in range(w):
                dest = 4 * (y * w + x)
                color = pixels[src_start + x]
                data[dest + ri] = chr(((color & rmask) >> rshift) << rloss)
                data[dest + gi] = chr(((color & gmask) >> gshift) << gloss)
                data[dest + bi] = chr(((color & bmask) >> bshift) << bloss)
                if has_colorkey:
                    data[dest + ai] = chr(ffi.cast('char', color != colorkey) * 255)
                else:
                    data[dest + ai] = chr((((color & amask) >> ashift) << aloss)
                                          if amask else 255)
    else:
        raise ValueError("invalid color depth")
    return ffi.buffer(data)[:]


def _tostring_RGBX(surf, flipped):
    return _tostring_RGBA(surf, flipped, False)


def _tostring_ARGB(surf, flipped):
    return _tostring_RGBA(surf, flipped, True, True)


def _tostring_RGBA_PREMULT(surf, flipped, argb=False):
    if surf.format.BytesPerPixel == 1 or surf.format.Amask == 0:
        raise ValueError("Can only create pre-multiplied alpha strings if "
                         "the surface has per-pixel alpha")

    rmask, gmask, bmask, amask = (surf.format.Rmask,
                                  surf.format.Gmask,
                                  surf.format.Bmask,
                                  surf.format.Amask)
    rshift, gshift, bshift, ashift = (surf.format.Rshift,
                                      surf.format.Gshift,
                                      surf.format.Bshift,
                                      surf.format.Ashift)
    rloss, gloss, bloss, aloss = (surf.format.Rloss,
                                  surf.format.Gloss,
                                  surf.format.Bloss,
                                  surf.format.Aloss)
    bpp = surf.format.BytesPerPixel
    h, w = surf.h, surf.w
    if argb:
        ri, gi, bi, ai = 1, 2, 3, 0
    else:
        ri, gi, bi, ai = 0, 1, 2, 3

    data = ffi.new('char[]', w * h * 4)
    if bpp == 2:
        pixels = ffi.cast('uint16_t*', surf.pixels)
        for y in range(h):
            src_start = (h - 1 - y) * w if flipped \
                        else y * w
            for x in range(w):
                dest = 4 * (y * w + x)
                color = pixels[src_start + x]
                alpha = ((color & amask) >> ashift) << aloss;
                data[dest + ri] = chr((((color & rmask) >> rshift) << rloss)
                                      * alpha / 255)
                data[dest + gi] = chr((((color & gmask) >> gshift) << gloss)
                                      * alpha / 255)
                data[dest + bi] = chr((((color & bmask) >> bshift) << bloss)
                                      * alpha / 255)
                data[dest + ai] = chr(alpha)
    elif bpp == 3:
        pixels = ffi.cast('uint8_t*', surf.pixels)
        for y in range(h):
            src_start = (h - 1 - y) * surf.pitch if flipped \
                        else y * surf.pitch
            for x in range(w):
                dest = 4 * (y * w + x)
                color = (pixels[src_start + x * 3 + BYTE0] +
                         (pixels[src_start + x * 3 + BYTE1] << 8) +
                         (pixels[src_start + x * 3 + BYTE2] << 16))
                alpha = ((color & amask) >> ashift) << aloss;
                data[dest + ri] = chr((((color & rmask) >> rshift) << rloss)
                                      * alpha / 255)
                data[dest + gi] = chr((((color & gmask) >> gshift) << gloss)
                                      * alpha / 255)
                data[dest + bi] = chr((((color & bmask) >> bshift) << bloss)
                                      * alpha / 255)
                data[dest + ai] = chr(alpha)
    elif bpp == 4:
        pixels = ffi.cast('uint32_t*', surf.pixels)
        for y in range(h):
            src_start = (h - 1 - y) * w if flipped \
                        else y * w
            for x in range(w):
                dest = 4 * (y * w + x)
                color = pixels[src_start + x]
                alpha = ((color & amask) >> ashift) << aloss;
                if alpha == 0:
                    data[dest + ri] = data[dest + gi] = data[dest + bi] = chr(0)
                else:
                    data[dest + ri] = chr((((color & rmask) >> rshift) << rloss)
                                          * alpha / 255)
                    data[dest + gi] = chr((((color & gmask) >> gshift) << gloss)
                                          * alpha / 255)
                    data[dest + bi] = chr((((color & bmask) >> bshift) << bloss)
                                          * alpha / 255)
                data[dest + ai] = chr(alpha)
    else:
        raise ValueError("invalid color depth")
    return ffi.buffer(data)[:]


def _tostring_ARGB_PREMULT(surf, flipped):
    return _tostring_RGBA_PREMULT(surf, flipped, True)


def _tostring_RGB(surf, flipped):
    rmask, gmask, bmask, amask = (surf.format.Rmask,
                                  surf.format.Gmask,
                                  surf.format.Bmask,
                                  surf.format.Amask)
    rshift, gshift, bshift, ashift = (surf.format.Rshift,
                                      surf.format.Gshift,
                                      surf.format.Bshift,
                                      surf.format.Ashift)
    rloss, gloss, bloss, aloss = (surf.format.Rloss,
                                  surf.format.Gloss,
                                  surf.format.Bloss,
                                  surf.format.Aloss)
    bpp = surf.format.BytesPerPixel
    h, w = surf.h, surf.w

    data = ffi.new('char[]', w * h * 3)
    if bpp == 1:
        pixels = ffi.cast('uint8_t*', surf.pixels)
        colors = surf.format.palette.colors
        for y in range(h):
            src_start = (h - 1 - y) * w if flipped \
                        else y * w
            for x in range(w):
                dest = 3 * (y * w + x)
                color = pixels[src_start + x]
                data[dest] = chr(colors[color].r)
                data[dest + 1] = chr(colors[color].g)
                data[dest + 2] = chr(colors[color].b)
    elif bpp == 2:
        pixels = ffi.cast('uint16_t*', surf.pixels)
        for y in range(h):
            src_start = (h - 1 - y) * w if flipped \
                        else y * w
            for x in range(w):
                dest = 3 * (y * w + x)
                color = pixels[src_start + x]
                data[dest] = chr(((color & rmask) >> rshift) << rloss)
                data[dest + 1] = chr(((color & gmask) >> gshift) << gloss)
                data[dest + 2] = chr(((color & bmask) >> bshift) << bloss)
    elif bpp == 3:
        pixels = ffi.cast('uint8_t*', surf.pixels)
        for y in range(h):
            src_start = (h - 1 - y) * surf.pitch if flipped \
                        else y * surf.pitch
            for x in range(w):
                dest = 3 * (y * w + x)
                color = (pixels[src_start + x * 3 + BYTE0] +
                         (pixels[src_start + x * 3 + BYTE1] << 8) +
                         (pixels[src_start + x * 3 + BYTE2] << 16))
                data[dest] = chr(((color & rmask) >> rshift) << rloss)
                data[dest + 1] = chr(((color & gmask) >> gshift) << gloss)
                data[dest + 2] = chr(((color & bmask) >> bshift) << bloss)
    elif bpp == 4:
        pixels = ffi.cast('uint32_t*', surf.pixels)
        for y in range(h):
            src_start = (h - 1 - y) * w if flipped \
                        else y * w
            for x in range(w):
                dest = 3 * (y * w + x)
                color = pixels[src_start + x]
                data[dest] = chr(((color & rmask) >> rshift) << rloss)
                data[dest + 1] = chr(((color & gmask) >> gshift) << gloss)
                data[dest + 2] = chr(((color & bmask) >> bshift) << bloss)
    else:
        raise ValueError("invalid color depth")
    return ffi.buffer(data)[:]


def frombuffer(string, size, format):
    """ frombuffer(string, size, format) -> Surface
    create a new Surface that shares data inside a string buffer
    """
    raise NotImplementedError()
