import string

from pygame._sdl import ffi, sdl
import pygame.colordict


class Color(object):
    def __init__(self, *args):
        if not args:
            raise TypeError("function takes at least 1 argument (0 given)")
        elif len(args) > 4:
            raise TypeError("function takes at most 4 arguments (%s given)" % (
                len(args),))

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
            elif isinstance(arg, (tuple, list)):
                if len(arg) == 4:
                    r, g, b, a = arg
                elif len(arg) == 3:
                    r, g, b = arg
                    a = 255
                else:
                    raise ValueError("expected a tuple of length 3 or 4")
            elif isinstance(arg, Color):
                r, g, b, a = arg[:]
            else:
                ValueError("invalid color argument")

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

    @property
    def hsva(self):
        r, g, b, a = self.normalize()

        maxv = max(r, g, b)
        minv = min(r, g, b)
        diff = maxv - minv

        v = maxv * 100

        if (maxv == minv):
            h = s = 0.0
        else:
            s = 100 * diff / maxv
            if maxv == r:
                h = (60 * (g - b) / diff) % 360.0
            elif maxv == g:
                h = (60 * (b - r) / diff) + 120.0
            else:
                h = (60 * (r - g) / diff) + 240.0
            if h < 0:
                h += 360.0

        return (h, s, v, a * 100)

    @hsva.setter
    def hsva(self, value):
        h = _float_from_seq(value, 0, 'HSVA', (0, 360))
        s = _float_from_seq(value, 1, 'HSVA', (0, 100)) / 100
        v = _float_from_seq(value, 2, 'HSVA', (0, 100)) / 100
        a = 0  # This is the default value in pygame 1.9.x, probably a bug.
        if len(value) >= 4:
            a = _float_from_seq(value, 3, 'HSVA', (0, 100)) / 100
            a = int(a * 255)

        hi = int(h / 60)
        f = (h / 60) - hi
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))

        if hi == 0:
            r = int(v * 255)
            g = int(t * 255)
            b = int(p * 255)
        elif hi == 1:
            r = int(q * 255)
            g = int(v * 255)
            b = int(p * 255)
        elif hi == 2:
            r = int(p * 255)
            g = int(v * 255)
            b = int(t * 255)
        elif hi == 3:
            r = int(p * 255)
            g = int(q * 255)
            b = int(v * 255)
        elif hi == 4:
            r = int(t * 255)
            g = int(p * 255)
            b = int(v * 255)
        elif hi == 5:
            r = int(v * 255)
            g = int(p * 255)
            b = int(q * 255)
        else:
            raise OverflowError("this is not allowed to happen ever")

        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @property
    def hsla(self):
        r, g, b, a = self.normalize()

        maxv = max(r, g, b)
        minv = min(r, g, b)
        diff = maxv - minv

        l = (maxv + minv) * 50

        if (maxv == minv):
            h = s = 0.0
        else:
            if l <= 50:
                s = diff / (maxv + minv)
            else:
                s = diff / (2 - maxv - minv)
            s *= 100

            if maxv == r:
                h = (60 * (g - b) / diff) % 360.0
            elif maxv == g:
                h = (60 * (b - r) / diff) + 120.0
            else:
                h = (60 * (r - g) / diff) + 240.0
            if h < 0:
                h += 360.0

        return (h, s, l, a * 100)

    def _calc_rgb_val_for_hsla(self, p, q, h):
        if h < 0:
            h += 1
        elif h > 1:
            h -= 1

        if h < (1.0 / 6.0):
            return int((p + ((q - p) * 6 * h)) * 255)
        if h < 0.5:
            return int(q * 255)
        if h < (2.0 / 3.0):
            return int((p + ((q - p) * 6 * ((2.0 / 3.0) - h))) * 255)
        else:
            return int(p * 255)

    @hsla.setter
    def hsla(self, value):
        h = _float_from_seq(value, 0, 'HSLA', (0, 360))
        s = _float_from_seq(value, 1, 'HSLA', (0, 100)) / 100
        l = _float_from_seq(value, 2, 'HSLA', (0, 100)) / 100
        a = 0  # This is the default value in pygame 1.9.x, probably a bug.
        if len(value) >= 4:
            a = _float_from_seq(value, 3, 'HSLA', (0, 100)) / 100
            a = int(a * 255)

        if s == 0:
            r = g = b = int(l * 255)

        else:
            if l < 0.5:
                q = l * (1 + s)
            else:
                q = l + s - (l * s)
            p = 2 * l - q

            ht = h / 360.0
            r = self._calc_rgb_val_for_hsla(p, q, ht + (1.0 / 3.0))
            g = self._calc_rgb_val_for_hsla(p, q, ht)
            b = self._calc_rgb_val_for_hsla(p, q, ht - (1.0 / 3.0))

        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @property
    def i1i2i3(self):
        r, g, b, _ = self.normalize()
        return (
            (r + g + b) / 3.0,
            (r - b) / 2.0,
            (2 * g - r - b) / 4.0,
        )

    @i1i2i3.setter
    def i1i2i3(self, value):
        i1 = _float_from_seq(value, 0, 'I1I2I3', (0, 1))
        i2 = _float_from_seq(value, 1, 'I1I2I3', (-0.5, 0.5))
        i3 = _float_from_seq(value, 2, 'I1I2I3', (-0.5, 0.5))

        b = i1 - i2 - 2 * i3 / 3.0
        r = 2 * i2 + b
        g = 3 * i1 - r - b

        self.r = int(r * 255)
        self.g = int(g * 255)
        self.b = int(b * 255)

    @property
    def cmy(self):
        r, g, b, _ = self.normalize()
        return (1.0 - r, 1.0 - g, 1.0 - b)

    @cmy.setter
    def cmy(self, value):
        c = _float_from_seq(value, 0, 'CMY', (0, 1))
        m = _float_from_seq(value, 1, 'CMY', (0, 1))
        y = _float_from_seq(value, 2, 'CMY', (0, 1))

        self.r = int((1.0 - c) * 255)
        self.g = int((1.0 - m) * 255)
        self.b = int((1.0 - y) * 255)

    def __repr__(self):
        return repr(tuple(self._data))

    def __eq__(self, other):
        if isinstance(other, tuple):
            try:
                other = Color(other)
            except:
                return NotImplemented
        if isinstance(other, Color):
            return self._data == other._data
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, tuple):
            try:
                other = Color(other)
            except:
                return NotImplemented
        if isinstance(other, Color):
            return self._data != other._data
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

    def __iter__(self):
        yield self.r
        yield self.g
        yield self.b
        yield self.a

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

    def __invert__(self):
        return Color(*[255 - self[i] for i in range(4)])

    def normalize(self):
        return (self.r / 255.0, self.g / 255.0, self.b / 255.0, self.a / 255.0)

    def _apply_gamma(self, value, gamma):
        value = (value / 255.0) ** gamma
        return max(0, min(255, int(round(value * 255))))

    def correct_gamma(self, gamma):
        return Color(*[self._apply_gamma(self[i], gamma) for i in range(4)])

    def set_length(self, length):
        if length not in (1, 2, 3, 4):
            raise ValueError("Length needs to be 1,2,3, or 4.")
        self._len = length


def _float_from_seq(seq, index, typename, bounds):
    try:
        val = float(seq[index])
        assert bounds[0] <= val <= bounds[1]
        return val
    except:
        raise ValueError("invalid %s value" % typename)


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


def uncreate_color(c_color, color_format):
    r, g, b, a = [ffi.new("uint8_t*") for _ in range(4)]
    sdl.SDL_GetRGBA(c_color, color_format, r, g, b, a)
    return Color(r[0], g[0], b[0], a[0])
