"""pygame module to control the display window and screen"""

from pygame._sdl import sdl, ffi
from pygame.error import SDLError, unpack_rect
from pygame.surface import Surface


def init():
    """ init() -> None
    Initialize the display module
    """
    if sdl.SDL_Init(sdl.SDL_INIT_VIDEO) == -1:
        raise SDLError.from_sdl_error()


def quit():
    """ quit() -> None
    Uninitialize the display module
    """
    sdl.SDL_Quit()


def get_init():
    """ get_init() -> bool
    Returns True if the display module has been initialized
    """
    return sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO) != 0


def flip():
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

    sdl.SDL_WM_SetCaption(title, icon)
    if not title:
        sdl.SDL_WM_SetCaption("pygame window", "pygame");

    # pygame does this, so it's possibly a good idea
    sdl.SDL_PumpEvents()

    return Surface._from_sdl_surface(c_surface)
