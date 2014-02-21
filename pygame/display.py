"""pygame module to control the display window and screen"""

from pygame._sdl import sdl, ffi, pre_video_init
from pygame._error import SDLError, unpack_rect
from pygame.rect import rect_from_obj
from pygame.surface import Surface


def init():
    """ init() -> None
    Initialize the display module
    """
    pre_video_init()
    if sdl.SDL_Init(sdl.SDL_INIT_VIDEO) == -1:
        raise SDLError.from_sdl_error()


def quit():
    """ quit() -> None
    Uninitialize the display module
    """
    sdl.SDL_Quit()


def check_video():
    if not get_init():
        raise SDLError("Display not initialized")


def get_init():
    """ get_init() -> bool
    Returns True if the display module has been initialized
    """
    return sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO) != 0


def flip():
    """ flip() -> None
    Update the full display Surface to the screen
    """
    if not get_init():
        raise SDLError("video system not initialized")

    screen = sdl.SDL_GetVideoSurface()
    if not screen:
        raise SDLError("Display mode not set")

    status = sdl.SDL_Flip(screen)

    if status == -1:
        raise SDLError.from_sdl_error()


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

    if depth == 0:
        flags |= sdl.SDL_ANYFORMAT
    c_surface = sdl.SDL_SetVideoMode(w, h, 0, flags)
    if not c_surface:
        raise SDLError.from_sdl_error()

    title = ffi.new("char*[1]")
    icon = ffi.new("char*[1]")

    sdl.SDL_WM_GetCaption(title, icon)
    if not title:
        sdl.SDL_WM_SetCaption("pygame window", "pygame")

    # pygame does this, so it's possibly a good idea
    sdl.SDL_PumpEvents()

    return Surface._from_sdl_surface(c_surface)


def mode_ok((h, w), flags, depth=None):
    """ mode_ok(size, flags=0, depth=0) -> depth
    Pick the best color depth for a display mode
    """
    if depth is None:
        depth = sdl.SDL_GetVideoInfo().vfmt.BitsPerPixel
    return sdl.SDL_VideoModeOK(w, h, depth, flags)


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
    return Surface._from_sdl_surface(sdl.SDL_GetVideoSurface())


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


def update(rectangle=None):
    """ update(rectangle=None) -> None
    update(rectangle_list) -> None
    Update portions of the screen for software displays
    """
    if not get_init():
        raise SDLError("video system not initialized")

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

        rect_li = []
        for obj in rects:
            if not obj:
                continue
            rect = rect_from_obj(obj)
            if screen_crop_rect(rect, screen.w, screen.h):
                rect_li.append(rect)

        rect_array = ffi.new('SDL_Rect[]', len(rect_li))
        for i, rect in enumerate(rect_li):
            rect_array[i] = rect[0]
        sdl.SDL_UpdateRects(screen, len(rect_li), rect_array)

    except (NotImplementedError, TypeError):
        raise ValueError("update requires a rectstyle or sequence of recstyles")


def get_driver():
    """ get_driver() -> name
    Get the name of the pygame display backend
    """
    pass


def Info():
    """ Info() -> VideoInfo
    Create a video display information object
    """
    pass


def get_wm_info():
    """ get_wm_info() -> dict
    Get information about the current windowing system
    """
    pass


def list_modes():
    """ list_modes(depth=0, flags=pygame.FULLSCREEN) -> list
    Get list of available fullscreen modes
    """
    pass


def mode_ok():
    """ mode_ok(size, flags=0, depth=0) -> depth
    Pick the best color depth for a display mode
    """
    pass


def gl_get_attribute():
    """ gl_get_attribute(flag) -> value
    Get the value for an OpenGL flag for the current display
    """
    pass


def gl_set_attribute():
    """ gl_set_attribute(flag, value) -> None
    Request an OpenGL display attribute for the display mode
    """
    pass


def get_active():
    """ get_active() -> bool
    Returns True when the display is active on the display
    """
    pass


def iconify():
    """ iconify() -> bool
    Iconify the display surface
    """
    pass


def toggle_fullscreen():
    """ toggle_fullscreen() -> bool
    Switch between fullscreen and windowed displays
    """
    pass


def set_gamma():
    """ set_gamma(red, green=None, blue=None) -> bool
    Change the hardware gamma ramps
    """
    pass


def set_gamma_ramp():
    """ set_gamma_ramp(red, green, blue) -> bool
    Change the hardware gamma ramps with a custom lookup
    """
    pass


def set_palette():
    """ set_palette(palette=None) -> None
    Set the display color palette for indexed displays
    """
    pass

