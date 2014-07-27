""" XXX """

from pygame._error import SDLError, unpack_rect
from pygame._sdl import sdl, ffi, get_sdl_byteorder
from pygame.color import create_color, Color
from pygame.rect import Rect, game_rect_from_obj
from pygame.surflock import locked


if get_sdl_byteorder() == sdl.SDL_LIL_ENDIAN:
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


def rect_vals_from_obj(obj):
    if isinstance(obj, Rect):
        return obj.r.x, obj.r.y, obj.r.w, obj.r.h
    try:
        if len(obj) == 1:
            r = obj[0].r
            return r.x, r.y, r.w, r.h
        elif len(obj) == 4:
            # truncate and normalize
            return int(obj[0]), int(obj[1]), int(obj[2]), int(obj[3])
        elif len(obj) == 2:
            # truncate and normalize
            return int(obj[0][0]), int(obj[0][1]), int(obj[1][0]), int(obj[1][1])
        raise TypeError("Argument must be rect style object")
    except (ValueError, AttributeError):
        raise TypeError("Argument must be rect style object")


def check_surface_overlap(c_src, srcrect, c_dest, destrect):
    srcx, srcy, destx, desty, w, h = (srcrect.x, srcrect.y,
                                      destrect.x, destrect.y,
                                      srcrect.w, srcrect.h)
    if srcx < 0:
        w += srcx
        destx -= srcx
        srcx = 0
    maxw = c_src.w - srcx
    if maxw < w:
        w = maxw
    if srcy < 0:
        h += srcy
        desty -= srcy
        srcy = 0
    maxh = c_src.h - srcy
    if maxh < h:
        h = maxh

    clip = c_dest.clip_rect
    x = clip.x - destx
    if x > 0:
        w -= x
        destx += x
        srcx += x
    x = destx + w - clip.x - clip.w
    if x > 0:
        w -= x
    y = clip.y - desty
    if y > 0:
        h -= y
        desty += y
        srcy += y
    y = desty + h - clip.y - clip.h
    if y > 0:
        h -= y

    if w <= 0 or h <= 0:
        return None

    srcpixels = ffi.cast("uint8_t*", c_src.pixels)
    srcpixels += c_src.offset + srcy * c_src.pitch + \
                 srcx * c_src.format.BytesPerPixel
    destpixels = ffi.cast("uint8_t*", c_dest.pixels)
    destpixels += c_src.offset + desty * c_dest.pitch + \
                  destx * c_dest.format.BytesPerPixel

    if destpixels <= srcpixels:
        return False
    span = w * c_src.format.BytesPerPixel
    if destpixels >= (srcpixels + (h - 1) * c_src.pitch + span):
        return False
    destoffset = (destpixels - srcpixels) % c_src.pitch
    return (destoffset < span) or (destoffset > c_src.pitch - span)


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
            if masks:
                raise ValueError("cannot pass surface for depth and color masks")
            surface = depth
            depth = 0
        else:
            surface = None
            depth = int(depth)

        if depth and masks:
            Rmask, Gmask, Bmask, Amask = masks
            bpp = depth

        elif surface is None:
            if depth:
                bpp = depth
                Rmask, Gmask, Bmask, Amask = \
                    self._get_default_masks(bpp, False)
            elif sdl.SDL_GetVideoSurface():
                pix = sdl.SDL_GetVideoSurface().format
                bpp = pix.BitsPerPixel
                Amask = pix.Amask
                Rmask = pix.Rmask
                Gmask = pix.Gmask
                Bmask = pix.Bmask
            elif sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO):
                pix = sdl.SDL_GetVideoInfo().vfmt
                bpp = pix.BitsPerPixel
                Amask = pix.Amask
                Rmask = pix.Rmask
                Gmask = pix.Gmask
                Bmask = pix.Bmask
            else:
                bpp = 32
                Rmask, Gmask, Bmask, Amask = \
                    self._get_default_masks(32, False)
            # the alpha mask might be different - must update
            if flags & sdl.SDL_SRCALPHA:
                Rmask, Gmask, Bmask, Amask = \
                    self._get_default_masks(bpp, True)

        # depth argument was a Surface object
        else:
            pix = surface._c_surface.format
            bpp = pix.BitsPerPixel
            if flags & sdl.SDL_SRCALPHA:
                Rmask, Gmask, Bmask, Amask = \
                    self._get_default_masks(bpp, True)
            else:
                Amask = pix.Amask
                Rmask = pix.Rmask
                Gmask = pix.Gmask
                Bmask = pix.Bmask

        self._c_surface = sdl.SDL_CreateRGBSurface(flags, w, h, bpp,
                                                   Rmask, Gmask,
                                                   Bmask, Amask)
        self._format = self._c_surface.format
        self._w = self._c_surface.w
        self._h = self._c_surface.h

        if not self._c_surface:
            raise SDLError.from_sdl_error()

        if masks:
            """
            Confirm the surface was created correctly (masks were valid).
            Also ensure that 24 and 32 bit surfaces have 8 bit fields
            (no losses).
            """
            format = self._format
            Rmask = (0xFF >> format.Rloss) << format.Rshift
            Gmask = (0xFF >> format.Gloss) << format.Gshift
            Bmask = (0xFF >> format.Bloss) << format.Bshift
            Amask = (0xFF >> format.Aloss) << format.Ashift
            bad_loss = format.Rloss or format.Gloss or format.Bloss
            if flags & sdl.SDL_SRCALPHA:
                bad_loss = bad_loss or format.Aloss
            else:
                bad_loss = bad_loss or format.Aloss != 8
            if (format.Rmask != Rmask or format.Gmask != Gmask or
                format.Bmask != Bmask or format.Amask != Amask or
                (format.BytesPerPixel >= 3 and bad_loss)):
                # Note: don't free _c_surface here. It will
                # be done in __del__.
                raise ValueError("Invalid mask values")

    def __del__(self):
        if self._c_surface and (sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO) or not \
                                (self._c_surface.flags & sdl.SDL_HWSURFACE)):
            sdl.SDL_FreeSurface(self._c_surface)
        self._c_surface = None
        self._format = None
        self._w = None
        self._h = None

    def __repr__(self):
        surface_type = ('HW' if (self._c_surface.flags & sdl.SDL_HWSURFACE)
                        else 'SW')
        return '<Surface(%dx%dx%s %s)>' % (self._w, self._h,
                                           self._format.BitsPerPixel,
                                           surface_type)

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
            Amask = 0
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

    def crop_to_surface(self, r):
        if r.x >= self._w or r.y >= self._h or r.w <= 0 or r.h <= 0:
            r.x = r.y = r.h = r.w = 0
            return False
        if r.x + r.w <= 0 or r.y + r.h <= 0:
            r.x = r.y = r.h = r.w = 0
            return False
        if r.x < 0:
            r.w += r.x
            r.x = 0
        if r.y < 0:
            r.h += r.y
            r.y = 0
        if r.x + r.w > self._w:
            r.w += self._w - (r.x + r.w)
        if r.y + r.h > self._h:
            r.h += self._h - (r.y + r.h)
        return True

    def fill(self, color, rect=None, special_flags=0):
        """ fill(color, rect=None, special_flags=0) -> Rect
        fill Surface with a solid color
        """
        self.check_opengl()

        c_color = create_color(color, self._format)
        sdlrect = ffi.new('SDL_Rect*')
        if rect is not None:
            sdlrect.x, sdlrect.y, sdlrect.w, sdlrect.h = rect_vals_from_obj(rect)
        else:
            sdlrect.w = self._w
            sdlrect.h = self._h

        if self.crop_to_surface(sdlrect):
            if special_flags:
                res = sdl.surface_fill_blend(self._c_surface, sdlrect,
                                             c_color, special_flags)
            else:
                with locked(self._c_surface):
                    # TODO: prep/unprep
                    res = sdl.SDL_FillRect(self._c_surface, sdlrect, c_color)

            if res == -1:
                raise SDLError.from_sdl_error()

        return Rect._from4(sdlrect.x, sdlrect.y, sdlrect.w, sdlrect.h)

    def blit(self, source, dest, area=None, special_flags=0):
        """ blit(source, dest, area=None, special_flags = 0) -> Rect
        draw one image onto another
        """
        if not self._c_surface or not source._c_surface:
            raise SDLError("display Surface quit")
        if self.is_pure_opengl():
            raise SDLError("Cannot blit to OPENGL Surfaces (OPENGLBLIT is ok)")

        srcrect = ffi.new('SDL_Rect*')
        destrect = ffi.new('SDL_Rect*')
        if area is not None:
            srcrect.x, srcrect.y, srcrect.w, srcrect.h = \
                    rect_vals_from_obj(area)
        else:
            srcrect.w = source._w
            srcrect.h = source._h
        if isinstance(dest, tuple) and len(dest) == 2:
            destrect.x = dest[0]
            destrect.y = dest[1]
            destrect.w = source._w
            destrect.h = source._h
        else:
            destrect.x, destrect.y, destrect.w, destrect.h = \
                    rect_vals_from_obj(dest)

        c_dest = self._c_surface
        c_src = source._c_surface
        c_subsurface = None
        flags = special_flags

        if self.subsurfacedata:
            owner = self.subsurfacedata.owner
            c_subsurface = owner._c_surface
            suboffsetx = self.subsurfacedata.xoffset
            suboffsety = self.subsurfacedata.yoffset
            while owner.subsurfacedata:
                subdata = owner.subsurfacedata
                owner = subdata.owner
                c_subsurface = owner._c_surface
                suboffsetx += subdata.xoffset
                suboffsety += subdata.yoffset

            orig_clip = ffi.new('SDL_Rect*')
            sub_clip = ffi.new('SDL_Rect*')
            sdl.SDL_GetClipRect(c_subsurface, orig_clip)
            sdl.SDL_GetClipRect(self._c_surface, sub_clip)
            sub_clip[0].x += suboffsetx
            sub_clip[0].y += suboffsety
            sdl.SDL_SetClipRect(c_subsurface, sub_clip)
            destrect.x += suboffsetx
            destrect.y += suboffsety
            c_dest = c_subsurface

        # TODO: implement special blend flags
        # these checks come straight from pygame - copied comments
        if (c_dest.format.Amask and (c_dest.flags & sdl.SDL_SRCALPHA) and
                not (c_src.format.Amask and not (c_src.flags & sdl.SDL_SRCALPHA)) and
                (c_dest.format.BytesPerPixel == 2 or c_dest.format.BytesPerPixel == 4)):
            # SDL works for 2 and 4 bytes
            res = sdl.pygame_Blit(c_src, srcrect, c_dest, destrect, flags)
        elif flags or (c_src.flags & (sdl.SDL_SRCALPHA | sdl.SDL_SRCCOLORKEY)
                       and c_dest.pixels == c_src.pixels
                       and check_surface_overlap(c_src, srcrect, c_dest, destrect)):
            '''
            This simplification is possible because a source subsurface
            is converted to its owner with a clip rect and a dst
            subsurface cannot be blitted to its owner because the
            owner is locked.
            '''
            res = sdl.pygame_Blit(c_src, srcrect, c_dest, destrect, flags)
        # can't blit alpha to 8bit, crashes SDL
        elif (c_dest.format.BytesPerPixel == 1 and (c_src.format.Amask
                or c_src.flags & sdl.SDL_SRCALPHA)):
            if c_src.format.BytesPerPixel == 1:
                res = sdl.pygame_Blit(c_src, srcrect, c_dest, destrect, 0)
            elif sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO):
                # TODO: SDL_DisplayFormat segfaults
                c_src = sdl.SDL_DisplayFormat(c_src)
                if c_src:
                    res = sdl.SDL_BlitSurface(c_src, srcrect, c_dest, destrect)
                    sdl.SDL_FreeSurface(c_src)
                else:
                    res = -1
            else:
                raise NotImplementedError()
        else:
            res = sdl.SDL_BlitSurface(c_src, srcrect, c_dest, destrect)
        
        if c_subsurface:
            sdl.SDL_SetClipRect(c_subsurface, orig_clip)
            destrect.x -= suboffsetx
            destrect.y -= suboffsety
        else:
            # TODO: prep/unprep
            pass

        if res == -1:
            raise SDLError.from_sdl_error()
        elif res == -2:
            raise SDLError("Surface was lost")

        return Rect._from4(destrect.x, destrect.y, destrect.w, destrect.h)

    def convert_alpha(self, srcsurf=None):
        with locked(self._c_surface):
            newsurf = sdl.SDL_DisplayFormatAlpha(self._c_surface)
        return Surface._from_sdl_surface(newsurf)

    def get_size(self):
        return self._w, self._h

    def get_width(self):
        return self._w

    def get_height(self):
        return self._h

    def get_pixels(self):
        return self._c_surface.pixels
    _pixels_address = property(get_pixels)

    @classmethod
    def _from_sdl_surface(cls, c_surface):
        surface = cls.__new__(cls)
        surface._c_surface = c_surface
        surface._format = surface._c_surface.format
        surface._w = surface._c_surface.w
        surface._h = surface._c_surface.h
        return surface

    def check_opengl(self):
        self.check_surface()
        if self._c_surface.flags & sdl.SDL_OPENGL:
            raise SDLError("Cannot call on OPENGL Surfaces")

    def check_surface(self):
        if not self._c_surface:
            raise SDLError("display Surface quit")

    def is_pure_opengl(self):
        return self._c_surface.flags & sdl.SDL_OPENGL and not \
            (self._c_surface.flags & (sdl.SDL_OPENGLBLIT & ~sdl.SDL_OPENGL))

    def get_rect(self, **kwargs):
        r = Rect._from4(0, 0, self._w, self._h)
        if kwargs:
            for attr, value in kwargs.iteritems():
                # Logic copied form pygame/surface.c - blame them
                setattr(r, attr, value)
        return r

    def set_at(self, pos, color):
        self.check_opengl()
        x, y = pos
        if x < 0 or y < 0 or x >= self._w or y >= self._h:
            raise IndexError("index out of bounds")
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
            base = y * self._c_surface.pitch + x * 3
            fmt = self._format
            if get_sdl_byteorder() == sdl.SDL_LIL_ENDIAN:
                pixels[base + (fmt.Rshift >> 3)] = ffi.cast('uint8_t', c_color >> 16)
                pixels[base + (fmt.Gshift >> 3)] = ffi.cast('uint8_t', c_color >> 8)
                pixels[base + (fmt.Bshift >> 3)] = ffi.cast('uint8_t', c_color)
            else:
                pixels[base + 2 - (fmt.Rshift >> 3)] = ffi.cast('uint8_t', c_color >> 16)
                pixels[base + 2 - (fmt.Gshift >> 3)] = ffi.cast('uint8_t', c_color >> 8)
                pixels[base + 2 - (fmt.Bshift >> 3)] = ffi.cast('uint8_t', c_color)
        elif bpp == 4:
            pixels = ffi.cast("uint32_t*", self._c_surface.pixels)
            pixels[y * (self._c_surface.pitch // bpp) + x] = c_color
        else:
            raise RuntimeError("invalid color depth for surface")

    def get_at(self, pos):
        self.check_opengl()
        x, y = pos
        if x < 0 or y < 0 or x >= self._w or y >= self._h:
            raise IndexError("index out of bounds")
        with locked(self._c_surface):
            c_color = self._get_at(x, y)
        return self.unmap_rgb(c_color)

    def get_at_mapped(self, pos):
        """ get_at_mapped((x, y)) -> Color
        get the mapped color value at a single pixel
        """
        self.check_opengl()
        x, y = pos
        if x < 0 or y < 0 or x >= self._w or y >= self._h:
            raise IndexError("index out of bounds")
        with locked(self._c_surface):
            c_color = self._get_at(x, y)
        return c_color

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
            base = y * self._c_surface.pitch + x * 3
            return (pixels[base + BYTE0] +
                    (pixels[base + BYTE1] << 8) +
                    (pixels[base + BYTE2] << 16))
        elif bpp == 4:
            pixels = ffi.cast("uint32_t*", self._c_surface.pixels)
            return pixels[y * self._c_surface.pitch // bpp + x]

    def subsurface(self, *rect):
        self.check_opengl()

        try:
            if hasattr(rect[0], '__iter__'):
                rect = game_rect_from_obj(rect[0])
            else:
                rect = game_rect_from_obj(rect)
        except TypeError:
            raise ValueError("not a valid rect style object")

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

        if format.BytesPerPixel == 1 and format.palette:
            sdl.SDL_SetPalette(sub, sdl.SDL_LOGPAL,
                               format.palette.colors, 0,
                               format.palette.ncolors);
        if surf.flags & sdl.SDL_SRCALPHA:
            sdl.SDL_SetAlpha(sub, surf.flags & sdl.SDL_SRCALPHA,
                             format.alpha);
        if surf.flags & sdl.SDL_SRCCOLORKEY:
            sdl.SDL_SetColorKey(sub, surf.flags & (sdl.SDL_SRCCOLORKEY |
                                                   sdl.SDL_RLEACCEL),
                                                   format.colorkey)
        subsurface = Surface._from_sdl_surface(sub)
        data = SubSurfaceData(self, pixeloffset, rect.x, rect.y)
        subsurface.subsurfacedata = data
        return subsurface

    def set_colorkey(self, color=None, flags=0):
        self.check_opengl()
        c_color = 0
        if color is not None:
            c_color = create_color(color, self._format)
            flags |= sdl.SDL_SRCCOLORKEY

        with locked(self._c_surface):
            if sdl.SDL_SetColorKey(self._c_surface, flags, c_color) == -1:
                raise SDLError.from_sdl_error()

    def copy(self):
        self.check_opengl()
        with locked(self._c_surface):
            # TODO: prep/unprep
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

    def get_bounding_rect(self, min_alpha=1):
        """ get_bounding_rect(min_alpha = 1) -> Rect
        find the smallest rect containing data
        """
        self.check_surface()

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
            sdl.SDL_GetRGBA(self._c_surface.format.colorkey,
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

        return Rect._from4(min_x, min_y, max_x - min_x, max_y - min_y)

    def get_flags(self):
        """ get_flags() -> int
        get the additional flags used for the Surface
        """
        self.check_surface()
        return self._c_surface.flags

    def get_bitsize(self):
        """ get_bitsize() -> int
        get the bit depth of the Surface pixel format
        """
        return self._format.BitsPerPixel

    def get_bytesize(self):
        """ get_bytesize() -> int
        get the bytes used per Surface pixel
        """
        return self._format.BytesPerPixel

    def get_palette(self):
        """ get_palette() -> [RGB, RGB, RGB, ...]
        get the color index palette for an 8bit Surface
        """
        palette = self._format.palette
        if not palette:
            raise SDLError("Surface has no palette to get")

        colors = []
        for i in range(palette.ncolors):
            c = palette.colors[i]
            colors.append(Color(c.r, c.g, c.b))
        return colors

    def get_palette_at(self, index):
        """ get_palette_at(index) -> RGB
        get the color for a single entry in a palette
        """
        palette = self._c_surface.format.palette
        if not palette:
            raise SDLError("Surface has no palette to get")
        if index < 0 or index >= palette.ncolors:
            raise IndexError("index out of bounds")

        c = palette.colors[index]
        return Color(c.r, c.g, c.b)

    def set_palette(self, colors):
        """ set_palette([RGB, RGB, RGB, ...]) -> None
        set the color palette for an 8bit Surface
        """
        palette = self._format.palette
        if not palette:
            raise SDLError("Surface has no palette")
        if not hasattr(colors, '__iter__'):
            raise ValueError("Argument must be a sequence type")
        if not sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO):
            raise SDLError("cannot set palette without pygame.display initialized")

        length = min(palette.ncolors, len(colors))
        c_colors = ffi.new('SDL_Color[]', length)
        for i in range(length):
            rgb = colors[i]
            if (not hasattr(rgb, '__iter__')) or len(rgb) < 3 or len(rgb) > 4:
                raise ValueError("takes a sequence of integers of RGB")
            c_colors[i].r = rgb[0]
            c_colors[i].g = rgb[1]
            c_colors[i].b = rgb[2]
            if len(rgb) == 4 and rgb[3] != 255:
                raise ValueError("takes an alpha value of 255")
        sdl.SDL_SetColors(self._c_surface, c_colors, 0, length)

    def set_palette_at(self, index, rgb):
        """ set_palette_at(index, RGB) -> None
        set the color for a single index in an 8bit Surface palette
        """
        palette = self._format.palette
        if not palette:
            raise SDLError("Surface has no palette")
        if index < 0 or index >= palette.ncolors:
            raise IndexError("index out of bounds")
        if not sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO):
            raise SDLError("cannot set palette without pygame.display initialized")
        if (not hasattr(rgb, '__iter__')) or len(rgb) < 3 or len(rgb) > 4:
            raise ValueError("takes a sequence of integers of RGB for argument 2")

        color = ffi.new('SDL_Color*')
        color[0].r = rgb[0]
        color[0].g = rgb[1]
        color[0].b = rgb[2]
        sdl.SDL_SetColors(self._c_surface, color, index, 1)

    def map_rgb(self, col):
        """ map_rgb(Color) -> mapped_int
        convert a color into a mapped color value
        """
        self.check_surface()
        try:
            if len(col) == 3:
                a = 255
            else:
                a = col[3]
            return sdl.SDL_MapRGBA(self._format, col[0], col[1], col[2], a)
        except (IndexError, TypeError):
            raise TypeError("Invalid RGBA argument")

    def unmap_rgb(self, mapped_int):
        """ unmap_rgb(mapped_int) -> Color
        convert a mapped integer color value into a Color
        """
        self.check_surface()
        mapped_int = ffi.cast('uint32_t', mapped_int)
        r, g, b, a = [ffi.new('uint8_t*') for i in range(4)]
        sdl.SDL_GetRGBA(mapped_int, self._format, r, g, b, a)
        return Color(r[0], g[0], b[0], a[0])

    def set_clip(self, rect):
        """ set_clip(rect) -> None
        set the current clipping area of the Surface
        """
        self.check_surface()
        if rect:
            sdlrect = ffi.new('SDL_Rect*')
            sdlrect.x, sdlrect.y, sdlrect.w, sdlrect.h = \
                    rect_vals_from_obj(rect)
            res = sdl.SDL_SetClipRect(self._c_surface, sdlrect)
        else:
            res = sdl.SDL_SetClipRect(self._c_surface, ffi.NULL)
        if res == -1:
            raise SDLError.from_sdl_error()

    def get_clip(self):
        """ get_clip() -> Rect
        get the current clipping area of the Surface
        """
        self.check_surface()
        c_rect = self._c_surface.clip_rect
        return Rect._from4(c_rect.x, c_rect.y, c_rect.w, c_rect.h)

    def get_parent(self):
        """ get_parent() -> Surface
        find the parent of a subsurface
        """
        if self.subsurfacedata:
            return self.subsurfacedata.owner
        return None

    def get_abs_parent(self):
        """ get_abs_parent() -> Surface
        find the top level parent of a subsurface
        """
        if self.subsurfacedata:
            owner = self.subsurfacedata.owner
            while owner.subsurfacedata:
                owner = owner.subsurfacedata.owner
            return owner
        return None

    def get_offset(self):
        """ get_offset() -> (x, y)
        find the position of a child subsurface inside a parent
        """
        if self.subsurfacedata:
            return (self.subsurfacedata.xoffset,
                    self.subsurfacedata.yoffset)
        return (0, 0)

    def get_abs_offset(self):
        """ get_abs_offset() -> (x, y)
        find the absolute position of a child subsurface inside its top level parent
        """
        if self.subsurfacedata:
            subsurf = self.subsurfacedata
            owner = subsurf.owner
            offsetx, offsety = subsurf.xoffset, subsurf.yoffset
            while owner.subsurfacedata:
                subsurf = owner.subsurfacedata
                owner = subsurf.owner
                offsetx += subsurf.xoffset
                offsety += subsurf.yoffset
            return (offsetx, offsety)
        return (0, 0)

    def get_pitch(self):
        """ get_pitch() -> int
        get the number of bytes used per Surface row
        """
        self.check_surface()
        return self._c_surface.flags

    def get_masks(self):
        """ get_masks() -> (R, G, B, A)
        the bitmasks needed to convert between a color and a mapped integer
        """
        self.check_surface()
        format = self._format
        return (format.Rmask, format.Gmask, format.Bmask, format.Amask)

    def set_masks(self, masks):
        """ set_masks((r,g,b,a)) -> None
        set the bitmasks needed to convert between a color and a mapped integer
        """
        self.check_surface()
        try:
            r, g, b, a = [ffi.cast('uint32_t', m) for m in masks]
            format = self._format
            format.Rmask = r
            format.Gmask = g
            format.Bmask = b
            format.Amask = a
        except (ValueError, TypeError):
            raise TypeError("invalid argument for masks")

    def get_shifts(self):
        """ get_shifts() -> (R, G, B, A)
        the bit shifts needed to convert between a color and a mapped integer
        """
        self.check_surface()
        format = self._format
        return  (format.Rshift, format.Gshift, format.Bshift, format.Ashift)

    def set_shifts(self, shifts):
        """ set_shifts((r,g,b,a)) -> None
        sets the bit shifts needed to convert between a color and a mapped integer
        """
        self.check_surface()
        try:
            r, g, b, a = [ffi.cast('uint8_t', s) for s in shifts]
            format = self._format
            format.Rshift = r
            format.Gshift = g
            format.Bshift = b
            format.Ashift = a
        except (ValueError, TypeError):
            raise TypeError("invalid argument for shifts")

    def get_losses(self):
        """ get_losses() -> (R, G, B, A)
        the significant bits used to convert between a color and a mapped integer
        """
        self.check_surface()
        format = self._format
        return (format.Rloss, format.Gloss, format.Bloss, format.Aloss)

    def get_view(self, kind):
        """ get_view(<kind>='2') -> BufferProxy
        return a buffer view of the Surface's pixels.
        """
        self.check_surface()
        raise NotImplementedError

    def get_buffer(self):
        """ get_buffer() -> BufferProxy
        acquires a buffer object for the pixels of the Surface.
        """
        self.check_surface()
        raise NotImplementedError

    def scroll(self, dx=0, dy=0):
        """ scroll(dx=0, dy=0) -> None
        Shift the surface image in place
        """

        self.check_surface()
        if self.is_pure_opengl():
            raise SDLError("Cannot scroll an OPENGL Surfaces (OPENGLBLIT is ok)")

        if not (dx or dy):
            return None

        clip_rect = self._c_surface.clip_rect
        w = clip_rect.w
        h = clip_rect.h
        if dx >= w or dx <= -w or dy >= h or dy <= -h:
            return None

        with locked(self._c_surface):
            bpp = self._c_surface.format.BytesPerPixel
            pitch = self._c_surface.pitch
            pixels = ffi.cast("uint8_t*", self._c_surface.pixels)
            src = dst = pixels + clip_rect.y * pitch + clip_rect.x * bpp
            if dx >= 0:
                w -= dx
                if dy > 0:
                    h -= dy
                    dst += dy * pitch + dx * bpp
                else:
                    h += dy
                    src -= dy * pitch
                    dst += dx * bpp
            else:
                w += dx
                if dy > 0:
                    h -= dy
                    src -= dx * bpp
                    dst += dy * pitch
                else:
                    h += dy
                    src -= dy * pitch + dx * bpp

            if src < dst:
                src += (h - 1) * pitch
                dst += (h - 1) * pitch
                pitch = -pitch

            span = w * bpp
            for _ in range(h):
                sdl.memmove(dst, src, span)
                src += pitch
                dst += pitch

        return None


class SurfaceNoFree(Surface):
    def __del__(self):
        pass
