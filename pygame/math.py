""" Math module """

from __future__ import absolute_import
import math
from numbers import Number

VECTOR_EPSILON = 1e-6  # For equality tests


def enable_swizzling():
    """Globally enables swizzling for vectors.

    Enables swizzling for all vectors until disable_swizzling() is called.
    By default swizzling is disabled.

    Note:  There may be performance degradation, as this replaces __getattr__
           and __setattr__.  Only enable if required.
    """
    # __getattr__ is not defined by default, so nothing to save
    Vector2.__getattr__ = Vector2.__getattr_swizzle__

    if '__oldsetattr__' not in dir(Vector2):
        Vector2.__oldsetattr__ = Vector2.__setattr__
    Vector2.__setattr__ = Vector2.__setattr_swizzle__


def disable_swizzling():
    """Globally disables swizzling for vectors.

    Disables swizzling for all vectors until enable_swizzling() is called.
    By default swizzling is disabled.
    """
    if '__getattr__' in dir(Vector2):
        del Vector2.__getattr__
    if '__oldsetattr__' in dir(Vector2):
        Vector2.__setattr__ = Vector2.__oldsetattr__


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
        return "<Vector2({}, {})>".format(self._x, self._y)

    def __str__(self):
        return "[{}, {}]".format(self._x, self._y)

    def __len__(self):
        return 2

    def __getitem__(self, key):
        """Provide indexed read access (vec[0] is x vec[1] is y)."""
        return [self._x, self._y][key]

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
                raise ValueError("Invalid slice or value arguments (key {}, value {}).".
                                 format(key, value))
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
            return (abs(self._x - other.x) < VECTOR_EPSILON
                    and abs(self._y - other.y) < VECTOR_EPSILON)
        elif hasattr(other, '__iter__'):
            try:
                other_v = Vector2(other)
                return self == other_v
            except TypeError:
                # Doesn't seem to be vector2-like, so NotImplemented
                return False
        return False

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self._x + other.x, self._y + other.y)
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
            return Vector2(self._x - other.x, self._y - other.y)
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
            return Vector2(other.x - self._x, other.y - self._y)
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
            return Vector2(self._x * float(other), self._y * float(other))
        elif isinstance(other, Vector2):
            return self.dot(other)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, other):
        if isinstance(other, Number):
            return Vector2(self._x / float(other), self._y / float(other))
        return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, Number):
            return Vector2(self._x // other, self._y // other)
        return NotImplemented

    def __bool__(self):
        """bool operator for Python 3."""
        return self._x != 0 or self._y != 0

    def __nonzero__(self):
        """bool operator for Python 2."""
        return self.__bool__()

    def __neg__(self):
        return Vector2(-self._x, -self._y)

    def __pos__(self):
        return Vector2(self._x, self._y)

    def __iter__(self):
        return (coord for coord in [self._x, self._y])

    def __getattr_swizzle__(self, name):
        result = []
        for letter in name:
            if letter == 'x':
                result.append(self._x)
            elif letter == 'y':
                result.append(self._y)
            else:
                raise AttributeError('Invalid swizzle request: {}.'.format(name))
        return tuple(result)

    def __setattr_swizzle__(self, name, value):
        if name == 'xy':
            super(Vector2, self).__setattr__('_x', value[0])
            super(Vector2, self).__setattr__('_y', value[1])
        elif name == 'yx':
            super(Vector2, self).__setattr__('_y', value[0])
            super(Vector2, self).__setattr__('_x', value[1])
        elif name == 'xx' or name == 'yy':
            raise AttributeError('Invalid swizzle request: {}={}.'.format(name, value))
        else:
            super(Vector2, self).__setattr__(name, value)

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
        return self._x * vec.x + self._y * vec.y

    def cross(self, vec):
        """calculates the determinant - 2D analog of the cross- or vector-product."""
        if not isinstance(vec, Vector2):
            vec = Vector2(vec)
        return self._x * vec.y - self._y * vec.x

    def length(self):
        """returns the euclidic length of the vector."""
        return math.sqrt(self._x * self._x + self._y * self._y)

    def length_squared(self):
        """returns the squared euclidic length of the vector."""
        return self._x * self._x + self._y * self._y

    def normalize(self):
        """returns a vector with the same direction but length 1."""
        length = self.length()
        if length >= VECTOR_EPSILON:
            return Vector2(self._x/length, self._y/length)
        else:
            raise ValueError("Can't normalize Vector of length Zero")

    def normalize_ip(self):
        """normalizes the vector in place so that its length is 1."""
        norm_vec = self.normalize()
        self.x = norm_vec.x
        self.y = norm_vec.y

    def is_normalized(self):
        """tests if the vector is normalized i.e. has length == 1."""
        length_squared = self.length_squared()
        return abs(length_squared - 1.0) < VECTOR_EPSILON

    def scale_to_length(self, new_length):
        """scales the vector to a given length."""
        length = self.length()
        if length >= VECTOR_EPSILON:
            new_vec = Vector2(self._x/length*new_length, self._y/length*new_length)
            self.x = new_vec.x
            self.y = new_vec.y
        else:
            raise ValueError("Cannot scale a vector with zero length")

    def reflect(self, normal):
        """returns a vector reflected around a given normal."""
        normal_vec = Vector2(normal).normalize()  # can't assume input is normalized
        dot_product = self.dot(normal_vec)
        result_vec = Vector2(self._x - 2 * normal_vec.x * dot_product,
                             self._y - 2 * normal_vec.y * dot_product)
        return result_vec

    def reflect_ip(self, normal):
        """reflect the vector around a given normal in place."""
        result_vec = self.reflect(normal)
        self.x = result_vec.x
        self.y = result_vec.y

    def distance_to(self, vec):
        """calculates the Euclidic distance to a given vector."""
        if not isinstance(vec, Vector2):
            vec = Vector2(vec)
        delta = self - vec
        return delta.length()

    def distance_squared_to(self, vec):
        """calculates the squared Euclidic distance to a given vector."""
        if not isinstance(vec, Vector2):
            vec = Vector2(vec)
        delta = self - vec
        return delta.length_squared()

    def lerp(self, vec, t):
        """returns a linear interpolation to the given vector, with t in [0..1]."""
        if t < 0 or t > 1:
            raise ValueError("Argument 't' must be in range [0, 1]")
        elif not isinstance(vec, Vector2):
            raise TypeError("Expected 'vec' to be of type Vector2")
        else:
            # check for special cases, exit early
            if t == 0:
                return self
            elif t == 1:
                return vec

            x = self._x * (1 - t) + vec.x * t
            y = self._y * (1 - t) + vec.y * t
            return Vector2(x, y)

    def slerp(self, vec, t):
        """returns a spherical interpolation to the given vector, with t in [-1..1]."""
        if t < -1 or t > 1:
            raise ValueError("Argument 't' must be in range [-1, 1]")
        elif not isinstance(vec, Vector2):
            raise TypeError("Expected 'vec' to be of type Vector2")
        else:
            # check for special cases, exit early
            if t == 0:
                return self
            elif t == -1 or t == 1:
                return vec

            polar_self = self.as_polar()
            polar_other = vec.as_polar()
            if polar_self[0] < VECTOR_EPSILON or polar_other[0] < VECTOR_EPSILON:
                raise ValueError("Can't use slerp with zero vector")
            new_radius = polar_self[0] * (1 - abs(t)) + polar_other[0] * abs(t)
            angle_delta = (polar_other[1] - polar_self[1]) % 360.0
            if abs(angle_delta - 180) < VECTOR_EPSILON:
                raise ValueError("Slerp with 180 degrees is undefined.")
            if t >= 0:
                # take the shortest route
                if angle_delta > 180:
                    angle_delta -= 360
            else:
                # go the long way around
                if angle_delta < 180:
                    angle_delta = 360 - angle_delta
            new_angle = polar_self[1] + angle_delta * t
            result_vec = Vector2()
            result_vec.from_polar((new_radius, new_angle))
            return result_vec

    def elementwise(self):
        """Return object for an elementwise operation."""
        return ElementwiseVectorProxy(self)

    def rotate(self, angle):
        """rotates a vector by a given angle in degrees."""
        # make sure angle is in range [0, 360)
        angle = angle % 360.0

        # special-case rotation by 0, 90, 180 and 270 degrees
        if ((angle + VECTOR_EPSILON) % 90.0) < 2 * VECTOR_EPSILON:
            quad =  int((angle + VECTOR_EPSILON) / 90)
            if quad == 0 or quad == 4:  # 0 or 360 degrees
                x = self._x
                y = self._y
            elif quad == 1:  # 90 degrees
                x = -self._y
                y = self._x
            elif quad == 2:  # 180 degreees
                x = -self._x
                y = -self._y
            elif quad == 3:  # 270 degrees
                x = self._y
                y = -self._x
            else:
                # this should NEVER happen and means a bug in the code
                raise RuntimeError("Please report this bug in Vector2.rotate "
                                   "to the developers")
        else:
            angle_rad = math.radians(angle)
            sin_value = math.sin(angle_rad)
            cos_value = math.cos(angle_rad)
            x = cos_value * self._x - sin_value * self._y
            y = sin_value * self._x + cos_value * self._y

        return Vector2(x, y)

    def rotate_ip(self, angle):
        """rotates the vector by a given angle in degrees in place."""
        new_vec = self.rotate(angle)
        self.x = new_vec._x
        self.y = new_vec._y

    def angle_to(self, vec):
        """calculates the minimum angle to a given vector in degrees."""
        if not isinstance(vec, Vector2):
            vec = Vector2(vec)
        angle_self_rad = math.atan2(self._y, self._x)
        angle_other_rad = math.atan2(vec.y, vec.x)
        return math.degrees(angle_other_rad - angle_self_rad)

    def as_polar(self):
        """returns a tuple with radial distance and azimuthal angle."""
        r = self.length()
        angle = math.degrees(math.atan2(self._y, self._x))
        return (r, angle)

    def from_polar(self, polar):
        """Sets x and y from a polar coordinates tuple."""
        if isinstance(polar, tuple) and len(polar) == 2:
            r = polar[0]
            angle_rad = math.radians(polar[1])
            self.x = r * math.cos(angle_rad)
            self.y = r * math.sin(angle_rad)
        else:
            raise TypeError("Expected 2 element tuple (radius, angle), but got {}"
                            .format(polar))


class Vector3(object):
    pass


class ElementwiseVectorProxy(object):
    """Class used internally for elementwise vector operations."""

    def __init__(self, vector):
        self.vector = Vector2(vector)

    def __add__(self, other):
        if isinstance(other, Number):
            return Vector2(self.vector.x + other, self.vector.y + other)
        elif isinstance(other, Vector2):
            return Vector2(self.vector.x + other.x, self.vector.y + other.y)
        elif isinstance(other, ElementwiseVectorProxy):
            return self.vector + other.vector
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Number):
            return Vector2(self.vector.x - other, self.vector.y - other)
        elif isinstance(other, Vector2):
            return Vector2(self.vector.x - other.x, self.vector.y - other.y)
        elif isinstance(other, ElementwiseVectorProxy):
            return self.vector - other.vector
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Number):
            return Vector2(other - self.vector.x, other - self.vector.y)
        elif isinstance(other, Vector2):
            return Vector2(other.x - self.vector.x, other.y - self.vector.y)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Number):
            return Vector2(self.vector.x * other, self.vector.y * other)
        elif isinstance(other, Vector2):
            return Vector2(self.vector.x * other.x, self.vector.y * other.y)
        elif isinstance(other, ElementwiseVectorProxy):
            return Vector2(self.vector.x * other.vector.x,
                           self.vector.y * other.vector.y)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, other):
        if isinstance(other, Number):
            return Vector2(self.vector.x / other, self.vector.y / other)
        elif isinstance(other, Vector2):
            return Vector2(self.vector.x / other.x, self.vector.y / other.y)
        elif isinstance(other, ElementwiseVectorProxy):
            return Vector2(self.vector.x / other.vector.x,
                           self.vector.y / other.vector.y)
        return NotImplemented

    def __rdiv__(self, other):
        if isinstance(other, Number):
            return Vector2(other / self.vector.x, other / self.vector.y)
        elif isinstance(other, Vector2):
            return Vector2(other.x / self.vector.x, other.y / self.vector.y)
        return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, Number):
            return Vector2(self.vector.x // other, self.vector.y // other)
        elif isinstance(other, Vector2):
            return Vector2(self.vector.x // other.x, self.vector.y // other.y)
        elif isinstance(other, ElementwiseVectorProxy):
            return Vector2(self.vector.x // other.vector.x,
                           self.vector.y // other.vector.y)
        return NotImplemented

    def __rfloordiv__(self, other):
        if isinstance(other, Number):
            return Vector2(other // self.vector.x, other // self.vector.y)
        elif isinstance(other, Vector2):
            return Vector2(other.x // self.vector.x, other.y // self.vector.y)
        return NotImplemented

    def __pow__(self, other):
        if isinstance(other, Number):
            return Vector2(self.vector.x ** other, self.vector.y ** other)
        elif isinstance(other, Vector2):
            return Vector2(self.vector.x ** other.x, self.vector.y ** other.y)
        elif isinstance(other, ElementwiseVectorProxy):
            return Vector2(self.vector.x ** other.vector.x,
                           self.vector.y ** other.vector.y)
        return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, Number):
            return Vector2(other ** self.vector.x, other ** self.vector.y)
        elif isinstance(other, Vector2):
            return Vector2(other.x ** self.vector.x, other.y ** self.vector.y)
        return NotImplemented

    def __mod__(self, other):
        if isinstance(other, Number):
            return Vector2(self.vector.x % other, self.vector.y % other)
        elif isinstance(other, Vector2):
            return Vector2(self.vector.x % other.x, self.vector.y % other.y)
        elif isinstance(other, ElementwiseVectorProxy):
            return Vector2(self.vector.x % other.vector.x,
                           self.vector.y % other.vector.y)
        return NotImplemented

    def __rmod__(self, other):
        if isinstance(other, Number):
            return Vector2(other % self.vector.x, other % self.vector.y)
        elif isinstance(other, Vector2):
            return Vector2(other.x % self.vector.x, other.y % self.vector.y)
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Number):
            return self.vector.x == other and self.vector.y == other
        elif isinstance(other, ElementwiseVectorProxy):
            return self.vector.x == other.vector.x and self.vector.y == other.vector.y
        return NotImplemented

    def __neq__(self, other):
        if isinstance(other, Number):
            return self.vector.x != other or self.vector.y != other
        elif isinstance(other, ElementwiseVectorProxy):
            return self.vector.x != other.vector.x or self.vector.y != other.vector.y
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Number):
            return self.vector.x > other and self.vector.y > other
        elif isinstance(other, ElementwiseVectorProxy):
            return self.vector.x > other.vector.x and self.vector.y > other.vector.y
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Number):
            return self.vector.x < other and self.vector.y < other
        elif isinstance(other, ElementwiseVectorProxy):
            return self.vector.x < other.vector.x and self.vector.y < other.vector.y
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Number):
            return self.vector.x >= other and self.vector.y >= other
        elif isinstance(other, ElementwiseVectorProxy):
            return self.vector.x >= other.vector.x and self.vector.y >= other.vector.y
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Number):
            return self.vector.x <= other and self.vector.y <= other
        elif isinstance(other, ElementwiseVectorProxy):
            return self.vector.x <= other.vector.x and self.vector.y <= other.vector.y
        return NotImplemented

    def __abs__(self):
        return Vector2(abs(self.vector.x), abs(self.vector.y))

    def __neg__(self):
        return -self.vector

    def __pos__(self):
        return self.vector

    def __bool__(self):
        """bool operator for Python 3."""
        return bool(self.vector)

    def __nonzero__(self):
        """bool operator for Python 2."""
        return bool(self.vector)
