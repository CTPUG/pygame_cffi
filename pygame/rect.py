"""
Module for the rectangle object
"""

from pygame._sdl import ffi


class Rect(object):

    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], Rect):
            # Copy the rect parameters
            self._sdlrect = new_rect(args[0]._sdlrect.x,
                                     args[0]._sdlrect.y,
                                     args[0]._sdlrect.w,
                                     args[0]._sdlrect.h)
        elif len(args) == 1 and hasattr(args[0], '__iter__'):
            if len(args[0]) == 4:
                self._sdlrect = new_rect(args[0][0], args[0][1],
                                         args[0][2], args[0][3])
            elif len(args[0]) == 2:
                # Try recurse
                r = Rect(args[0][0], args[0][1])
                self._sdlrect = r._sdlrect
        elif len(args) == 4:
            self._sdlrect = new_rect(*args)
        elif len(args) == 2:
            if not hasattr(args[0], '__iter__') or len(args[0]) != 2:
                raise TypeError("Argument must be rect style object")
            if not hasattr(args[1], '__iter__') or len(args[1]) != 2:
                raise TypeError("Argument must be rect style object")
            self._sdlrect = new_rect(args[0][0], args[0][1],
                                     args[1][0], args[1][1])

    def __eq__(self, other):
        if isinstance(other, Rect):
            return ((self._sdlrect.x == other._sdlrect.x)
                    and (self._sdlrect.y == other._sdlrect.y)
                    and (self._sdlrect.w == other._sdlrect.w)
                    and (self._sdlrect.h == other._sdlrect.h))
        elif hasattr(other, '__iter__'):
            try:
                other_r = Rect(other)
                return self == other_r
            except TypeError:
                # Doesn't seem to be rect-like, so NotImplemented
                return NotImplemented
        return NotImplemented

    def __len__(self):
        return 4

    def __getitem__(self, index):
        data = [self._sdlrect.x, self._sdlrect.y,
                self._sdlrect.w, self._sdlrect.h]
        if isinstance(index, slice):
            if index.step is not None:
                raise TypeError("slice steps not supported")
            start = index.start if index.start is not None else 0
            stop = index.stop if index.stop is not None else 4
            return data[start:stop]
        return data[index]

    def move(self, (x, y)):
        return Rect(self._sdlrect.x + x, self._sdlrect.y + y,
                    self._sdlrect.w, self._sdlrect.h)

    def move_ip(self, x, y):
        self._sdlrect.x += x
        self._sdlrect.y += y

    def copy(self):
        return Rect(self)

    def get_x(self):
        return self._sdlrect.x
    def set_x(self, new_x):
        self._sdlrect.x = new_x
    x = property(get_x, set_x)
    left = property(get_x, set_x)

    def get_y(self):
        return self._sdlrect.y
    def set_y(self, new_y):
        self._sdlrect.y = new_y
    y = property(get_y, set_y)
    top = property(get_y, set_y)

    def get_w(self):
        return self._sdlrect.w
    def set_w(self, new_w):
        self._sdlrect.w = new_w
    w = property(get_w, set_w)
    width = property(get_w, set_w)

    def get_h(self):
        return self._sdlrect.h
    def set_h(self, new_h):
        self._sdlrect.h = new_h
    h = property(get_h, set_h)
    height = property(get_h, set_h)

    def get_right(self):
        return self._sdlrect.x + self._sdlrect.w
    def set_right(self, r):
        self._sdlrect.x = r - self._sdlrect.w
    right = property(get_right, set_right)

    def get_bottom(self):
        return self._sdlrect.y + self._sdlrect.h
    def set_bottom(self, b):
        self._sdlrect.y = b - self._sdlrect.h
    bottom = property(get_bottom, set_bottom)

    def get_topleft(self):
        return (self._sdlrect.x, self._sdlrect.y)
    def set_topleft(self, (x, y)):
        self._sdlrect.x = x
        self._sdlrect.y = y
    topleft = property(get_topleft, set_topleft)

    def get_topright(self):
        return (self._sdlrect.x + self._sdlrect.w, self._sdlrect.y)
    def set_topright(self, (x, y)):
        self._sdlrect.x = x - self._sdlrect.w
        self._sdlrect.y = y
    topright = property(get_topright, set_topright)

    def get_midleft(self):
        return (self._sdlrect.x,
                self._sdlrect.y + self._sdlrect.h // 2)
    def set_midleft(self, (x, y)):
        self._sdlrect.x = x
        self._sdlrect.y = y - self._sdlrect.h // 2
    midleft = property(get_midleft, set_midleft)

    def get_midright(self):
        return (self._sdlrect.x + self._sdlrect.w,
                self._sdlrect.y + self._sdlrect.h // 2)
    def set_midright(self, (x, y)):
        self._sdlrect.x = x - self._sdlrect.w
        self._sdlrect.y = y - self._sdlrect.h // 2
    midright = property(get_midright, set_midright)

    def get_midtop(self):
        return (self._sdlrect.x + self._sdlrect.w // 2, self._sdlrect.y)

    def set_midtop(self, (x, y)):
        self._sdlrect.x = x - self._sdlrect.w // 2
        self._sdlrect.y = y
    midtop = property(get_midtop, set_midtop)

    def get_center(self):
        return (self._sdlrect.x + self._sdlrect.w // 2,
                self._sdlrect.y + self._sdlrect.h // 2)

    def set_center(self, (x, y)):
        self._sdlrect.x = x - self._sdlrect.w // 2
        self._sdlrect.y = y - self._sdlrect.h // 2
    center = property(get_center, set_center)

    def get_centerx(self):
        return self._sdlrect.x + self._sdlrect.w // 2
    def set_centerx(self, x):
        self._sdlrect.x = x - self._sdlrect.w // 2
    centerx = property(get_centerx, set_centerx)

    def get_centery(self):
        return self._sdlrect.y + self._sdlrect.h // 2
    def set_centery(self, y):
        self._sdlrect.y = y - self._sdlrect.h // 2
    centery = property(get_centery, set_centery)

    def get_bottomleft(self):
        return (self._sdlrect.x,
                self._sdlrect.y + self._sdlrect.h)
    def set_bottomleft(self, (x, y)):
        self._sdlrect.x = x
        self._sdlrect.y = y - self._sdlrect.h
    bottomleft = property(get_bottomleft, set_bottomleft)

    def get_midbottom(self):
        return (self._sdlrect.x + self._sdlrect.w // 2,
                self._sdlrect.y + self._sdlrect.h)
    def set_midbottom(self, (x, y)):
        self._sdlrect.x = x - self._sdlrect.w // 2
        self._sdlrect.y = y - self._sdlrect.h
    midbottom = property(get_midbottom, set_midbottom)

    def get_bottomright(self):
        return (self._sdlrect.x + self._sdlrect.w,
                self._sdlrect.y + self._sdlrect.h)
    def set_bottomright(self, (x, y)):
        self._sdlrect.x = x - self._sdlrect.w
        self._sdlrect.y = y - self._sdlrect.h
    bottomright = property(get_bottomright, set_bottomright)

    def get_size(self):
        return (self._sdlrect.w, self._sdlrect.h)
    def set_size(self, (w, h)):
        self._sdlrect.w = w
        self._sdlrect.h = h
    size = property(get_size, set_size)

    def colliderect(self, other):
        other = rect_from_obj(other)
        return do_rects_intersect(self._sdlrect, other)

    def inflate(self, x, y):
        return Rect(self.x - x // 2, self.y - y // 2,
                    self.w + x, self.h + y)

    def inflate_ip(self, x, y):
        self._sdlrect.x -= x // 2
        self._sdlrect.y -= y // 2
        self._sdlrect.w += x
        self._sdlrect.h += y

    def _calc_clamp(self, *args):
        other = Rect(*args)
        if self._sdlrect.w >= other._sdlrect.w:
            x = other._sdlrect.x + other._sdlrect.w // 2 - self._sdlrect.w // 2
        elif self._sdlrect.x < other._sdlrect.x:
            x = other._sdlrect.x
        elif (self._sdlrect.x + self._sdlrect.w >
                other._sdlrect.x + other._sdlrect.w):
            x = other._sdlrect.x + other._sdlrect.w - self._sdlrect.w
        else:
            x = self._sdlrect.x

        if self._sdlrect.h >= other._sdlrect.h:
            y = other._sdlrect.y + other._sdlrect.h / 2 - self._sdlrect.h / 2
        elif self._sdlrect.y < other._sdlrect.y:
            y = other._sdlrect.y
        elif (self._sdlrect.y + self._sdlrect.h >
                other._sdlrect.y + other._sdlrect.h):
            y = other._sdlrect.y + other._sdlrect.h - self._sdlrect.h
        else:
            y = self._sdlrect.y

        return x, y

    def clamp(self, *args):
        x, y = self._calc_clamp(*args)
        return Rect(x, y, self._sdlrect.w, self._sdlrect.h)

    def clamp_ip(self, *args):
        x, y = self._calc_clamp(*args)
        self._sdlrect.x = x
        self._sdlrect.y = y

    def clip(self, *args):
        """Rect.clip(Rect): return Rect
           crops a rectangle inside another"""
        other = Rect(*args)

        if ((self._sdlrect.x >= other._sdlrect.x) and
                (self._sdlrect.x < (other._sdlrect.x + other._sdlrect.w))):
            x = self._sdlrect.x
        elif ((other._sdlrect.x >= self._sdlrect.x) and
                (other._sdlrect.x < (self._sdlrect.x + self._sdlrect.w))):
            x = other._sdlrect.x
        else:
            # no intersect
            return Rect(self._sdlrect.x, self._sdlrect.y, 0, 0)

        if (((self._sdlrect.x + self._sdlrect.w) > other._sdlrect.x) and
            ((self._sdlrect.x + self._sdlrect.w) <=
             (other._sdlrect.x + other._sdlrect.w))):
            w = (self._sdlrect.x + self._sdlrect.w) - x
        elif (((other._sdlrect.x + other._sdlrect.w) > self._sdlrect.x) and
              ((other._sdlrect.x + other._sdlrect.w) <=
                  (self._sdlrect.x + self._sdlrect.w))):
            w = (other._sdlrect.x + other._sdlrect.w) - x
        else:
            # no intersect
            return Rect(self._sdlrect.x, self._sdlrect.y, 0, 0)

        if ((self._sdlrect.y >= other._sdlrect.y) and (
                self._sdlrect.y < (other._sdlrect.y + other._sdlrect.h))):
            y = self._sdlrect.y
        elif ((other._sdlrect.y >= self._sdlrect.y) and
              (other._sdlrect.y < (self._sdlrect.y + self._sdlrect.h))):
            y = other._sdlrect.y
        else:
            # no intersect
            return Rect(self._sdlrect.x, self._sdlrect.y, 0, 0)

        if (((self._sdlrect.y + self._sdlrect.h) > other._sdlrect.y) and
                ((self._sdlrect.y + self._sdlrect.h) <=
                 (other._sdlrect.y + other._sdlrect.h))):
            h = (self._sdlrect.y + self._sdlrect.h) - y
        elif (((other._sdlrect.y + other._sdlrect.h) > self._sdlrect.y) and
              ((other._sdlrect.y + other._sdlrect.h) <=
                  (self._sdlrect.y + self._sdlrect.h))):
            h = (other._sdlrect.y + other._sdlrect.h) - y
        else:
            # no intersect
            return Rect(self._sdlrect.x, self._sdlrect.y, 0, 0)

        return Rect(x, y, w, h)

    def fit(self, *args):
        """Rect.fit(Rect): return Rect
           resize and move a rectangle with aspect ratio"""
        other = Rect(*args)
        xratio = float(self._sdlrect.w) / float(other._sdlrect.w)
        yratio = float(self._sdlrect.h) / float(other._sdlrect.h)
        maxratio = xratio if xratio > yratio else yratio

        w = int(self._sdlrect.w / maxratio)
        h = int(self._sdlrect.h / maxratio)

        x = other._sdlrect.x + (other._sdlrect.w - w) // 2
        y = other._sdlrect.y + (other._sdlrect.h - h) // 2

        return Rect(x, y, w, h)

    def contains(self, *args):
        other = Rect(*args)
        return (self._sdlrect.x <= other._sdlrect.x and
                self._sdlrect.y <= other._sdlrect.y and
                self._sdlrect.x + self._sdlrect.w >= other._sdlrect.x + other._sdlrect.w and
                self._sdlrect.y + self._sdlrect.h >= other._sdlrect.y + other._sdlrect.h and
                self._sdlrect.x + self._sdlrect.w > other._sdlrect.x and
                self._sdlrect.y + self._sdlrect.h > other._sdlrect.y)

    def union(self, *args):
        other = Rect(*args)
        x = min(self._sdlrect.x, other._sdlrect.x)
        y = min(self._sdlrect.y, other._sdlrect.y)
        w = max(self._sdlrect.x + self._sdlrect.w,
                other._sdlrect.x + other._sdlrect.w) - x
        h = max(self._sdlrect.y + self._sdlrect.h,
                other._sdlrect.y + other._sdlrect.h) - y
        return Rect(x, y, w, h)

    def collidepoint(self, (x, y)):
        # FIXME: Handle the non-tuple calling cases
        return (self._sdlrect.x <= x <= self._sdlrect.x + self._sdlrect.w and
                self._sdlrect.y <= y <= self._sdlrect.y + self._sdlrect.h)

    def colliderect(self, *args):
        other = Rect(*args)
        return do_rects_intersect(self, other)


def do_rects_intersect(A, B):
    return (((A.x >= B.x and A.x < B.x + B.w) or
             (B.x >= A.x and B.x < A.x + A.w)) and
             ((A.y >= B.y and A.y < B.y + B.h) or
             (B.y >= A.y and B.y < A.y + A.h)))


def rect_from_obj(obj):
    if isinstance(obj, Rect):
        return obj._sdlrect
    if hasattr(obj, '__iter__') and len(obj) == 4:
        return new_rect(*obj)
    raise NotImplementedError


def new_rect(x, y, w, h):
    sdlrect = ffi.new('SDL_Rect*')
    sdlrect.x = x
    sdlrect.y = y
    sdlrect.w = w
    sdlrect.h = h
    return sdlrect
