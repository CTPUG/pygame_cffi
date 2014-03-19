""" pygame module for monitoring time
"""

from pygame._sdl import sdl, ffi
from pygame._error import SDLError


WORST_CLOCK_ACCURACY = 12


def _get_init():
    return sdl.SDL_WasInit(sdl.SDL_INIT_TIMER)


def _try_init():
    if not _get_init():
        if sdl.SDL_InitSubSystem(sdl.SDL_INIT_TIMER):
            raise SDLError.from_sdl_error()


class Clock(object):
    """ Clock() -> Clock
    create an object to help track time
    """

    def __init__(self):
        _try_init()
        self._last_tick = get_ticks()
        self._rawpassed = 0
        self._fps_count = 0
        self._fps_tick = 0
        self._fps = 0.0

    def _base(self, framerate=None, use_accurate_delay=False):
        if framerate:
            endtime = int((1.0 / framerate) * 1000.)
            self._rawpassed = sdl.SDL_GetTicks() - self._last_tick
            delay = endtime - self._rawpassed

            _try_init()

            if use_accurate_delay:
                delay = _accurate_delay(delay);
            else:
                delay = max(delay, 0)
                sdl.SDL_Delay(delay)

        nowtime = sdl.SDL_GetTicks()
        self._timepassed = nowtime - self._last_tick
        self._fps_count += 1
        self._last_tick = nowtime
        if not framerate:
            self._rawpassed = self._timepassed

        if not self._fps_tick:
            self._fps_count = 0
            self._fps_tick = nowtime
        elif self._fps_count >= 10:
            try:
                self._fps = (self._fps_count /
                            ((nowtime - self._fps_tick) / 1000.0))
            except ZeroDivisionError:
                self._fps = float('inf')
            self._fps_count = 0
            self._fps_tick = nowtime

        return self._timepassed

    def tick(self, framerate=0):
        """ tick(framerate=0) -> milliseconds
        update the clock
        """
        return self._base(framerate)

    def get_fps(self):
        """ get_fps() -> float
        compute the clock framerate
        """
        return self._fps

    def get_time(self):
        """ get_time() -> milliseconds
        time used in the previous tick
        """
        return self._timepassed

    def get_rawtime(self):
        """ get_rawtime() -> milliseconds
        actual time used in the previous tick
        """
        return self._rawpassed

    def tick_busy_loop(self, framerate=0):
        """ tick_busy_loop(framerate=0) -> milliseconds
        update the clock
        """
        return self._base(framerate, True)


def get_ticks():
    """ get_ticks() -> milliseconds
    get the time in milliseconds
    """
    if not _get_init():
        return 0
    return sdl.SDL_GetTicks()


_event_timers = {}


@ffi.callback("SDL_NewTimerCallback")
def _timer_callback(interval, param):
    if sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO):
        event = ffi.new("SDL_Event")
        event.type = ffi.cast("intptr_t", param)
        sdl.SDL_PushEvent(event)
    return interval


def set_timer(eventid, milliseconds):
    """set_timer(eventid, milliseconds) -> None
    repeatedly create an event on the event queue"
    """
    if eventid <= sdl.SDL_NOEVENT or eventid >= sdl.SDL_NUMEVENTS:
        raise ValueError("Event id must be between NOEVENT(0) and"
                         " NUMEVENTS(32)")

    old_event = _event_timers.pop(eventid, None)
    if old_event:
        sdl.SDL_RemoveTimer(old_event)

    if milliseconds <= 0:
        return

    _try_init()

    handle = ffi.cast("void *", eventid)
    newtimer = sdl.SDL_AddTimer(milliseconds, _timer_callback, handle)
    if not newtimer:
        SDLError.from_sdl_error()

    _event_timers[eventid] = newtimer


def wait(milliseconds):
    """ wait(milliseconds) -> time
    pause the program for an amount of time
    """
    try:
        milliseconds = int(milliseconds)
    except (ValueError, TypeError):
        raise TypeError("wait requires one integer argument")

    _try_init()

    milliseconds = max(milliseconds, 0)

    start = sdl.SDL_GetTicks()
    sdl.SDL_Delay(milliseconds)
    return sdl.SDL_GetTicks() - start


def _accurate_delay(ticks):
    if ticks <= 0:
        return 0

    start = sdl.SDL_GetTicks()
    if ticks >= WORST_CLOCK_ACCURACY:
        delay = (ticks - 2) - (ticks % WORST_CLOCK_ACCURACY)
        if delay >= WORST_CLOCK_ACCURACY:
            sdl.SDL_Delay(delay)

    # hog CPU for a bit to get the delay just right
    delay = ticks - (sdl.SDL_GetTicks() - start)
    while delay > 0:
        delay = ticks - (sdl.SDL_GetTicks() - start)

    return sdl.SDL_GetTicks() - start


def delay(milliseconds):
    """ delay(milliseconds) -> time
    pause the program for an amount of time
    """
    try:
        milliseconds = int(milliseconds)
    except (ValueError, TypeError):
        raise TypeError("delay requires one integer argument")

    _try_init()

    # don't check for negative milliseconds since _accurate_delay does that
    return _accurate_delay(milliseconds)
