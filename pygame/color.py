
from pygame._sdl import sdl

class Color(object):
    def __init__(self, *args):
        if len(args) == 4:
            r, g, b, a = args
        elif len(args) == 3:
            r, g, b = args
            a = 255
        else:
            raise NotImplementedError("implement me")
        self.r = r
        self.g = g
        self.b = b
        self.a = a


def _check_range(val):
    if not 0 <= val <= 255:
        raise ValueError("Color should be between 0 and 255")
    return val

def create_color(color, color_format):
    if isinstance(color, int):
        return color
    if isinstance(color, Color):
        return sdl.SDL_MapRGBA(color_format, color.r, color.g, color.b,
                               color.a)
    if isinstance(color, tuple) and len(color) == 1:
        return create_color(color[0], color_format)
    if hasattr(color, '__iter__') and 3 <= len(color) <= 4:
        if len(color) == 3:
            a = 255
        else:
            a = _check_range(color[3])
        return sdl.SDL_MapRGBA(color_format, _check_range(color[0]),
                               _check_range(color[1]),
                               _check_range(color[2]), a)
    raise ValueError("Unrecognised color format %s" % (color, ))
