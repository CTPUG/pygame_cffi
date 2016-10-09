""" Math module """

from numbers import Number


swizzling = False


def enable_swizzling():
    """Globally enables swizzling for vectors.

    Enables swizzling for all vectors until disable_swizzling() is called.
    By default swizzling is disabled.
    """
    global swizzling
    swizzling = True


def disable_swizzling():
    """Globally disables swizzling for vectors.

    Disables swizzling for all vectors until enable_swizzling() is called.
    By default swizzling is disabled.
    """
    global swizzling
    swizzling = False


class Vector2(object):
    """A 2-Dimensional Vector."""

    def __init__(self, *args):
        if len(args) == 0:
            self.x = 0.0
            self.y = 0.0
        elif len(args) == 1:
            if isinstance(args[0], Vector2):
                self.x = args[0].x
                self.y = args[0].y
            elif isinstance(args[0], basestring):
                if args[0].startswith("<Vector2(") and args[0].endswith(")>"):
                    tokens = args[0][9:-2].split(",")
                    try:
                        self.x = float(tokens[0])
                        self.y = float(tokens[1])
                    except ValueError:
                        raise TypeError("Invalid string arguments - not floats ({}).".
                                        format(args[0]))
                else:
                    raise TypeError("Invalid string argument - not like __repr__ ({}).".
                                    format(args[0]))
            elif len(args[0]) == 2:
                self.x = args[0][0]
                self.y = args[0][1]
            else:
                raise TypeError("Invalid argument length ({}).".format(len(args[0])))
        else:
            self.x = args[0]
            self.y = args[1]

    def __repr__(self):
        return "<Vector2({}, {})>".format(self.x, self.y)

    def __str__(self):
        return "[{}, {}]".format(self.x, self.y)

    def __len__(self):
        return 2

    def __getitem__(self, key):
        """Provide indexed read access (vec[0] is x vec[1] is y)."""
        if isinstance(key, slice):
            return [self[ind] for ind in xrange(*key.indices(len(self)))]
        elif isinstance(key, int):
            if key < 0:
                key += len(self)
            if key == 0:
                return self.x
            elif key == 1:
                return self.y
            else:
                raise IndexError("Out of range index requested: {}".format(key))
        else:
            raise TypeError("Invalid argument type")

    def __setitem__(self, key, value):
        """Provide indexed modification."""
        if isinstance(value, Vector2):
            value = [value.x, value.y]
        if isinstance(key, slice):
            indices = range(*key.indices(len(self)))
            if len(value) <= len(self) and len(value) == len(indices):
                for count, index in enumerate(indices):
                    self[index] = value[count]
            else:
                raise ValueError("Invalid slice or value arguments ({}).".format(key))
        elif isinstance(key, int):
            if key < 0:
                key += len(self)
            if key == 0:
                self.x = value
            elif key == 1:
                self.y = value
            else:
                raise IndexError("Out of range index requested: {}".format(key))
        else:
            raise TypeError("Invalid argument type")

    def __delitem__(self):
        """Item deletion not supported."""
        raise TypeError("Items may not be deleted.")

    def __eq__(self, other):
        if isinstance(other, Vector2):
            return (self.x == other.x) and (self.y == other.y)
        elif hasattr(other, '__iter__'):
            try:
                other_v = Vector2(other)
                return self == other_v
            except TypeError:
                # Doesn't seem to be vector2-like, so NotImplemented
                return False
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        elif hasattr(other, '__iter__'):
            try:
                other_v = Vector2(other)
                return self + other_v
            except TypeError:
                # Doesn't seem to be vector2-like, so NotImplemented
                return NotImplemented
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        elif hasattr(other, '__iter__'):
            try:
                other_v = Vector2(other)
                return self - other_v
            except TypeError:
                # Doesn't seem to be vector2-like, so NotImplemented
                return NotImplemented
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(other.x - self.x, other.y - self.y)
        elif hasattr(other, '__iter__'):
            try:
                other_v = Vector2(other)
                return other_v - self
            except TypeError:
                # Doesn't seem to be vector2-like, so NotImplemented
                return NotImplemented
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Number):
            return Vector2(self.x * float(other), self.y * float(other))
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, other):
        if isinstance(other, Number):
            return Vector2(self.x / float(other), self.y / float(other))
        return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, Number):
            return Vector2(self.x // other, self.y // other)
        return NotImplemented

    def __bool__(self):
        """bool operator for Python 3."""
        return self.x != 0 or self.y != 0

    def __nonzero__(self):
        """bool operator for Python 2."""
        return self.__bool__()

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __pos__(self):
        return Vector2(self.x, self.y)

    @property
    def x(self):
        """Vector x value."""
        return self._x

    @x.setter
    def x(self, value):
        if isinstance(value, Number):
            self._x = value
        else:
            raise TypeError("Value {} is not a valid number.".format(value))

    @property
    def y(self):
        """Vector y value."""
        return self._y

    @y.setter
    def y(self, value):
        if isinstance(value, Number):
            self._y = value
        else:
            raise TypeError("Value {} is not a valid number.".format(value))

    def dot(self, vec):
        """calculates the dot- or scalar-product with the other vector.

        dot(Vector2) -> float.
        """
        if not isinstance(vec, Vector2):
            vec = Vector2(vec)
        return self.x * vec.x + self.y * vec.y

    def cross(self):
        """calculates the cross- or vector-product."""
        pass

    def length(self):
        """returns the euclidic length of the vector."""
        pass

    def length_squared(self):
        """returns the squared euclidic length of the vector."""
        pass

    def normalize(self):
        """returns a vector with the same direction but length 1."""
        pass

    def normalize_ip(self):
        """normalizes the vector in place so that its length is 1."""
        pass

    def is_normalized(self):
        """tests if the vector is normalized i.e. has length == 1."""
        pass

    def scale_to_length(self):
        """scales the vector to a given length."""
        pass

    def reflect(self):
        """returns a vector reflected of a given normal."""
        pass

    def reflect_ip(self):
        """reflect the vector of a given normal in place."""
        pass

    def distance_to(self):
        """calculates the euclidic distance to a given vector."""
        pass

    def distance_squared_to(self):
        """calculates the squared euclidic distance to a given vector."""
        pass

    def lerp(self):
        """returns a linear interpolation to the given vector."""
        pass

    def slerp(self):
        """returns a spherical interpolation to the given vector."""
        pass

    def elementwise(self):
        """The next operation will be performed elementwize."""
        pass

    def rotate(self):
        """rotates a vector by a given angle in degrees."""
        pass

    def rotate_ip(self):
        """rotates the vector by a given angle in degrees in place."""
        pass

    def angle_to(self):
        """calculates the angle to a given vector in degrees."""
        pass

    def as_polar(self):
        """returns a tuple with radial distance and azimuthal angle."""
        pass

    def from_polar(self):
        """Sets x and y from a polar coordinates tuple."""
        pass


class Vector3(object):
    pass
