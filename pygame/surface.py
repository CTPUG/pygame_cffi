""" XXX """

from pygame._error import SDLError, unpack_rect
from pygame._sdl import sdl, locked, ffi, FillRect, BlitSurface
from pygame.rect import Rect, new_rect, rect_from_obj
from pygame.color import create_color, uncreate_color


if sdl.SDL_BYTEORDER == sdl.SDL_LIL_ENDIAN:
    BYTE0 = 0
    BYTE1 = 1
    BYTE2 = 2
else:  # BIG_ENDIAN
    BYTE0 = 2
    BYTE1 = 1
    BYTE2 = 0


class SubSurfaceData(object):
    def __init__(self, owner, pixeloffset, xoffset, yoffset):
        self.owner = owner
        self.pixeloffset = pixeloffset
        self.xoffset = xoffset
        self.yoffset = yoffset


class Surface(object):
    """ Surface((width, height), flags=0, depth=0, masks=None) -> Surface
    Surface((width, height), flags=0, Surface) -> Surface

    pygame object for representing images
    """
    _c_surface = None
    subsurfacedata = None

    def __init__(self, size, flags=0, depth=0, masks=None):
        w, h = unpack_rect(size)
        if isinstance(depth, Surface):
            surface = depth
            depth = 0
        else:
            surface = None

        if depth or masks:
            raise SDLError("XXX: Not implemented!")

        if surface is None:
            if sdl.SDL_GetVideoSurface():
                pix = sdl.SDL_GetVideoSurface().format
            elif sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO):
                pix = sdl.SDL_GetVideoInfo().vfmt
            else:
                pix = ffi.new("SDL_PixelFormat*")
                pix.BitsPerPixel = 32
                pix.Rmask, pix.Gmask, pix.Bmask, pix.Amask = \
                    self._get_default_masks(32, False)
            # the alpha mask might be different - must update
            if flags & sdl.SDL_SRCALPHA:
                pix.Rmask, pix.Gmask, pix.Bmask, pix.Amask = \
                    self._get_default_masks(pix.BitsPerPixel, True)
            self._c_surface = sdl.SDL_CreateRGBSurface(flags, w, h,
                                                       pix.BitsPerPixel,
                                                       pix.Rmask,
                                                       pix.Gmask,
                                                       pix.Bmask,
                                                       pix.Amask)

        else:
            pix = surface._c_surface.format
            if flags & sdl.SDL_SRCALPHA:
                Rmask, Gmask, Bmask, Amask = \
                    self._get_default_masks(pix.BitsPerPixel, True)
            else:
                Amask = pix.Amask
                Rmask = pix.Rmask
                Gmask = pix.Gmask
                Bmask = pix.Bmask
            self._c_surface = sdl.SDL_CreateRGBSurface(flags, w, h,
                                                       pix.BitsPerPixel,
                                                       Rmask, Gmask,
                                                       Bmask, Amask)

        if not self._c_surface:
                raise SDLError.from_sdl_error()

    def __del__(self):
        if (sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO) or
                self._c_surface.flags & sdl.SDL_HWSURFACE):
            sdl.SDL_FreeSurface(self._c_surface)

    def _get_default_masks(self, bpp, alpha):
        if alpha:
            if bpp == 16:
                Amask = 0xF000
                Rmask = 0x0F00
                Gmask = 0x00F0
                Bmask = 0x000F
            elif bpp == 32:
                Amask = 0xFF000000
                Rmask = 0x00FF0000
                Gmask = 0x0000FF00
                Bmask = 0x000000FF
            else:
                raise ValueError("no standard masks exist for given bitdepth with alpha")
        else:
            if bpp == 8:
                Rmask = 0xFF >> 6 << 5
                Gmask = 0xFF >> 5 << 2
                Bmask = 0xFF >> 6
            elif bpp == 12:
                Rmask = 0xFF >> 4 << 8
                Gmask = 0xFF >> 4 << 4
                Bmask = 0xFF >> 4
            elif bpp == 15:
                Rmask = 0xFF >> 3 << 10
                Gmask = 0xFF >> 3 << 5
                Bmask = 0xFF >> 3
            elif bpp == 16:
                Rmask = 0xFF >> 3 << 11
                Gmask = 0xFF >> 2 << 5
                Bmask = 0xFF >> 3
            elif bpp == 24 or bpp == 32:
                Rmask = 0xFF << 16
                Gmask = 0xFF << 8
                Bmask = 0xFF
            else:
                raise ValueError("nonstandard bit depth given")
        return Rmask, Gmask, Bmask, Amask

    def fill(self, color, rect=None, special_flags=0):
        assert special_flags == 0
        c_color = create_color(color, self._format)
        if rect is not None:
            sdlrect = rect_from_obj(rect)
        else:
            sdlrect = new_rect(0, 0, self._w, self._h)
        with locked(self._c_surface):
            FillRect(self._c_surface, sdlrect, c_color)

    def blit(self, source, destrect, area=None, special_flags=0):
        if area is not None:
            srcrect = rect_from_obj(area)
        else:
            srcrect = new_rect(0, 0, source._w, source._h)
        if isinstance(destrect, tuple):
            destrect = new_rect(destrect[0], destrect[1], source._w, source._h)
        elif isinstance(destrect, Rect):
            destrect = destrect._sdlrect
        BlitSurface(source, srcrect, self, destrect, special_flags)
        return Rect(destrect.x, destrect.y, destrect.w, destrect.h)

    def convert_alpha(self, srcsurf=None):
        with locked(self._c_surface):
            newsurf = sdl.SDL_DisplayFormatAlpha(self._c_surface)
        return Surface._from_sdl_surface(newsurf)

    def get_format(self):
        return self._c_surface.format
    _format = property(get_format)

    def get_w(self):
        return self._c_surface.w
    _w = property(get_w)

    def get_h(self):
        return self._c_surface.h
    _h = property(get_h)

    def get_size(self):
        return self._w, self._h

    def get_width(self):
        return self._w

    def get_height(self):
        return self._h

    @classmethod
    def _from_sdl_surface(cls, c_surface):
        surface = cls.__new__(cls)
        surface._c_surface = c_surface
        return surface

    def check_opengl(self):
        if not self._c_surface:
            raise SDLError("display Surface quit")
        if self._c_surface.flags & sdl.SDL_OPENGL:
            raise SDLError("Cannot call on OPENGL Surfaces")

    def get_rect(self, **kwargs):
        r = Rect(0, 0, self._w, self._h)
        if kwargs:
            for attr, value in kwargs.iteritems():
                # Logic copied form pygame/surface.c - blame them
                setattr(r, attr, value)
        return r

    def set_at(self, pos, color):
        self.check_opengl()
        x, y = pos
        c_color = create_color(color, self._format)
        with locked(self._c_surface):
            self._set_at(x, y, c_color)

    def _set_at(self, x, y, c_color):
        bpp = self._format.BytesPerPixel
        if bpp == 1:
            pixels = ffi.cast("uint8_t*", self._c_surface.pixels)
            pixels[y * self._c_surface.pitch // bpp + x] = c_color
        elif bpp == 2:
            pixels = ffi.cast("uint16_t*", self._c_surface.pixels)
            pixels[y * self._c_surface.pitch // bpp + x] = c_color
        elif bpp == 3:
            pixels = ffi.cast("uint8_t*", self._c_surface.pixels)
            raise RuntimeError("Not implemented")
        elif bpp == 4:
            pixels = ffi.cast("uint32_t*", self._c_surface.pixels)
            pixels[y * (self._c_surface.pitch // bpp) + x] = c_color
        else:
            raise RuntimeError("invalid color depth for surface")

    def get_at(self, pos):
        self.check_opengl()
        x, y = pos
        with locked(self._c_surface):
            c_color = self._get_at(x, y)
        return uncreate_color(c_color, self._format)

    def _get_at(self, x, y):
        bpp = self._format.BytesPerPixel
        if bpp == 1:
            pixels = ffi.cast("uint8_t*", self._c_surface.pixels)
            return pixels[y * self._c_surface.pitch // bpp + x]
        elif bpp == 2:
            pixels = ffi.cast("uint16_t*", self._c_surface.pixels)
            return pixels[y * self._c_surface.pitch // bpp + x]
        elif bpp == 3:
            pixels = ffi.cast("uint8_t*", self._c_surface.pixels)
            pixel = pixels[y * self._c_surface.pitch // bpp + x]
            return pixel[BYTE0] | pixel[BYTE1] << 8 | pixel[BYTE2] << 16
        elif bpp == 4:
            pixels = ffi.cast("uint32_t*", self._c_surface.pixels)
            return pixels[y * self._c_surface.pitch // bpp + x]
        else:
            raise RuntimeError("invalid color depth for surface")

    def subsurface(self, rect):
        self.check_opengl()

        rect = rect_from_obj(rect)
        if (rect.x < 0 or rect.x + rect.w > self._c_surface.w or rect.y < 0 or
            rect.y + rect.h > self._c_surface.h):
            raise ValueError("subsurface rectangle outside surface area")
        with locked(self._c_surface):
            format = self._format
            pixeloffset = (rect.x * format.BytesPerPixel +
                           rect.y * self._c_surface.pitch)
            startpixel = ffi.cast("char*", self._c_surface.pixels) + pixeloffset
            surf = self._c_surface
            sub = sdl.SDL_CreateRGBSurfaceFrom(startpixel, rect.w, rect.h,
                                               format.BitsPerPixel, surf.pitch,
                                               format.Rmask, format.Gmask,
                                               format.Bmask, format.Amask)
        if not sub:
            raise SDLError.from_sdl_error()

        if format.BytesPerPixel == 1:
            xxx
            #SDL_SetPalette (sub, SDL_LOGPAL, surf->format->palette->colors, 0,
            #            surf->format->palette->ncolors);
        if surf.flags & sdl.SDL_SRCALPHA:
            XXX
            #SDL_SetAlpha (sub, surf->flags & SDL_SRCALPHA, format->alpha);
        if surf.flags & sdl.SDL_SRCCOLORKEY:
            sdl.SDL_SetColorKey(sub, surf.flags & (sdl.SDL_SRCCOLORKEY |
                                                   sdl.SDL_RLEACCEL),
                                                   format.colorkey)
        subsurface = Surface._from_sdl_surface(sub)
        data = SubSurfaceData(self, pixeloffset, rect.x, rect.y)
        subsurface.subsurfdata = data
        return subsurface

    def set_colorkey(self, color=None, flags=0):
        c_color = 0
        if color is not None:
            c_color = create_color(color, self._format)
            flags |= sdl.SDL_SRCCOLORKEY

        with locked(self._c_surface):
            if sdl.SDL_SetColorKey(self._c_surface, flags, c_color) == -1:
                raise SDLError.from_sdl_error()

    def copy(self):
        with locked(self._c_surface):
            newsurf = sdl.SDL_ConvertSurface(self._c_surface,
                                             self._format,
                                             self._c_surface.flags)
        return Surface._from_sdl_surface(newsurf)


    def convert(self, arg=None, flags=0):
        with locked(self._c_surface):
            if isinstance(arg, Surface):
                flags = arg._c_surface.flags | (self._c_surface.flags &
                                     (sdl.SDL_SRCCOLORKEY |
                                      sdl.SDL_SRCALPHA))
                newsurf = sdl.SDL_ConvertSurface(self._c_surface,
                                                 arg._format, flags)
            elif arg is None:
                if sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO):
                    newsurf = sdl.SDL_DisplayFormat(self._c_surface)
                else:
                    newsurf = sdl.SDL_ConvertSurface(self._c_surface,
                                                     self._format,
                                                     self._c_surface.flags)
            else:
                xxx
        return Surface._from_sdl_surface(newsurf)

    def get_colorkey(self):
        self.check_opengl()

        if not self._c_surface.flags & sdl.SDL_SRCCOLORKEY:
            return None
        r = ffi.new("uint8_t[1]")
        g = ffi.new("uint8_t[1]")
        b = ffi.new("uint8_t[1]")
        a = ffi.new("uint8_t[1]")
        sdl.SDL_GetRGBA(self._format.colorkey, self._format, r, g, b, a)
        return (r[0], g[0], b[0], a[0])

    def set_alpha(self, value=None, flags=0):
        """ set_alpha(value, flags=0) -> None
        set the alpha value for the full Surface image
        """
        if value is not None:
            value = int(value)
            if value > 255:
                value = 255
            if value < 0:
                value = 0
            flags |= sdl.SDL_SRCALPHA
        else:
            value = 255

        with locked(self._c_surface):
            if sdl.SDL_SetAlpha(self._c_surface, flags, value) == -1:
                raise SDLError.from_sdl_error()

    def get_alpha(self):
        """ get_alpha() -> int_value or None
        get the current Surface transparency value
        """
        self.check_opengl()

        if self._c_surface.flags & sdl.SDL_SRCALPHA:
            return int(self._c_surface.format.alpha)
        return None

    def get_clip(self):
        """ get_clip() -> Rect
        get the current clipping area of the Surface
        """
        # TODO: Clipping.
        return self.get_rect()

    def get_bounding_rect(self, min_alpha=1):
        """ get_bounding_rect(min_alpha = 1) -> Rect
        find the smallest rect containing data
        """
        if not self._c_surface:
            raise SDLError("display Surface quit")

        min_alpha = int(min_alpha)
        if min_alpha > 255:
            min_alpha = 255
        elif min_alpha < 0:
            min_alpha = 0

        r, g, b, a = (ffi.new('uint8_t *'), ffi.new('uint8_t *'),
                      ffi.new('uint8_t *'), ffi.new('uint8_t *'))
        format = self._c_surface.format

        if self._c_surface.flags & sdl.SDL_SRCCOLORKEY:
            keyr = ffi.new('uint8_t *')
            keyg = ffi.new('uint8_t *')
            keyb = ffi.new('uint8_t *')
            sdl.SDL_GetRGBA(self._c_surface.colorkey,
                            format, keyr, keyg, keyb, a)
            keyr, keyg, keyb = keyr[0], keyg[0], keyb[0]
        else:
            keyr = keyg = keyb = None

        min_x, min_y, max_x, max_y = 0, 0, self._w, self._h

        def check_alpha(x, y):
            value = self._get_at(x, y)
            sdl.SDL_GetRGBA(value, format, r, g, b, a)
            if (keyr is None and a[0] >= min_alpha) or \
               (keyr is not None and (r[0] != keyr or
                                      g[0] != keyg or
                                      b[0] != keyb)):
               return True
            return False

        with locked(self._c_surface):
            found_alpha = False
            for y in range(max_y - 1, -1, -1):
                for x in range(min_x, max_x):
                    found_alpha = check_alpha(x, y)
                    if found_alpha:
                        break
                if found_alpha:
                    break
                max_y = y

            found_alpha = False
            for x in range(max_x - 1, -1, -1):
                for y in range(min_y, max_y):
                    found_alpha = check_alpha(x, y)
                    if found_alpha:
                        break
                if found_alpha:
                    break
                max_x = x

            found_alpha = False
            for y in range(min_y, max_y):
                min_y = y
                for x in range(min_x, max_x):
                    found_alpha = check_alpha(x, y)
                    if found_alpha:
                        break
                if found_alpha:
                    break

            found_alpha = False
            for x in range(min_x, max_x):
                min_x = x
                for y in range(min_y, max_y):
                    found_alpha = check_alpha(x, y)
                    if found_alpha:
                        break
                if found_alpha:
                    break

        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def get_flags(self):
        """ get_flags() -> int
        get the additional flags used for the Surface
        """
        if not self._c_surface:
            raise SDLError("display Surface quit")
        return self._c_surface.flags
