"""
Module for the rectangle object
"""

from pygame._sdl import ffi


class Rect(object):

    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], Rect):
            # Copy the rect parameters
            self._sdlrect = args[0]._sdlrect
        elif len(args) == 4:
            self._sdlrect = new_rect(*args)
        elif len(args) == 2:
            if not isinstance(args[0], tuple) or len(args[0]) != 2:
                raise TypeError("Argument must be rect style object")
            if not isinstance(args[1], tuple) or len(args[1]) != 2:
                raise TypeError("Argument must be rect style object")
            self._sdlrect = new_rect(args[0][0], args[0][1],
                                     args[1][0], args[1][1])

    def move(self, (x, y)):
        return Rect(self._sdlrect.x + x, self._sdlrect.y + y,
                    self._sdlrect.w, self._sdlrect.h)

    def move_ip(self, x, y):
        self._sdlrect.x += x
        self._sdlrect.y += y

    def get_x(self):
        return self._sdlrect.x
    def set_x(self, new_x):
        self._sdlrect.x = new_x
    x = property(get_x, set_x)

    def get_y(self):
        return self._sdlrect.y
    def set_y(self, new_y):
        self._sdlrect.y = new_y
    y = property(get_y, set_y)

    def get_w(self):
        return self._sdlrect.x + self._sdlrect.w
    w = property(get_w)

    def get_h(self):
        return self._sdlrect.y + self._sdlrect.h
    h = property(get_h)

    def get_left(self):
        return self._sdlrect.x
    left = property(get_left)

    def get_right(self):
        return self._sdlrect.x + self._sdlrect.w
    right = property(get_right)

    def get_top(self):
        return self._sdlrect.y
    top = property(get_top)

    def get_bottom(self):
        return self._sdlrect.y + self._sdlrect.y
    bottom = property(get_bottom)

    def get_topleft(self):
        return (self._sdlrect.x, self._sdlrect.y)

    def set_topleft(self, (x, y)):
        self._sdlrect.x = x
        self._sdlrect.y = y
    topleft = property(get_topleft, set_topleft)

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

    def colliderect(self, other):
        other = rect_from_obj(other)
        return do_rects_intersect(self._sdlrect, other)

    def inflate(self, x, y):
        return Rect(self.x - x // 2, self.y - y // 2,
                    self.w + x, self.h + y)
        

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
