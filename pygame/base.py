""" the top level pygame package
"""
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
    # TODO: CheckSDLVersions()
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
    # pygame inspects sys.modules but checks for
    # __PYGAMEinit__ attr instead of init
    modules = [v for k, v in sys.modules.iteritems() if k.startswith('pygame.')
               and v is not None and v != sys.modules[__name__]]
    for module in modules:
        init_call = getattr(module, 'init', None)
        if hasattr(init_call, '__call__'):
            if init_call() is None:
                success += 1
            else:
                fail += 1

    return success, fail


def quit():
    """ quit() -> None
    uninitialize all pygame modules
    """
    # TODO: this is a pale shadow of the madness inside pygame.base.quit()
    for quit_func in reversed(_quit_functions):
        quit_func()

    global _sdl_was_init
    if _sdl_was_init:
        _sdl_was_init = False
        sdl.SDL_Quit()
