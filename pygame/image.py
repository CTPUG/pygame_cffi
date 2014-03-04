""" The pygame image module """

import struct

from pygame._error import SDLError
from pygame._sdl import sdl, ffi, get_sdl_byteorder
from pygame.imageext import load_extended, save_extended
from pygame.rect import new_rect
from pygame.rwobject import (rwops_encode_file_path, rwops_from_file,
                             rwops_from_file_path)
from pygame.surface import Surface, locked, BYTE0, BYTE1, BYTE2


def get_extended():
    # Only correct if we always require SDL_image
    return True


def load_basic(filename, namehint=""):
    # Will we need this, if we're always requiring SDL_image?
    try:
        filename = rwops_encode_file_path(filename)
        c_surface = sdl.SDL_LoadBMP(filename)
    except TypeError:
        # filename is not a string, try as file object
        try:
            rwops = rwops_from_file(filename)
            c_surface = sdl.SDL_LoadBMP_RW(rwops, 1)
        except TypeError:
            raise TypeError("file argument must be a valid path "
                            "string or file object")
    if not c_surface:
        raise SDLError.from_sdl_error()
    return Surface._from_sdl_surface(c_surface)


if get_extended():
    load = load_extended
else:
    load = load_basic


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
        # save as JPEG
        result = sdl.SDL_SaveBMP(surf, filename)
    elif (fn_normalized.endswith('png') or
          fn_normalized.endswith('jpg') or
          fn_normalized.endswith('jpeg')):
        if get_extended():
            save_extended(surface, filename)
        else:
            result = save_tga(surf, filename)
    else:
        result = save_tga(surf, filename)
    if result == -1:
        raise SDLError.from_sdl_error()


# Entire TGA implementation here since SDL doesn't write TGAs

TGA_TYPE_INDEXED = 1
TGA_TYPE_RGB = 2
TGA_TYPE_BW = 3
TGA_TYPE_RLE = 8

TGA_INTERLEAVE_MASK = 0xc0
TGA_INTERLEAVE_NONE = 0x00
TGA_INTERLEAVE_2WAY = 0x40
TGA_INTERLEAVE_4WAY = 0x80

TGA_ORIGIN_MASK = 0x30
TGA_ORIGIN_LEFT = 0x00
TGA_ORIGIN_RIGHT = 0x10
TGA_ORIGIN_LOWER = 0x00
TGA_ORIGIN_UPPER = 0x20

TGA_RLE_MAX = 128

# read/write unaligned little-endian 16-bit ints
def le16(p):
    return p[0] + (p[1] << 8)


def makele16(v):
    return (v & 255, ((v >> 8) & 255))


class TGAHeader(object):
    def __init__(self):
        self.infolen = 0
        self.has_cmap = 0
        self.type = 0
        self._cmap_start = (0, 0)
        self._cmap_len = (0, 0)
        self.cmap_bits = 0
        self._yorigin = (0, 0)
        self._xorigin = (0, 0)
        self._width = (0, 0)
        self._height = (0, 0)
        self.pixel_bits = 0
        self.flags = 0
        self._order = ('infolen', 'has_cmap', 'type', '_cmap_start', '_cmap_len',
                       'cmap_bits', '_yorigin', '_xorigin', '_width', '_height',
                       'pixel_bits', 'flags')
        # all header fields are 8 bits
        self._packed_format = 'B' * 18

    def get_cmap_start(self):
        return le16(self._cmap_start)
    def set_cmap_start(self, value):
        self._cmap_start = makele16(value)
    cmap_start = property(get_cmap_start, set_cmap_start)

    def get_cmap_len(self):
        return le16(self._cmap_len)
    def set_cmap_len(self, value):
        self._cmap_len = makele16(value)
    cmap_len = property(get_cmap_start, set_cmap_start)

    def get_yorigin(self):
        return le16(self._yorigin)
    def set_yorigin(self, value):
        self._yorigin = makele16(value)
    yorigin = property(get_yorigin, set_yorigin)

    def get_xorigin(self):
        return le16(self._xorigin)
    def set_xorigin(self, value):
        self._xorigin = makele16(value)
    xorigin = property(get_xorigin, set_xorigin)

    def get_width(self):
        return le16(self._width)
    def set_width(self, value):
        self._width = makele16(value)
    width = property(get_width, set_width)

    def get_height(self):
        return le16(self._height)
    def set_height(self, value):
        self._height = makele16(value)
    height = property(get_height, set_height)

    @property
    def size(self):
        return struct.calcsize(self._packed_format)

    def __str__(self):
        pack_args = []
        for attr in self._order:
            val = getattr(self, attr)
            if hasattr(val, '__iter__'):
                pack_args.extend(val)
            else:
                pack_args.append(val)
        return struct.pack(self._packed_format, *pack_args)


def save_tga(surf, filename, rle=False):
    if rle:
        raise NotImplementedError("rle compression not implemented yet")
    rwops = rwops_from_file_path(filename, 'wb')
    srcbpp = surf.format.BitsPerPixel
    header = TGAHeader()
    colorkey = None
    alpha = False

    def close_and_err(rwops):
        sdl.SDL_RWclose(rwops)
        return -1

    # write TGA header
    if srcbpp < 8:
        sdl.SDL_SetError("cannot save <8bpp images as TGA")
        return close_and_err(rwops)
    elif srcbpp == 8:
        header.has_cmap = 1
        header.type = TGA_TYPE_INDEXED
        if surf.flags & sdl.SDL_SRCCOLORKEY:
            colorkey = surf.format.colorkey
            header.cmap_bits = 32
        else:
            header.cmap_bits = 24
        header.cmap_len = surf.format.palette.ncolors
        header.pixel_bits = 8
        rmask = gmask = bmask = amask = 0
    else:
        header.type = TGA_TYPE_RGB
        header.cmap_bits = 0
        if surf.format.Amask:
            alpha = True
            header.pixel_bits = 32
        else:
            header.pixel_bits = 24
        if get_sdl_byteorder() == sdl.SDL_LIL_ENDIAN:
            amask = 0xff000000 if alpha else 0
            rmask = 0x00ff0000
            gmask = 0x0000ff00
            bmask = 0x000000ff
        else:
            s = 0 if alpha else 8
            amask = 0x000000ff >> s
            rmask = 0x0000ff00 >> s
            gmask = 0x00ff0000 >> s
            bmask = 0xff000000 >> s
    header.width = surf.w
    header.height = surf.h
    header.flags = TGA_ORIGIN_UPPER | (8 if alpha else 0)
    if not sdl.SDL_RWwrite(rwops, ffi.new('char[]', str(header)),
                           header.size, 1):
        return close_and_err(rwops)

    # write color map
    if header.has_cmap:
        palette = surf.format.palette
        color = ffi.new('uint8_t[]', 4)
        for i in range(palette.ncolors):
            color[0] = palette.colors[i].b
            color[1] = palette.colors[i].g
            color[2] = palette.colors[i].r
            color[3] = 0 if i == colorkey else 0xff
            if not sdl.SDL_RWwrite(rwops, color, header.cmap_bits >> 3, 1):
                return close_and_err(rwops)

    # write content
    destbpp = header.pixel_bits >> 3
    linebuffer = sdl.SDL_CreateRGBSurface(sdl.SDL_SWSURFACE, surf.w, 1,
                                          header.pixel_bits, rmask,
                                          gmask, bmask, amask)
    if not linebuffer:
        return close_and_err()
    if header.has_cmap:
        sdl.SDL_SetColors(linebuffer, surf.format.palette.colors, 0,
                          surf.format.palette.ncolors)
    # stash flags
    surf_flags = surf.flags & (sdl.SDL_SRCALPHA | sdl.SDL_SRCCOLORKEY)
    surf_alpha = surf.format.alpha
    if surf_flags & sdl.SDL_SRCALPHA:
        sdl.SDL_SetAlpha(surf, 0, 255)
    if surf_flags & sdl.SDL_SRCCOLORKEY:
        sdl.SDL_SetColorKey(surf, 0, surf.format.colorkey)
    rect = new_rect(0, 0, surf.w, 1)
    for y in range(surf.h):
        rect.y = y
        if sdl.SDL_BlitSurface(surf, rect, linebuffer, ffi.NULL) < 0:
            sdl.SDL_FreeSurface(linebuffer)
            return close_and_err(rwops)
        if not sdl.SDL_RWwrite(rwops, linebuffer.pixels, surf.w * destbpp, 1):
            sdl.SDL_FreeSurface(linebuffer)
            return close_and_err(rwops)
    # restore flags
    if surf_flags & sdl.SDL_SRCALPHA:
        sdl.SDL_SetAlpha(surf, sdl.SDL_SRCALPHA, surf_alpha)
    if surf_flags & sdl.SDL_SRCCOLORKEY:
        sdl.SDL_SetColorKey(surf, sdl.SDL_SRCCOLORKEY, surf.format.colorkey)

    sdl.SDL_FreeSurface(linebuffer)
    sdl.SDL_RWclose(rwops)
    return 0


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
