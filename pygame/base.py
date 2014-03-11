""" the top level pygame package
"""
import atexit
import platform
import sys
try:
    import thread
    _with_thread = True
except ImportError:
    _with_thread = False

from pygame._sdl import sdl, get_sdl_version, get_sdl_byteorder
from pygame._error import SDLError

# TODO: not sure whether it should be True or False
HAVE_NEWBUF = False

_sdl_was_init = False
_quit_functions = []


if platform.system().startswith('Darwin'):
    from pygame.macosx import pre_video_init
else:
    def pre_video_init():
        pass


def video_autoinit():
    if not sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO):
        pre_video_init()
        if sdl.SDL_InitSubSystem(sdl.SDL_INIT_VIDEO):
            return False
        sdl.SDL_EnableUNICODE(1)
    return True


def video_autoquit():
    if sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO):
        sdl.SDL_QuitSubSystem(sdl.SDL_INIT_VIDEO)


def register_quit(quit_func):
    _quit_functions.append(quit_func)


def init():
    """ init() -> (numpass, numfail)
    initialize all imported pygame modules
    """
    # check that the SDL version is supported
    # TODO: preserve backwards compatibility in mixer, RWops, etc
    major, minor, patch = get_sdl_version()
    try:
        assert major == 1
        assert minor == 2
        assert patch >= 9
    except AssertionError:
        raise RuntimeError("Current version of SDL is %i.%i.%i. Only SDL "
                           "versions >= 1.2.9, < 2.0.0 are supported." %
                           (major, minor, patch))

    global _sdl_was_init
    if not platform.system().startswith('Windows') and _with_thread:
        _sdl_was_init = sdl.SDL_Init(sdl.SDL_INIT_TIMER |
                                     sdl.SDL_INIT_NOPARACHUTE |
                                     sdl.SDL_INIT_EVENTTHREAD)
    else:
        _sdl_was_init = sdl.SDL_Init(sdl.SDL_INIT_TIMER |
                                     sdl.SDL_INIT_NOPARACHUTE)
    if _sdl_was_init == -1:
        raise SDLError.from_sdl_error()

    # initialize all the things!
    success, fail = 0, 0
    if video_autoinit():
        success += 1
    else:
        fail += 1

    # pygame inspects sys.modules and finds all __PYGAMEinit__ functions.
    # We look for autoinit and only consider submodules of pygame.
    # pygame normally initializes 6 modules.
    # We are at 4 modules: cdrom and joystick are missing
    modules = [v for k, v in sys.modules.iteritems() if k.startswith('pygame.')
               and v is not None and v != sys.modules[__name__]]
    for module in modules:
        init_call = getattr(module, 'autoinit', None)
        if hasattr(init_call, '__call__'):
            if init_call():
                success += 1
            else:
                fail += 1

    return success, fail


def quit():
    """ quit() -> None
    uninitialize all pygame modules
    """
    # quit in reverse order of initialization
    for quit_func in reversed(_quit_functions):
        quit_func()

    atexit_quit()


@atexit.register
def atexit_quit():
    video_autoquit()

    global _sdl_was_init
    if _sdl_was_init:
        _sdl_was_init = False
        sdl.SDL_Quit()
