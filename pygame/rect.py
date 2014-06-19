"""
Module for the rectangle object
"""


class GameRect(object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class Rect(object):

    def __init__(self, *args):
        try:
            if len(args) == 1:
                if isinstance(args[0], Rect):
                    # Copy the rect parameters
                    self.r = GameRect(args[0].r.x,
                                      args[0].r.y,
                                      args[0].r.w,
                                      args[0].r.h)
                elif len(args[0]) == 4:
                    self.r = GameRect(int(args[0][0]), int(args[0][1]),
                                      int(args[0][2]), int(args[0][3]))
                elif len(args[0]) == 2:
                    # Try recurse
                    rect = Rect(args[0][0], args[0][1])
                    self.r = rect.r
            elif len(args) == 4:
                self.r = GameRect(int(args[0]), int(args[1]),
                                  int(args[2]), int(args[3]))
            elif len(args) == 2:
                self.r = GameRect(int(args[0][0]), int(args[0][1]),
                                  int(args[1][0]), int(args[1][1]))

        except (IndexError, TypeError):
            raise TypeError("Argument must be rect style object")

    @classmethod
    def _from4(cls, x, y, w, h):
        # Creates a Rect without any of the checks in Rect.__init__
        rect = cls.__new__(cls)
        rect.r = GameRect(x, y, w, h)
        return rect

    def __repr__(self):
        return "<rect(%d, %d, %d, %d)>" % (self.x, self.y, self.w, self.h)

    def __eq__(self, other):
        if isinstance(other, Rect):
            return ((self.r.x == other.r.x)
                    and (self.r.y == other.r.y)
                    and (self.r.w == other.r.w)
                    and (self.r.h == other.r.h))
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
        data = [self.r.x, self.r.y,
                self.r.w, self.r.h]
        if isinstance(index, slice):
            if index.step is not None:
                raise TypeError("slice steps not supported")
            start = index.start if index.start is not None else 0
            stop = index.stop if index.stop is not None else 4
            return data[start:stop]
        return data[index]

    def __setitem__(self, index, value):
        value = int(value)
        index = int(index)
        if index == 0:
            self.r.x = value
        elif index == 1:
            self.r.y = value
        # normalize if width or height is given
        elif index == 2:
            self.w = value
        elif index == 3:
            self.h = value
        else:
            raise IndexError("index out of range")

    def move(self, *args):
        x, y = unpack_pos(args)
        return Rect._from4(int(self.r.x + x), int(self.r.y + y),
                           self.r.w, self.r.h)

    def move_ip(self, *args):
        x, y = unpack_pos(args)
        self.r.x += int(x)
        self.r.y += int(y)

    def copy(self):
        return Rect._from4(self.r.x, self.r.y,
                           self.r.w, self.r.h)

    def get_x(self):
        return self.r.x
    def set_x(self, new_x):
        self.r.x = int(new_x)
    x = property(get_x, set_x)
    left = property(get_x, set_x)

    def get_y(self):
        return self.r.y
    def set_y(self, new_y):
        self.r.y = int(new_y)
    y = property(get_y, set_y)
    top = property(get_y, set_y)

    def get_w(self):
        return self.r.w
    def set_w(self, new_w):
        self.r.w = int(new_w)
    w = property(get_w, set_w)
    width = property(get_w, set_w)

    def get_h(self):
        return self.r.h
    def set_h(self, new_h):
        self.r.h = int(new_h)
    h = property(get_h, set_h)
    height = property(get_h, set_h)

    def get_right(self):
        return self.r.x + self.r.w
    def set_right(self, r):
        self.r.x = int(r) - self.r.w
    right = property(get_right, set_right)

    def get_bottom(self):
        return self.r.y + self.r.h
    def set_bottom(self, b):
        self.r.y = int(b) - self.r.h
    bottom = property(get_bottom, set_bottom)

    def get_topleft(self):
        return (self.r.x, self.r.y)
    def set_topleft(self, (x, y)):
        self.r.x = int(x)
        self.r.y = int(y)
    topleft = property(get_topleft, set_topleft)

    def get_topright(self):
        return (self.r.x + self.r.w, self.r.y)
    def set_topright(self, (x, y)):
        self.r.x = int(x) - self.r.w
        self.r.y = int(y)
    topright = property(get_topright, set_topright)

    def get_midleft(self):
        return (self.r.x,
                self.r.y + self.r.h // 2)
    def set_midleft(self, (x, y)):
        self.r.x = int(x)
        self.r.y = int(y) - self.r.h // 2
    midleft = property(get_midleft, set_midleft)

    def get_midright(self):
        return (self.r.x + self.r.w,
                self.r.y + self.r.h // 2)
    def set_midright(self, (x, y)):
        self.r.x = int(x) - self.r.w
        self.r.y = int(y) - self.r.h // 2
    midright = property(get_midright, set_midright)

    def get_midtop(self):
        return (self.r.x + self.r.w // 2, self.r.y)

    def set_midtop(self, (x, y)):
        self.r.x = int(x) - self.r.w // 2
        self.r.y = int(y)
    midtop = property(get_midtop, set_midtop)

    def get_center(self):
        return (self.r.x + self.r.w // 2,
                self.r.y + self.r.h // 2)

    def set_center(self, (x, y)):
        self.r.x = int(x) - self.r.w // 2
        self.r.y = int(y) - self.r.h // 2
    center = property(get_center, set_center)

    def get_centerx(self):
        return self.r.x + self.r.w // 2
    def set_centerx(self, x):
        self.r.x = int(x) - self.r.w // 2
    centerx = property(get_centerx, set_centerx)

    def get_centery(self):
        return self.r.y + self.r.h // 2
    def set_centery(self, y):
        self.r.y = int(y) - self.r.h // 2
    centery = property(get_centery, set_centery)

    def get_bottomleft(self):
        return (self.r.x,
                self.r.y + self.r.h)
    def set_bottomleft(self, (x, y)):
        self.r.x = int(x)
        self.r.y = int(y) - self.r.h
    bottomleft = property(get_bottomleft, set_bottomleft)

    def get_midbottom(self):
        return (self.r.x + self.r.w // 2,
                self.r.y + self.r.h)
    def set_midbottom(self, (x, y)):
        self.r.x = int(x) - self.r.w // 2
        self.r.y = int(y) - self.r.h
    midbottom = property(get_midbottom, set_midbottom)

    def get_bottomright(self):
        return (self.r.x + self.r.w,
                self.r.y + self.r.h)
    def set_bottomright(self, (x, y)):
        self.r.x = int(x) - self.r.w
        self.r.y = int(y) - self.r.h
    bottomright = property(get_bottomright, set_bottomright)

    def get_size(self):
        return (self.r.w, self.r.h)
    def set_size(self, (w, h)):
        self.r.w = int(w)
        self.r.h = int(h)
    size = property(get_size, set_size)

    def colliderect(self, other):
        other = game_rect_from_obj(other)
        return do_rects_intersect(self.r, other)

    def inflate(self, x, y):
        return Rect._from4(self.r.x - x // 2, self.r.y - y // 2,
                           self.r.w + x, self.r.h + y)

    def normalize(self):
        """ normalize() -> None
        correct negative sizes
        """
        if self.r.w < 0:
            self.r.x += self.r.w
            self.r.w = -self.r.w
        if self.r.h < 0:
            self.r.y += self.r.h
            self.r.h = -self.r.h

    def inflate_ip(self, *args):
        x, y = unpack_pos(args)
        self.r.x -= x // 2
        self.r.y -= y // 2
        self.r.w += x
        self.r.h += y

    def _calc_clamp(self, rect):
        other = game_rect_from_obj(rect)
        if self.r.w >= other.w:
            x = other.x + other.w // 2 - self.r.w // 2
        elif self.r.x < other.x:
            x = other.x
        elif (self.r.x + self.r.w >
              other.x + other.w):
            x = other.x + other.w - self.r.w
        else:
            x = self.r.x

        if self.r.h >= other.h:
            y = other.y + other.h / 2 - self.r.h / 2
        elif self.r.y < other.y:
            y = other.y
        elif (self.r.y + self.r.h >
              other.y + other.h):
            y = other.y + other.h - self.r.h
        else:
            y = self.r.y

        return x, y

    def clamp(self, *args):
        x, y = self._calc_clamp(args)
        return Rect._from4(x, y, self.r.w, self.r.h)

    def clamp_ip(self, *args):
        x, y = self._calc_clamp(args)
        self.r.x = x
        self.r.y = y

    def clip(self, *rect):
        """Rect.clip(Rect): return Rect
           crops a rectangle inside another"""
        other = game_rect_from_obj(rect)

        if ((self.r.x >= other.x) and
            (self.r.x < (other.x + other.w))):
            x = self.r.x
        elif ((other.x >= self.r.x) and
              (other.x < (self.r.x + self.r.w))):
            x = other.x
        else:
            # no intersect
            return Rect._from4(self.r.x, self.r.y, 0, 0)

        if (((self.r.x + self.r.w) > other.x) and
            ((self.r.x + self.r.w) <=
             (other.x + other.w))):
            w = (self.r.x + self.r.w) - x
        elif (((other.x + other.w) > self.r.x) and
              ((other.x + other.w) <=
               (self.r.x + self.r.w))):
            w = (other.x + other.w) - x
        else:
            # no intersect
            return Rect._from4(self.r.x, self.r.y, 0, 0)

        if ((self.r.y >= other.y) and (
             self.r.y < (other.y + other.h))):
            y = self.r.y
        elif ((other.y >= self.r.y) and
              (other.y < (self.r.y + self.r.h))):
            y = other.y
        else:
            # no intersect
            return Rect._from4(self.r.x, self.r.y, 0, 0)

        if (((self.r.y + self.r.h) > other.y) and
            ((self.r.y + self.r.h) <=
             (other.y + other.h))):
            h = (self.r.y + self.r.h) - y
        elif (((other.y + other.h) > self.r.y) and
              ((other.y + other.h) <=
               (self.r.y + self.r.h))):
            h = (other.y + other.h) - y
        else:
            # no intersect
            return Rect._from4(self.r.x, self.r.y, 0, 0)

        return Rect._from4(x, y, w, h)

    def fit(self, *rect):
        """Rect.fit(Rect): return Rect
           resize and move a rectangle with aspect ratio"""
        other = game_rect_from_obj(*rect)
        xratio = float(self.r.w) / float(other.w)
        yratio = float(self.r.h) / float(other.h)
        maxratio = xratio if xratio > yratio else yratio

        w = int(self.r.w / maxratio)
        h = int(self.r.h / maxratio)

        x = other.x + (other.w - w) // 2
        y = other.y + (other.h - h) // 2

        return Rect._from4(x, y, w, h)

    def contains(self, *rect):
        other = game_rect_from_obj(rect)
        return (self.r.x <= other.x and
                self.r.y <= other.y and
                self.r.x + self.r.w >= other.x + other.w and
                self.r.y + self.r.h >= other.y + other.h and
                self.r.x + self.r.w > other.x and
                self.r.y + self.r.h > other.y)

    def union(self, *rect):
        other = game_rect_from_obj(rect)
        x = min(self.r.x, other.x)
        y = min(self.r.y, other.y)
        w = max(self.r.x + self.r.w,
                other.x + other.w) - x
        h = max(self.r.y + self.r.h,
                other.y + other.h) - y
        return Rect._from4(x, y, w, h)

    def union_ip(self, *rect):
        """ union_ip(Rect) -> None
        joins two rectangles into one, in place
        """
        other = game_rect_from_obj(rect)
        x = min(self.r.x, other.x)
        y = min(self.r.y, other.y)
        w = max(self.r.x + self.r.w,
                other.x + other.w) - x
        h = max(self.r.y + self.r.h,
                other.y + other.h) - y
        self.r.x = x
        self.r.y = y
        self.r.w = w
        self.r.h = h

    def unionall(self, rects):
        """ unionall(Rect_sequence) -> Rect
        the union of many rectangles
        """
        l = self.r.x
        t = self.r.y
        r = self.r.x + self.r.w
        b = self.r.y + self.r.h
        try:
            for args in rects:
                rect = game_rect_from_obj(args)
                l = min(l, rect.x);
                t = min(t, rect.y);
                r = max(r, rect.x + rect.w);
                b = max(b, rect.y + rect.h);
        except TypeError:
            raise TypeError("Argument must be a sequence of rectstyle objects")
        return Rect._from4(l, t, r - l, b - t)

    def unionall_ip(self, rects):
        """ unionall_ip(Rect_sequence) -> None
        the union of many rectangles, in place
        """
        l = self.r.x
        t = self.r.y
        r = self.r.x + self.r.w
        b = self.r.y + self.r.h
        try:
            for args in rects:
                rect = game_rect_from_obj(args)
                l = min(l, rect.x);
                t = min(t, rect.y);
                r = max(r, rect.x + rect.w);
                b = max(b, rect.y + rect.h);
        except TypeError:
            raise TypeError("Argument must be a sequence of rectstyle objects")
        self.r.x = l
        self.r.y = t
        self.r.w = r - l
        self.r.h = b - t

    def collidepoint(self, *args):
        x, y = unpack_pos(args)
        return (self.r.x <= x < self.r.x + self.r.w and
                self.r.y <= y < self.r.y + self.r.h)

    def collidelist(self, rects):
        """ collidelist(list) -> index
        test if one rectangle in a list intersects
        """
        try:
            for i, args in enumerate(rects):
                rect = game_rect_from_obj(args)
                if do_rects_intersect(self.r, rect):
                    return i
        except TypeError:
            raise TypeError("Argument must be a sequence of rectstyle objects")
        return -1

    def collidelistall(self, rects):
        """ collidelistall(list) -> indices
        test if all rectangles in a list intersect
        """
        colliding_indices = []
        try:
            for i, args in enumerate(rects):
                rect = game_rect_from_obj(args)
                if do_rects_intersect(self.r, rect):
                    colliding_indices.append(i)
        except TypeError:
            raise TypeError("Argument must be a sequence of rectstyle objects")
        return colliding_indices

    def collidedict(self, rect_dict, values=False):
        """ collidedict(dict) -> (key, value)
        test if one rectangle in a dictionary intersects
        """
        try:
            for key, val in rect_dict.iteritems():
                if values:
                    try:
                        rect = game_rect_from_obj(val)
                    except TypeError:
                        raise TypeError("Argument must be a dict with rectstyle values")
                else:
                    try:
                        rect = game_rect_from_obj(key)
                    except TypeError:
                        raise TypeError("Argument must be a dict with rectstyle keys")
                if do_rects_intersect(self.r, rect):
                    return key, val
        except AttributeError:
            raise TypeError("Argument must be a dict with rectstyle keys")

    def collidedictall(self, rect_dict, values=False):
        """ collidedictall(dict) -> [(key, value), ...]
        test if all rectangles in a dictionary intersect
        """
        colliding_pairs = []
        try:
            for key, val in rect_dict.iteritems():
                if values:
                    try:
                        rect = game_rect_from_obj(val)
                    except TypeError:
                        raise TypeError("Argument must be a dict with rectstyle values")
                else:
                    try:
                        rect = game_rect_from_obj(key)
                    except TypeError:
                        raise TypeError("Argument must be a dict with rectstyle keys")
                if do_rects_intersect(self.r, rect):
                    colliding_pairs.append((key, val))
        except AttributeError:
            raise TypeError("Argument must be a dict with rectstyle keys")
        return colliding_pairs


def unpack_pos(args):
    try:
        x, y = args
    except ValueError:
        x, y = args[0]
    except (TypeError, IndexError):
        raise TypeError("argument must contain two numbers")
    return x, y


def do_rects_intersect(A, B):
    return (A.x < B.x + B.w and A.y < B.y + B.h and
            A.x + A.w > B.x and A.y + A.h > B.y)


def game_rect_from_obj(obj):
    if isinstance(obj, Rect):
        return obj.r
    try:
        if len(obj) == 1:
            return obj[0].r
        elif len(obj) == 4:
            return GameRect(int(obj[0]), int(obj[1]), int(obj[2]), int(obj[3]))
        elif len(obj) == 2:
            return GameRect(int(obj[0][0]), int(obj[0][1]),
                            int(obj[1][0]), int(obj[1][1]))
        raise TypeError("Argument must be rect style object")
    except (ValueError, AttributeError):
        raise TypeError("Argument must be rect style object")
