import string

from pygame._sdl import sdl
import pygame.colordict


class Color(object):
    def __init__(self, *args):
        if not args:
            raise TypeError("function takes at least 1 argument (0 given)")
        elif len(args) > 4:
            raise TypeError("function takes at most 4 arguments (6 given)")

        if isinstance(args[0], basestring):
            if len(args) > 1:
                raise ValueError("invalid arguments")
            r, g, b, a = self._parse_string_color(args[0])

        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, int):
                r = (arg >> 24) & 0xff
                g = (arg >> 16) & 0xff
                b = (arg >> 8) & 0xff
                a = arg & 0xff
            elif isinstance(arg, tuple):
                if len(arg) == 4:
                    r, g, b, a = arg
                elif len(arg) == 3:
                    r, g, b = arg
                    a = 255
                else:
                    raise ValueError("expected a tuple of length 3 or 4")

        elif len(args) == 4:
            r, g, b, a = args
        elif len(args) == 3:
            r, g, b = args
            a = 255
        else:
            ValueError("invalid color argument")

        self._data = [0, 0, 0, 0]
        self._len = 4
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def _parse_string_color(self, name):
        name = name.replace(" ", "").lower()

        # Named colors
        rgba = pygame.colordict.THECOLORS.get(name)
        if rgba is not None:
            return rgba

        # Hex color strings
        if name.startswith('#'):
            name = name[1:]
        elif name.startswith('0x'):
            name = name[2:]
        else:
            raise ValueError("invalid color name")

        if len(name) == 6:
            name += 'ff'  # Add default alpha value.
        if len(name) != 8 or len(name.strip(string.hexdigits)) != 0:
            raise ValueError("invalid color name")

        return (
            int(name[0:2], 16),
            int(name[2:4], 16),
            int(name[4:6], 16),
            int(name[6:8], 16),
        )

    @property
    def r(self):
        return self._data[0]

    @r.setter
    def r(self, value):
        self[0] = value

    @property
    def g(self):
        return self._data[1]

    @g.setter
    def g(self, value):
        self[1] = value

    @property
    def b(self):
        return self._data[2]

    @b.setter
    def b(self, value):
        self[2] = value

    @property
    def a(self):
        return self._data[3]

    @a.setter
    def a(self, value):
        self[3] = value

    def __repr__(self):
        return repr(tuple(self._data))

    def __eq__(self, other):
        if isinstance(other, Color):
            other = tuple(other._data)
        if isinstance(other, tuple):
            return tuple(self._data) == other
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Color):
            other = tuple(other._data)
        if isinstance(other, tuple):
            return tuple(self._data) != other
        return NotImplemented

    def __int__(self):
        return sum((
            self.r << 24,
            self.g << 16,
            self.b << 8,
            self.a))

    def __long__(self):
        return self.__int__()

    def __float__(self):
        return float(int(self))

    def __hex__(self):
        return hex(int(self))

    def __oct__(self):
        return oct(int(self))

    def __len__(self):
        return self._len

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.step is not None:
                raise TypeError("slice steps not supported")
            start = index.start if index.start is not None else 0
            stop = index.stop if index.stop is not None else 4
            return tuple(self._data[start:stop])
        return self._data[:self._len][index]

    def __setitem__(self, index, value):
        if not isinstance(value, int):
            raise ValueError("invalid color argument")
        if not 0 <= index <= 3:
            raise IndexError("invalid index")
        if not 0 <= value <= 255:
            raise ValueError("color exceeds allowed range")
        self._data[index] = value

    def __add__(self, other):
        if not isinstance(other, Color):
            return NotImplemented
        return Color(*[min(255, self[i] + other[i]) for i in range(4)])

    def __sub__(self, other):
        if not isinstance(other, Color):
            return NotImplemented
        return Color(*[max(0, self[i] - other[i]) for i in range(4)])

    def __mul__(self, other):
        if not isinstance(other, Color):
            return NotImplemented
        return Color(*[min(255, self[i] * other[i]) for i in range(4)])

    def __floordiv__(self, other):
        if not isinstance(other, Color):
            return NotImplemented
        return Color(*[self[i] / other[i] if other[i] else 0
                       for i in range(4)])

    def __div__(self, other):
        return self.__floordiv__(other)

    def __mod__(self, other):
        if not isinstance(other, Color):
            return NotImplemented
        return Color(*[self[i] % other[i] for i in range(4)])

    def __mod__(self, other):
        if not isinstance(other, Color):
            return NotImplemented
        return Color(*[self[i] % other[i] for i in range(4)])

    def __invert__(self):
        if not isinstance(other, Color):
            return NotImplemented
        return Color(*[255 - self[i] for i in range(4)])

    def normalize(self):
        return (self.r / 255.0, self.g / 255.0, self.b / 255.0, self.a / 255.0)

    def correct_gamma(self, gamma):
        raise NotImplementedError("implement me")

    def set_length(self, length):
        if length not in (1, 2, 3, 4):
            raise ValueError("Length needs to be 1,2,3, or 4.")
        self._len = length


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
