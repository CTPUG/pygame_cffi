""" Key module """

from pygame._error import SDLError
from pygame._sdl import ffi, sdl
from pygame.display import check_video


def get_focused():
    """ get_focused() -> bool
    true if the display is receiving keyboard input from the system
    """
    check_video()
    return (sdl.SDL_GetAppState() & sdl.SDL_APPINPUTFOCUS) != 0


def get_pressed():
    """ get_pressed() -> bools
    get the state of all keyboard buttons
    """
    check_video()
    num_keys = ffi.new('int*')
    key_state = sdl.SDL_GetKeyState(num_keys)
    num_keys = num_keys[0]
    if not key_state or not num_keys:
        return None
    return [key_state[i] for i in range(num_keys)]


def get_mods():
    """ get_mods() -> int
    determine which modifier keys are being held
    """
    check_video()
    return sdl.SDL_GetModState()


def set_mods(mod_int):
    """ set_mods(int) -> None
    temporarily set which modifier keys are pressed
    """
    check_video()
    sdl.SDL_SetModState(int(mod_int))


def set_repeat(delay=0, interval=0):
    """ set_repeat() -> None
    control how held keys are repeated
    """
    check_video()
    if delay and not interval:
        interval = delay
    if sdl.SDL_EnableKeyRepeat(delay, interval) == -1:
        raise SDLError.from_sdl_error()


def get_repeat():
    """ get_repeat() -> (delay, interval)
    see how held keys are repeated
    """
    check_video()
    delay, interval = ffi.new('int*'), ffi.new('int*')
    sdl.SDL_GetKeyRepeat(delay, interval)
    return (delay[0], interval[0])


def name(key):
    """ name(key) -> string
    get the name of a key identifier
    """
    return ffi.string(sdl.SDL_GetKeyName(int(key)))
