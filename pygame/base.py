""" the top level pygame package
"""

from pygame._sdl import sdl
from pygame.error import SDLError
from pygame import display


def init():
    """ init() -> (numpass, numfail)
    initialize all imported pygame modules
    """
    # TODO: this is a pale shadow of the madness inside pygame.base.init()
    res = sdl.SDL_Init(sdl.SDL_INIT_TIMER | sdl.SDL_INIT_NOPARACHUTE)
    if res == -1:
        raise SDLError.from_sdl_error()
    display.init()


def quit():
    """ quit() -> None
    uninitialize all pygame modules
    """
    # TODO: this is a pale shadow of the madness inside pygame.base.quit()
    sdl.SDL_Quit()


def get_sdl_version():
    """ get_sdl_version() -> major, minor, patch
    get the version number of SDL
    """
    v = sdl.SDL_Linked_Version()
    return (v.major, v.minor, v.patch)
