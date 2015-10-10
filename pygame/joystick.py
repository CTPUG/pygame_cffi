"""Pygame module for interacting with joysticks, gamepads, and trackballs."""

from pygame._error import SDLError
from pygame._sdl import ffi, sdl
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
    for joydata in Joystick._OPEN_JOYSTICKS:
        sdl.SDL_JoystickClose(joydata)
    Joystick._OPEN_JOYSTICKS.clear()

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

    _OPEN_JOYSTICKS = {}

    def __init__(self, i):
        _check_init()
        if i < 0 or i >= get_count():
            raise SDLError("Invalid joystick device number")
        self._id = i

    @property
    def _joydata(self):
        joydata = self._OPEN_JOYSTICKS.get(self._id)
        if not joydata:
            raise SDLError("Joystick not initialized")
        return joydata

    def init(self):
        """ init() -> None
        initialize the Joystick
        """
        if self._id not in self._OPEN_JOYSTICKS:
            joydata = sdl.SDL_JoystickOpen(self._id)
            if not joydata:
                raise SDLError.from_sdl_error()
            self._OPEN_JOYSTICKS[self._id] = joydata

    def quit(self):
        """ quit() -> None
        uninitialize the Joystick
        """
        joydata = self._OPEN_JOYSTICKS.get(self._id)
        if joydata:
            sdl.SDL_JoystickClose(joydata)
            del self._OPEN_JOYSTICKS[self._id]

    def get_init(self):
        """ get_init() -> bool
        check if the Joystick is initialized
        """
        return self._OPEN_JOYSTICKS.get(self._id) is not None

    def get_id(self):
        """ get_id() -> int
        get the Joystick ID
        """
        return self._id

    def get_name(self):
        """ get_name() -> string
        get the Joystick system name
        """
        return ffi.string(sdl.SDL_JoystickName(self._id))

    def get_numaxes(self):
        """ get_numaxes() -> int
        get the number of axes on a Joystick
        """
        return sdl.SDL_JoystickNumAxes(self._joydata)

    def get_axis(self, i):
        """ get_axis(axis_number) -> float
        get the current position of an axis
        """
        joydata = self._joydata
        if i < 0 or i >= sdl.SDL_JoystickNumAxes(joydata):
            raise SDLError("Invalid joystick axis")

        value = sdl.SDL_JoystickGetAxis(joydata, i)
        return value / 32768.0

    def get_numballs(self):
        """ get_numballs() -> int
        get the number of trackballs on a Joystick
        """
        return sdl.SDL_JoystickNumBalls(self._joydata)

    def get_ball(self, i):
        """ get_ball(ball_number) -> x, y
        get the relative position of a trackball
        """
        joydata = self._joydata
        if i < 0 or i >= sdl.SDL_JoystickNumBalls(joydata):
            raise SDLError("Invalid joystick trackball")

        dx, dy = ffi.new('int*'), ffi.new('int*')
        sdl.SDL_JoystickGetBall(joydata, i, dx, dy)
        return (dx[0], dy[0])

    def get_numbuttons(self):
        """ get_numbuttons() -> int
        get the number of buttons on a Joystick
        """
        return sdl.SDL_JoystickNumButtons(self._joydata)

    def get_button(self, i):
        """ get_button(button) -> bool
        get the current button state
        """
        joydata = self._joydata
        if i < 0 or i >= sdl.SDL_JoystickNumButtons(joydata):
            raise SDLError("Invalid joystick button")
        return sdl.SDL_JoystickGetButton(joydata, i)

    def get_numhats(self):
        """ get_numhats() -> int
        get the number of hat controls on a Joystick
        """
        return sdl.SDL_JoystickNumHats(self._joydata)

    def get_hat(self, i):
        """ get_hat(hat_number) -> x, y
        get the position of a joystick hat
        """
        joydata = self._joydata
        if i < 0 or i >= sdl.SDL_JoystickNumHats(joydata):
            raise SDLError("Invalid joystick hat")
        value = sdl.SDL_JoystickGetHat(joydata, i)

        px = py = 0
        if value & sdl.SDL_HAT_UP:
            py = 1
        elif value & sdl.SDL_HAT_DOWN:
            py = -1
        if value & sdl.SDL_HAT_RIGHT:
            px = 1
        elif value & sdl.SDL_HAT_LEFT:
            px = -1

        return (px, py)

# alias for pygame compatibility
JoystickType = Joystick
