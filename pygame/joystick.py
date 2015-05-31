"""Pygame module for interacting with joysticks, gamepads, and trackballs."""

from pygame._error import SDLError
from pygame._sdl import sdl
from pygame.base import register_quit


def _check_init():
    if not sdl.SDL_WasInit(sdl.SDL_INIT_JOYSTICK):
        raise SDLError("joystick system not initialized")


def autoinit():
    if not sdl.SDL_WasInit(sdl.SDL_INIT_JOYSTICK):
        if sdl.SDL_InitSubSystem(sdl.SDL_INIT_JOYSTICK):
            return False
        sdl.SDL_JoystickEventState(sdl.SDL_ENABLE)
        register_quit(autoquit)
    return True


def autoquit():
    # TODO: this three lists are really just a reminder that
    #       we need to close joysticks before exiting
    for joystick in Joystick._JOYSTICKS:
        sdl.SDL_JoystickClose(joystick._sdl_data)
    del Joystick._JOYSTICKS[:]

    if sdl.SDL_WasInit(sdl.SDL_INIT_JOYSTICK):
        sdl.SDL_JoystickEventState(sdl.SDL_DISABLE)
        sdl.SDL_QuitSubSystem(sdl.SDL_INIT_JOYSTICK)


def init():
    """ init() -> None
    Initialize the joystick module.
    """
    if not autoinit():
        SDLError.from_sdl_error()


def quit():
    """ quit() -> None
    Uninitialize the joystick module.
    """
    autoquit()


def get_init():
    """ get_init() -> bool
    Returns True if the joystick module is initialized.
    """
    return sdl.SDL_WasInit(sdl.SDL_INIT_JOYSTICK) != 0


def get_count():
    """ get_count() -> count
    Returns the number of joysticks.
    """
    _check_init()
    return sdl.SDL_NumJoysticks()


class Joystick(object):
    """ Joystick(id) -> Joystick
    Create a new Joystick object.
    """

    # to allow clean-up of joysticks
    _JOYSTICKS = []

    def init(self):
        """ init() -> None
        initialize the Joystick
        """
        TODO

    def quit(self):
        """ quit() -> None
        uninitialize the Joystick
        """
        TODO

    def get_init(self):
        """ get_init() -> bool
        check if the Joystick is initialized
        """
        TODO

    def get_id(self):
        """ get_id() -> int
        get the Joystick ID
        """
        TODO

    def get_name(self):
        """ get_name() -> string
        get the Joystick system name
        """
        TODO

    def get_numaxes(self):
        """ get_numaxes() -> int
        get the number of axes on a Joystick
        """
        TODO

    def get_axis(self, axis_number):
        """ get_axis(axis_number) -> float
        get the current position of an axis
        """
        TODO

    def get_numballs(self):
        """ get_numballs() -> int
        get the number of trackballs on a Joystick
        """
        TODO

    def get_ball(self, ball_number):
        """ get_ball(ball_number) -> x, y
        get the relative position of a trackball
        """
        TODO

    def get_numbuttons(self):
        """ get_numbuttons() -> int
        get the number of buttons on a Joystick
        """
        TODO

    def get_button(self, button):
        """ get_button(button) -> bool
        get the current button state
        """
        TODO

    def get_numhats(self):
        """ get_numhats() -> int
        get the number of hat controls on a Joystick
        """
        TODO

    def get_hat(self, hat_number):
        """ get_hat(hat_number) -> x, y
        get the position of a joystick hat
        """
        TODO

# alias for pygame compatibility
JoystickType = Joystick
