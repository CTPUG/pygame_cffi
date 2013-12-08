""" The pygame event module """

from pygame._sdl import sdl, ffi

from pygame.constants import (
    ACTIVEEVENT, KEYDOWN, KEYUP, MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP,
    JOYAXISMOTION, JOYBALLMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP,
    QUIT, SYSWMEVENT, VIDEORESIZE, VIDEOEXPOSE, USEREVENT, NUMEVENTS, NOEVENT)


_USEROBJECT_CHECK1 = 0xDEADBEEF
_USEROBJECT_CHECK2 = 0xFEEDF00D


def _button_state(state, button):
    if state & sdl._pygame_SDL_BUTTON(button):
        return 1
    return 0


class Event(object):
    """An event object"""

    def __init__(self, sdlevent):
        self._sdlevent = sdlevent
        if not sdlevent:
            self.type = sdl.SDL_NOEVENT
            return
        self.type = self._sdlevent.type

        if (sdlevent.user.code == _USEROBJECT_CHECK1 and
                sdlevent.user.data1 == ffi.cast('void *', _USEROBJECT_CHECK2)):
            raise NotImplementedError("TODO: User-posted events.")

        if self.type == ACTIVEEVENT:
            self.gain = sdlevent.active.gain
            self.state = sdlevent.active.state

        elif self.type == KEYDOWN:
            self.unicode = sdlevent.key.keysym.unicode
            self.key = sdlevent.key.keysym.sym
            self.mod = sdlevent.key.keysym.mod
            self.scancode = sdlevent.key.keysym.scancode
        elif self.type == KEYUP:
            self.key = sdlevent.key.keysym.sym
            self.mod = sdlevent.key.keysym.mod
            self.scancode = sdlevent.key.keysym.scancode

        elif self.type == MOUSEMOTION:
            self.pos = (sdlevent.motion.x, sdlevent.motion.y)
            self.rel = (sdlevent.motion.xrel, sdlevent.motion.yrel)
            self.buttons = (_button_state(sdlevent.motion.state, 1),
                            _button_state(sdlevent.motion.state, 2),
                            _button_state(sdlevent.motion.state, 3))
        elif self.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
            self.pos = (sdlevent.button.x, sdlevent.button.y)
            self.button = sdlevent.button.button

        elif self.type == JOYAXISMOTION:
            self.joy = sdlevent.jaxis.which
            self.axis = sdlevent.jaxis.axis
            self.value = sdlevent.jaxis.value / 32767.0
        elif self.type == JOYBALLMOTION:
            self.joy = sdlevent.jball.which
            self.ball = sdlevent.jball.ball
            self.rel = (sdlevent.jball.xrel, sdlevent.jball.yrel)
        elif self.type == JOYHATMOTION:
            self.joy = sdlevent.jhat.which
            self.hat = sdlevent.jhat.hat
            hx = hy = 0
            if sdlevent.jhat.value & sdl.SDL_HAT_UP:
                hy = 1
            elif sdlevent.jhat.value & sdl.SDL_HAT_DOWN:
                hy = -1
            if sdlevent.jhat.value & sdl.SDL_HAT_RIGHT:
                hx = 1
            elif sdlevent.jhat.value & sdl.SDL_HAT_LEFT:
                hx = -1
            self.value = (hx, hy)
        elif self.type in (JOYBUTTONUP, JOYBUTTONDOWN):
            self.joy = sdlevent.jbutton.which
            self.button = sdlevent.jbutton.button

        elif self.type == VIDEORESIZE:
            self.size = (sdlevent.resize.w, sdlevent.resize.h)
            self.w = sdlevent.resize.w
            self.h = sdlevent.resize.h

        elif self.type == SYSWMEVENT:
            print "SYSWMEVENT not properly supported yet."
            pass

        elif self.type in (VIDEOEXPOSE, QUIT):
            pass  # No attributes here.

        elif USEREVENT <= self.type < NUMEVENTS:
            self.code = sdlevent.user.code
            if self.type == USEREVENT and sdlevent.user.code == 0x1000:
                print "USEREVENT with code 0x1000 not properly supported yet."
                # insobj (dict, "filename", Text_FromUTF8 (event->user.data1));
                # free(event->user.data1);
                # event->user.data1 = NULL;


def event_name(event_type):
    name = {
        ACTIVEEVENT: "ActiveEvent",
        KEYDOWN: "KeyDown",
        KEYUP: "KeyUp",
        MOUSEMOTION: "MouseMotion",
        MOUSEBUTTONDOWN: "MouseButtonDown",
        MOUSEBUTTONUP: "MouseButtonUp",
        JOYAXISMOTION: "JoyAxisMotion",
        JOYBALLMOTION: "JoyBallMotion",
        JOYHATMOTION: "JoyHatMotion",
        JOYBUTTONUP: "JoyButtonUp",
        JOYBUTTONDOWN: "JoyButtonDown",
        QUIT: "Quit",
        SYSWMEVENT: "SysWMEvent",
        VIDEORESIZE: "VideoResize",
        VIDEOEXPOSE: "VideoExpose",
        NOEVENT: "NoEvent",
    }.get(event_type)
    if name is None:
        if USEREVENT <= event_type < NUMEVENTS:
            name = "UserEvent"
        else:
            name = "Unknown"
    return name


def get(event_filter=None):
    if event_filter is None:
        # unfiltered list of events
        mask = sdl.SDL_ALLEVENTS
    else:
        raise RuntimeError("Implement me")
    sdl.SDL_PumpEvents()
    event_list = []
    event = ffi.new("SDL_Event *")
    while sdl.SDL_PeepEvents(event, 1, sdl.SDL_GETEVENT, mask) == 1:
        event_list.append(Event(event))
    return event_list


def poll():
    event = ffi.new("SDL_Event[1]")
    if sdl.SDL_PollEvent(event):
        return Event(event[0])
    return Event(None)


def clear(event_filter=None):
    if event_filter is None:
        # unfiltered list of events
        mask = sdl.SDL_ALLEVENTS
    else:
        raise NotImplementedError("Implement me")
    sdl.SDL_PumpEvents()
    event = ffi.new("SDL_Event *")
    while sdl.SDL_PeepEvents(event, 1, sdl.SDL_GETEVENT, mask) == 1:
        pass


def set_grab(value):
    if value:
        sdl.SDL_WM_GrabInput(sdl.SDL_GRAB_ON)
    else:
        sdl.SDL_WM_GrabInput(sdl.SDL_GRAB_OFF)


def get_grab():
    mode = sdl.SDL_WM_GrabInput(sdl.SDL_GRAB_QUERY)
    return mode == sdl.SDL_GRAB_ON


def _event_types_iter(event_types):
    if isinstance(event_types, int):
        if not 0 <= event_types < NUMEVENTS:
            raise ValueError("Invalid event")
        event_types = [event_types]

    try:
        iterator = iter(event_types)
    except TypeError:
        raise TypeError("type must be numeric or a sequence")

    for event_type in iterator:
        if not isinstance(event_type, int):
            raise TypeError("type sequence must contain valid event types")
        if not 0 <= event_type < NUMEVENTS:
            raise ValueError("Invalid event in sequence")
        yield event_type


def set_allowed(event_types):
    if event_types is None:
        sdl.SDL_EventState(0xff, sdl.SDL_IGNORE)
        return

    for event_type in _event_types_iter(event_types):
        sdl.SDL_EventState(event_type, sdl.SDL_ENABLE)


def set_blocked(event_types):
    if event_types is None:
        sdl.SDL_EventState(0xff, sdl.SDL_IGNORE)
        return

    for event_type in _event_types_iter(event_types):
        sdl.SDL_EventState(event_type, sdl.SDL_IGNORE)


def get_blocked(event_types):
    is_blocked = False

    for event_type in _event_types_iter(event_types):
        # TODO: Is it safe to short-circuit here? The implementation in
        # pygame's event.c doesn't.
        if sdl.SDL_EventState(event_type, sdl.SDL_QUERY) == sdl.SDL_IGNORE:
            is_blocked = True

    return is_blocked


def pump():
    sdl.SDL_PumpEvents()
