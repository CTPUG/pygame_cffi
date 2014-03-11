""" The pygame event module """

from pygame._sdl import sdl, ffi
from pygame._error import SDLError
from pygame.display import check_video

from pygame.constants import (
    ACTIVEEVENT, KEYDOWN, KEYUP, MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP,
    JOYAXISMOTION, JOYBALLMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP,
    QUIT, SYSWMEVENT, VIDEORESIZE, VIDEOEXPOSE, USEREVENT, NUMEVENTS, NOEVENT,
    USEREVENT_DROPFILE)

# We do this to avoid roundtripping issues caused by 0xDEADBEEF casting to a 
# negative number
_USEROBJECT_CHECK1 = ffi.cast('int', 0xDEADBEEF)
_USEROBJECT_CHECK2 = ffi.cast('void*', 0xFEEDF00D)

# I'm not wild about this global dict, but it's the same idea as the linked
# list pygame uses and I don't have a better approach right now
_user_events = {}


def _button_state(state, button):
    if state & sdl._pygame_SDL_BUTTON(button):
        return 1
    return 0


class EventType(object):
    """An event object"""

    def __init__(self, sdlevent, d=None, **kwargs):
        self._sdlevent = sdlevent
        if isinstance(sdlevent, int):
            # User specificed event with kwargs
            self.type = sdlevent
            # XXX: Pygame manipulates __dict__, we're currently don't
            # this causes a failure in test_Event
            if d:
                self._dict = d.copy()
            else:
                self._dict = {}
            if kwargs:
                self._dict.update(kwargs)
            for attr, value in self._dict.iteritems():
                setattr(self, attr, value)
            return
        if not sdlevent:
            self.type = sdl.SDL_NOEVENT
            return
        self.type = self._sdlevent.type

        if (sdlevent.user.code == int(_USEROBJECT_CHECK1) and
                sdlevent.user.data1 == _USEROBJECT_CHECK2):
            eventkey = ffi.cast("SDL_Event *", sdlevent.user.data2)
            if eventkey in _user_events:
                self._dict = _user_events[eventkey]._dict
                del _user_events[eventkey]
                for attr, value in self._dict.iteritems():
                    setattr(self, attr, value)
                return
            raise NotImplementedError("TODO: Error handling for user-posted events.")

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
            raise NotImplementedError("SYSWMEVENT not properly supported yet.")

        elif self.type in (VIDEOEXPOSE, QUIT):
            pass  # No attributes here.

        elif USEREVENT <= self.type < NUMEVENTS:
            self.code = sdlevent.user.code
            if self.type == USEREVENT and sdlevent.user.code == USEREVENT_DROPFILE:
                # mirrors what pygame does - not sure if correct
                self.filename = ffi.string(sdlevent.user.data1)
                sdl.free(sdlevent.user.data1)
                sdlevent.user.data1 = ffi.NULL

    def __nonzero__(self):
        return self.type != sdl.SDL_NOEVENT

    def __eq__(self, other):
        if not isinstance(other, EventType):
            return NotImplemented
        if self.type != other.type:
            return False
        if hasattr(self, '_dict'):
            if hasattr(other, '_dict'):
                return self._dict == other._dict
            return False
        # FIXME: Either add _dict for all events, or add appropriate
        # logic for all cases here
        return False

    def __ne__(self, other):
        res = self == other
        if res is NotImplemented:
            return res
        return not res


def Event(type_id, attr_dict=None, **attrs):
    """ Event(type, dict) -> EventType instance
    create a new event object
    """
    if attr_dict:
        return EventType(type_id, attr_dict)
    return EventType(type_id, attrs)


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


def event_mask(event_id):
    return 1 << event_id


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
        event_list.append(EventType(event))
    return event_list


def poll():
    event = ffi.new("SDL_Event[1]")
    if sdl.SDL_PollEvent(event):
        return EventType(event[0])
    return EventType(None)


def post(event):
    """post(Event): return None
       place a new event on the queue"""
    # SDL requires video to be initialised before PushEvent does the right thing
    check_video()
    is_blocked = sdl.SDL_EventState(event.type, sdl.SDL_QUERY) == sdl.SDL_IGNORE
    if is_blocked:
        raise RuntimeError("event post blocked for %s" % event_name(event.type))

    sdl_event = ffi.new("SDL_Event *")
    sdl_event.type = event.type
    sdl_event.user.code = _USEROBJECT_CHECK1
    sdl_event.user.data1 = _USEROBJECT_CHECK2
    sdl_event.user.data2 = ffi.cast("void*", sdl_event)
    _user_events[sdl_event] = event
    if sdl.SDL_PushEvent(sdl_event) == -1:
        raise SDLError.from_sdl_error()


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


def wait():
    """ wait() -> EventType instance
    wait for a single event from the queue
    """
    event = ffi.new('SDL_Event*')
    if not sdl.SDL_WaitEvent(event):
        raise SDLError.from_sdl_error()
    return EventType(event[0])


def peek(types=None):
    """ peek(type) -> bool
    test if event types are waiting on the queue
    """
    mask = 0
    if not types:
        mask = sdl.SDL_ALLEVENTS
    elif isinstance(types, int):
        mask |= event_mask(types) 
    elif hasattr(types, '__iter__'):
        try:
            for t in types:
                mask |= event_mask(int(t))
        except (ValueError, TypeError):
            raise TypeError("type sequence must contain valid event types")
    else:
        raise TypeError("peek type must be numeric or a sequence")

    sdl.SDL_PumpEvents()
    event = ffi.new('SDL_Event*')
    result = sdl.SDL_PeepEvents(event, 1, sdl.SDL_PEEKEVENT, mask)

    if not types:
        return EventType(event[0])
    return result == 1
