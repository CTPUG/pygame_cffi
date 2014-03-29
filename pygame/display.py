"""pygame module to control the display window and screen"""

from pygame._sdl import sdl, ffi, get_sdl_version
from pygame._error import SDLError, unpack_rect
from pygame.base import video_autoinit, video_autoquit, register_quit
from pygame.rect import game_rect_from_obj
from pygame.surface import SurfaceNoFree, Surface


# the global display surface approach comes from pygame
_display_surface = None


class VidInfo(object):
    _c_vidinfo = None

    def __init__(self, info):
        self._c_vidinfo = info
        self._current_w = -1
        self._current_h = -1
        sdl_v = get_sdl_version()
        if sdl_v[0] >= 1 and sdl_v[1] >= 2 and sdl_v[2] >= 10:
            self._current_w = info.current_w
            self._current_h = info.current_h

    @property
    def hw(self):
        return self._c_vidinfo.hw_available

    @property
    def wm(self):
        return self._c_vidinfo.wm_available

    @property
    def blit_hw(self):
        return self._c_vidinfo.blit_hw

    @property
    def blit_hw_CC(self):
        return self._c_vidinfo.blit_hw_CC

    @property
    def blit_hw_A(self):
        return self._c_vidinfo.blit_hw_A

    @property
    def blit_sw(self):
        # XXX: sw swapped with hw in pygame
        return self._c_vidinfo.blit_sw

    @property
    def blit_sw_CC(self):
        # XXX: sw swapped with hw in pygame
        return self._c_vidinfo.blit_sw_CC

    @property
    def blit_sw_A(self):
        # XXX: sw swapped with hw in pygame
        return self._c_vidinfo.blit_sw_A

    @property
    def blit_fill(self):
        return self._c_vidinfo.blit_fill

    @property
    def video_mem(self):
        return self._c_vidinfo.video_mem

    @property
    def bitsize(self):
        return self._c_vidinfo.vfmt.BitsPerPixel

    @property
    def bytesize(self):
        return self._c_vidinfo.vfmt.BytesPerPixel

    @property
    def masks(self):
        return (self._c_vidinfo.vfmt.Rmask, self._c_vidinfo.vfmt.Gmask,
                self._c_vidinfo.vfmt.Bmask, self._c_vidinfo.vfmt.Amask)

    @property
    def shifts(self):
        return (self._c_vidinfo.vfmt.Rshift, self._c_vidinfo.vfmt.Gshift,
                self._c_vidinfo.vfmt.Bshift, self._c_vidinfo.vfmt.Ashift)

    @property
    def losses(self):
        return (self._c_vidinfo.vfmt.Rloss, self._c_vidinfo.vfmt.Gloss,
                self._c_vidinfo.vfmt.Bloss, self._c_vidinfo.vfmt.Aloss)

    @property
    def current_h(self):
        return self._current_h

    @property
    def current_w(self):
        return self._current_w

    def __repr__(self):
        return ("<VideoInfo(hw = %d, wm = %d,video_mem = %d\n"
                "         blit_hw = %d, blit_hw_CC = %d, blit_hw_A = %d,\n"
                "         blit_sw = %d, blit_sw_CC = %d, blit_sw_A = %d,\n"
                "         bitsize  = %d, bytesize = %d,\n"
                "         masks =  %r,\n"
                "         shifts = %r,\n"
                "         losses =  %r,\n"
                "         current_w = %d, current_h = %d\n"
                ">\n") % (self.hw, self.wm, self.video_mem, self.blit_hw,
                          self.blit_hw_CC, self.blit_hw_A, self.blit_sw,
                          self.blit_sw_CC, self.blit_sw_A, self.bitsize,
                          self.bytesize, self.masks, self.shifts, self.losses,
                          self.current_w, self.current_h)

    def __str__(self):
        return self.__repr__()


def autoinit():
    register_quit(autoquit)
    return True


def autoquit():
    global _display_surface
    _display_surface = None


def init():
    """ init() -> None
    Initialize the display module
    """
    if not video_autoinit():
        raise SDLError.from_sdl_error()
    if not autoinit():
        raise RuntimeError("autoinit failed")


def quit():
    """ quit() -> None
    Uninitialize the display module
    """
    video_autoquit()
    autoquit()


def check_video():
    if not get_init():
        raise SDLError("video system not initialized")


def check_opengl():
    screen = sdl.SDL_GetVideoSurface()
    if not screen:
        raise SDLError("Display mode not set")

    if not (screen.flags & sdl.SDL_OPENGL):
        raise SDLError("Not an OPENGL display")


def get_init():
    """ get_init() -> bool
    Returns True if the display module has been initialized
    """
    return sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO) != 0


def flip():
    """ flip() -> None
    Update the full display Surface to the screen
    """
    check_video()

    screen = sdl.SDL_GetVideoSurface()
    if not screen:
        raise SDLError("Display mode not set")

    if screen.flags & sdl.SDL_OPENGL:
        sdl.SDL_GL_SwapBuffers()
        status = 0
    else:
        status = sdl.SDL_Flip(screen)

    if status == -1:
        raise SDLError.from_sdl_error()


def update(rectangle=None):
    """ update(rectangle=None) -> None
    update(rectangle_list) -> None
    Update portions of the screen for software displays
    """
    check_video()

    screen = sdl.SDL_GetVideoSurface()
    if not screen:
        raise SDLError("Display mode not set")

    if (screen.flags & sdl.SDL_OPENGL):
        raise SDLError("Cannot update an OPENGL display")

    if not rectangle:
        sdl.SDL_UpdateRect(screen, 0, 0, 0, 0)
        return

    try:
        if hasattr(rectangle, '__iter__'):
            # it can either be a rect style 4-tuple or
            # a sequence of rects or rect styles
            try:
                int(rectangle[0])
                rects = (rectangle, )
            except (ValueError, TypeError):
                rects = rectangle
        else:
            rects = (rectangle, )

        if len(rects) == 1:
            rect = game_rect_from_obj(rects[0])
            if screen_crop_rect(rect, screen.w, screen.h):
                sdl.SDL_UpdateRect(screen, rect.x, rect.y, rect.w, rect.h)
            return

        rect_array = ffi.new('SDL_Rect[]', len(rects))
        count = 0
        for obj in rects:
            if not obj:
                continue
            rect = game_rect_from_obj(obj)
            if screen_crop_rect(rect, screen.w, screen.h):
                sdlrect = rect_array[count]
                sdlrect.x = rect.x
                sdlrect.y = rect.y
                sdlrect.w = rect.w
                sdlrect.h = rect.h
                count += 1

        sdl.SDL_UpdateRects(screen, count, rect_array)

    except (NotImplementedError, TypeError):
        raise ValueError("update requires a rectstyle or sequence of recstyles")


def set_mode(resolution=(0, 0), flags=0, depth=0):
    """ set_mode(resolution=(0,0), flags=0, depth=0) -> Surface
    Initialize a window or screen for display
    """
    w, h = unpack_rect(resolution)
    if w < 0 or h < 0:
        raise SDLError("Cannot set negative sized display mode")

    if flags == 0:
        flags = sdl.SDL_SWSURFACE

    if not get_init():
        init()

    # depth and double buffering attributes need to be set specially for OpenGL
    if flags & sdl.SDL_OPENGL:
        if flags & sdl.SDL_DOUBLEBUF:
            gl_set_attribute(sdl.SDL_GL_DOUBLEBUFFER, 1)
        else:
            gl_set_attribute(sdl.SDL_GL_DOUBLEBUFFER, 0)
        if depth:
            gl_set_attribute(sdl.SDL_GL_DEPTH_SIZE, depth)

        c_surface = sdl.SDL_SetVideoMode(w, h, depth, flags)
        if c_surface and gl_get_attribute(sdl.SDL_GL_DOUBLEBUFFER):
            c_surface.flags |= sdl.SDL_DOUBLEBUF

    else:
        if depth == 0:
            flags |= sdl.SDL_ANYFORMAT
        c_surface = sdl.SDL_SetVideoMode(w, h, depth, flags)

    if not c_surface:
        raise SDLError.from_sdl_error()

    title = ffi.new("char*[1]")
    icon = ffi.new("char*[1]")

    sdl.SDL_WM_GetCaption(title, icon)
    if not title:
        sdl.SDL_WM_SetCaption("pygame window", "pygame")

    # pygame does this, so it's possibly a good idea
    sdl.SDL_PumpEvents()

    global _display_surface
    _display_surface = SurfaceNoFree._from_sdl_surface(c_surface)
    # TODO: set icon stuff
    return _display_surface


def mode_ok((w, h), flags=0, depth=None):
    """ mode_ok(size, flags=0, depth=0) -> depth
    Pick the best color depth for a display mode
    """
    if depth is None:
        depth = sdl.SDL_GetVideoInfo().vfmt.BitsPerPixel
    return sdl.SDL_VideoModeOK(w, h, depth, flags)


def list_modes(depth=None, flags=sdl.SDL_FULLSCREEN):
    """ list_modes(depth=0, flags=pygame.FULLSCREEN) -> list
    Get list of available fullscreen modes
    """
    check_video()

    format = ffi.new('SDL_PixelFormat*')
    if depth is None:
        format.BitsPerPixel = sdl.SDL_GetVideoInfo().vfmt.BitsPerPixel
    else:
        format.BitsPerPixel = depth

    rects = sdl.SDL_ListModes(format, flags)
    if rects == ffi.NULL:
        return []

    counter = 0
    rect = rects[0]
    sizes = []
    while rect != ffi.NULL:
        sizes.append((rect.w, rect.h))
        counter += 1
        rect = rects[counter]
    return sizes


def set_caption(title, icontitle=None):
    """ set_caption(title, icontitle=None) -> None
    Set the current window caption
    """
    if not isinstance(title, basestring):
        raise TypeError("Must be string, not %s" % type(title))
    if not icontitle:
        icontitle = title
    elif not isinstance(icontitle, basestring):
        raise TypeError("Must be string, not %s" % type(icontitle))
    sdl.SDL_WM_SetCaption(title, icontitle)


def get_caption():
    """ get_caption() -> (title, icontitle)
    Get the current window caption
    """
    title = ffi.new("char*[1]")
    icon = ffi.new("char*[1]")

    sdl.SDL_WM_GetCaption(title, icon)
    return ffi.string(title[0]), ffi.string(icon[0])


def get_surface():
    """ get_surface() -> Surface
    Get a reference to the currently set display surface
    """
    check_video()
    return _display_surface


def set_icon(icon):
    """ set_icon(Surface) -> None
    Change the system image for the display window
    """
    check_video()
    if not isinstance(icon, Surface):
        raise TypeError("Expected a pygame.surface.Surface, got %r" %
                        (type(icon),))
    sdl.SDL_WM_SetIcon(icon._c_surface, ffi.NULL)


def screen_crop_rect(r, w, h):
    if (r.x > w) or (r.y > h) or (r.x + r.w <= 0) or (r.y + r.h <= 0):
        return None
    right = min(r.x + r.w, w)
    bottom = min(r.y + r.h, h)
    r.x = max(r.x, 0)
    r.y = max(r.y, 0)
    r.w = right - r.x
    r.h = bottom - r.y
    return r


def get_driver():
    """ get_driver() -> name
    Get the name of the pygame display backend
    """
    check_video()

    buffer_len = 256
    buf = ffi.new('char[]', buffer_len)
    if not sdl.SDL_VideoDriverName(buf, buffer_len):
        return None
    return ffi.string(buf)


def Info():
    """ Info() -> VideoInfo
    Create a video display information object
    """
    check_video()
    return VidInfo(sdl.SDL_GetVideoInfo())


def get_wm_info():
    """ get_wm_info() -> dict
    Get information about the current windowing system
    """
    # XXX
    raise NotImplementedError


def gl_get_attribute(flag):
    """ gl_get_attribute(flag) -> value
    Get the value for an OpenGL flag for the current display
    """
    check_video()
    # pygame seg faults instead of doing this
    # check_opengl()

    value = ffi.new('int *')
    if sdl.SDL_GL_GetAttribute(flag, value) == -1:
        raise SDLError.from_sdl_error()
    return value[0]


def gl_set_attribute(flag, value):
    """ gl_set_attribute(flag, value) -> None
    Request an OpenGL display attribute for the display mode
    """
    check_video()
    # check_opengl()

    if flag == -1:
        return None
    if sdl.SDL_GL_SetAttribute(flag, value) == -1:
        raise SDLError.from_sdl_error()


def get_active():
    """ get_active() -> bool
    Returns True when the display is active on the display
    """
    return (sdl.SDL_GetAppState() & sdl.SDL_APPACTIVE) != 0


def iconify():
    """ iconify() -> bool
    Iconify the display surface
    """
    check_video()
    return (sdl.SDL_WM_IconifyWindow() != 0)


def toggle_fullscreen():
    """ toggle_fullscreen() -> bool
    Switch between fullscreen and windowed displays
    """
    check_video()

    screen = sdl.SDL_GetVideoSurface()
    if not screen:
        raise SDLError("Display mode not set")
    return (sdl.SDL_WM_ToggleFullScreen(screen) != 0)


def set_gamma(red, green=None, blue=None):
    """ set_gamma(red, green=None, blue=None) -> bool
    Change the hardware gamma ramps
    """
    if green is None and blue is None:
        green = blue = red
    elif green is None or blue is None:
        raise ValueError("set_gamma requires either 1 or 3 arguments")

    check_video()
    return (sdl.SDL_SetGamma(red, green, blue) == 0)


def set_gamma_ramp(r, g, b):
    """ set_gamma_ramp(red, green, blue) -> bool
    Change the hardware gamma ramps with a custom lookup
    """
    if not (hasattr(r, '__iter__') and
            hasattr(g, '__iter__') and
            hasattr(b, '__iter__')):
        raise TypeError("gamma ramp must be sequence type")

    if not (len(r) == len(g) == len(b) == 256):
        raise ValueError("gamma ramp must be 256 elements long")

    try:
        c_r = ffi.new('uint16_t[256]', r)
        c_g = ffi.new('uint16_t[256]', g)
        c_b = ffi.new('uint16_t[256]', b)
    except OverflowError:
        raise ValueError("gamma ramp value must be between 0 and 65535")
    except TypeError:
        raise ValueError("gamma ramp must contain integer elements")

    check_video()
    return (sdl.SDL_SetGammaRamp(c_r, c_g, c_b) == 0)


def set_palette(palette=None):
    """ set_palette(palette=None) -> None
    Set the display color palette for indexed displays
    """
    check_video()

    screen = sdl.SDL_GetVideoSurface()
    if not screen:
        raise SDLError("Display mode not set")

    if palette and not hasattr(palette, '__iter__'):
        raise TypeError("Argument must be a sequence type")

    default_pal = screen.format.palette
    if screen.format.BytesPerPixel != 1 or default_pal is None:
        raise SDLError("Display mode is not colormapped")

    if palette is None:
        sdl.SDL_SetPalette(screen, sdl.SDL_PHYSPAL,
                           default_pal.colors, 0, default_pal.ncolors)
    else:
        ncolors = min(default_pal.ncolors, len(palette))
        colors = ffi.new('SDL_Color[]', ncolors)
        for i in range(ncolors):
            try:
                r, g, b = palette[i]
            except (ValueError, TypeError):
                raise TypeError("takes a sequence of sequence of RGB")
            try:
                colors[i].r = r
                colors[i].g = g
                colors[i].b = b
            except:
                raise TypeError("RGB sequence must contain numeric values")
        sdl.SDL_SetPalette(screen, sdl.SDL_PHYSPAL, colors, 0, ncolors)
