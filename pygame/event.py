""" The pygame event module """

from pygame._sdl import sdl, ffi


class Event(object):
    """An event object"""

    def __init__(self, sdlevent):
        self._sdlevent = sdlevent
        self.type = self._sdlevent.type
        # XXX: Implement this
        self.dict = {}


def get(event_filter=None):
    if event_filter is None:
        # unfiltered list of events
        mask = sdl.SDL_ALLEVENTS
    else:
        raise RuntimeError("Implement me")
    event_list = []
    event = ffi.new("SDL_Event *")
    while sdl.SDL_PeepEvents(event, 1, sdl.SDL_GETEVENT, mask) == 1:
        event_list.append(Event(event))
    return event_list
