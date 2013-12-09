""" XXX """

from pygame._error import SDLError, unpack_rect
from pygame._sdl import sdl, locked, ffi, FillRect, BlitSurface
from pygame.rect import Rect, new_rect, rect_from_obj
from pygame.color import create_color

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
                pix.Amask = 0
                pix.Rmask = 0xff0000
                pix.Gmask = 0xFF00
                pix.Bmask = 0xFF
            self._c_surface = sdl.SDL_CreateRGBSurface(flags, w, h,
                                                       pix.BitsPerPixel,
                                                       pix.Rmask,
                                                       pix.Gmask,
                                                       pix.Bmask,
                                                       pix.Amask)
            if not self._c_surface:
                raise SDLError.from_sdl_error()

        else:
            raise NotImplementedError("xxx")

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

    def get_rect(self, **kwargs):
        r = Rect(0, 0, self._w, self._h)
        if kwargs:
            for attr, value in kwargs.iteritems():
                # Logic copied form pygame/surface.c - blame them
                setattr(r, attr, value)
        return r

    def set_at(self, pos, color):
        x, y = pos
        c_color = create_color(color, self._format)
        with locked(self._c_surface):
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
                pixels[y * self._c_surface.pitch // bpp + x] = c_color
            else:
                raise RuntimeError("Unknown pixel format")

    def subsurface(self, rect):
        if not self._c_surface:
            raise SDLError("display Surface quit")
        if self._c_surface.flags & sdl.SDL_OPENGL:
            raise SDLError("Cannot call on OPENGL Surfaces")
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
        if not self._c_surface:
            raise SDLError("display Surface quit")
        if self._c_surface.flags & sdl.SDL_OPENGL:
            raise SDLError("Cannot call on OPENGL Surfaces")
        if not self._c_surface.flags & sdl.SDL_SRCCOLORKEY:
            return None
        r = ffi.new("uint8_t[1]")
        g = ffi.new("uint8_t[1]")
        b = ffi.new("uint8_t[1]")
        a = ffi.new("uint8_t[1]")
        sdl.SDL_GetRGBA(self._format.colorkey, self._format, r, g, b, a)
        return (r[0], g[0], b[0], a[0])

    def set_alpha(self, value=None, flags=0):
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

    def get_at(self, pos):
        x, y = pos
        with locked(self._c_surface):
            bpp = self._format.BytesPerPixel
            if bpp == 1:
                pixels = ffi.cast("uint8_t*", self._c_surface.pixels)
                c_color = pixels[y * self._c_surface.pitch // bpp + x]
            elif bpp == 2:
                pixels = ffi.cast("uint16_t*", self._c_surface.pixels)
                c_color = pixels[y * self._c_surface.pitch // bpp + x]
            elif bpp == 3:
                pixels = ffi.cast("uint8_t*", self._c_surface.pixels)
                raise RuntimeError("Not implemented")
            elif bpp == 4:
                pixels = ffi.cast("uint32_t*", self._c_surface.pixels)
                c_color = pixels[y * self._c_surface.pitch // bpp + x]
            else:
                raise RuntimeError("Unknown pixel format")
        return c_color
