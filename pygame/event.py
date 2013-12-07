""" The pygame event module """

from pygame._sdl import sdl, ffi

from pygame.constants import KEYDOWN, KEYUP


_USEROBJECT_CHECK1 = 0xDEADBEEF
_USEROBJECT_CHECK2 = 0xFEEDF00D


class Event(object):
    """An event object"""

    def __init__(self, sdlevent):
        self._sdlevent = sdlevent
        self.type = self._sdlevent.type

        if (sdlevent.user.code == _USEROBJECT_CHECK1 and
                sdlevent.user.data1 == ffi.cast('void *', _USEROBJECT_CHECK2)):
            raise NotImplementedError("TODO: User-posted events.")

        # TODO: SDL_ACTIVEEVENT
        if self.type == KEYDOWN:
            self.unicode = sdlevent.key.keysym.unicode
            self.key = sdlevent.key.keysym.sym
            self.mod = sdlevent.key.keysym.mod
            self.scancode = sdlevent.key.keysym.scancode
        elif self.type == KEYUP:
            self.key = sdlevent.key.keysym.sym
            self.mod = sdlevent.key.keysym.mod
            self.scancode = sdlevent.key.keysym.scancode
        else:
            raise NotImplementedError("TODO: More event types.")


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
