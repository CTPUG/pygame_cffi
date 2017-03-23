# pygame_cffi - a cffi implementation of the pygame library
# Copyright (C) 2016  Anton Joubert
# Copyright (C) 2016  Simon Cross
# Copyright (C) 2016  Neil Muller
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301  USA

""" Math module """

from __future__ import absolute_import as _absolute_import
from __future__ import division as _division

import math as _math
from numbers import Number as _Number

from pygame.compat import string_types as _string_types
from pygame.compat import pow_compat as _pow_compat

_VECTOR_EPSILON = 1e-6  # For equality tests (default for new vectors)


def enable_swizzling():
    """Globally enables swizzling for vectors.

    Enables swizzling for all vectors until disable_swizzling() is called.
    By default swizzling is disabled.

    Note:  There may be performance degradation, as this replaces __getattr__
           and __setattr__.  Only enable if required.
    """
    # __getattr__ is not defined by default, so nothing to save
    Vector2.__getattr__ = Vector2.__getattr_swizzle__
    Vector3.__getattr__ = Vector3.__getattr_swizzle__

    if '__oldsetattr__' not in dir(Vector2):
        Vector2.__oldsetattr__ = Vector2.__setattr__
    Vector2.__setattr__ = Vector2.__setattr_swizzle__

    if '__oldsetattr__' not in dir(Vector3):
        Vector3.__oldsetattr__ = Vector3.__setattr__
    Vector3.__setattr__ = Vector3.__setattr_swizzle__


def disable_swizzling():
    """Globally disables swizzling for vectors.

    Disables swizzling for all vectors until enable_swizzling() is called.
    By default swizzling is disabled.
    """
    if '__getattr__' in dir(Vector2):
        del Vector2.__getattr__
    if '__oldsetattr__' in dir(Vector2):
        Vector2.__setattr__ = Vector2.__oldsetattr__
    if '__getattr__' in dir(Vector3):
        del Vector3.__getattr__
    if '__oldsetattr__' in dir(Vector3):
        Vector3.__setattr__ = Vector3.__oldsetattr__


class Vector2(object):
    """A 2-Dimensional Vector."""

    def __init__(self, *args):
        if len(args) == 0:
            self.x = 0.0
            self.y = 0.0
        elif len(args) == 1:
            if isinstance(args[0], _Number):
                self.x = args[0]
                self.y = 0.0
            elif isinstance(args[0], Vector2):
                self.x = args[0].x
                self.y = args[0].y
            elif isinstance(args[0], _string_types):
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
        self.epsilon = _VECTOR_EPSILON

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
            return (abs(self._x - other.x) < self._epsilon and
                    abs(self._y - other.y) < self._epsilon)
        elif hasattr(other, '__iter__'):
            try:
                other_v = Vector2(other)
                return self == other_v
            except TypeError:
                # Doesn't seem to be vector2-like, so NotImplemented
                return NotImplemented
        return NotImplemented

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
        if isinstance(other, _Number):
            other = float(other)
            return Vector2(self._x * other, self._y * other)
        elif isinstance(other, Vector2):
            return self.dot(other)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, _Number):
            other = float(other)
            return Vector2(self._x / other, self._y / other)
        return NotImplemented

    __div__ = __truediv__  # for backwards compatibility with Python 2

    def __floordiv__(self, other):
        if isinstance(other, _Number):
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
        if isinstance(value, _Number):
            self._x = value
        else:
            raise TypeError("Value {} is not a valid number.".format(value))

    @property
    def y(self):
        """Vector y value."""
        return self._y

    @y.setter
    def y(self, value):
        if isinstance(value, _Number):
            self._y = value
        else:
            raise TypeError("Value {} is not a valid number.".format(value))

    @property
    def epsilon(self):
        """Small value used for vector comparisons."""
        return self._epsilon

    @epsilon.setter
    def epsilon(self, value):
        if isinstance(value, _Number):
            self._epsilon = value
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
        return _math.sqrt(self._x * self._x + self._y * self._y)

    def length_squared(self):
        """returns the squared euclidic length of the vector."""
        return self._x * self._x + self._y * self._y

    def normalize(self):
        """returns a vector with the same direction but length 1."""
        length = self.length()
        if length >= self._epsilon:
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
        return abs(length_squared - 1.0) < self._epsilon

    def scale_to_length(self, new_length):
        """scales the vector to a given length."""
        length = self.length()
        if length >= self._epsilon:
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
            if polar_self[0] < self._epsilon or polar_other[0] < self._epsilon:
                raise ValueError("Can't use slerp with zero vector")
            new_radius = polar_self[0] * (1 - abs(t)) + polar_other[0] * abs(t)
            angle_delta = (polar_other[1] - polar_self[1]) % 360.0
            if abs(angle_delta - 180) < self._epsilon:
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
        return _ElementwiseVector2Proxy(self)

    def rotate(self, angle):
        """rotates a vector by a given angle in degrees."""
        x, y = _rotate_2d(self._x, self._y, angle, self._epsilon)
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
        angle_self_rad = _math.atan2(self._y, self._x)
        angle_other_rad = _math.atan2(vec.y, vec.x)
        return _math.degrees(angle_other_rad - angle_self_rad)

    def as_polar(self):
        """returns a tuple with radial distance and azimuthal angle."""
        r = self.length()
        angle = _math.degrees(_math.atan2(self._y, self._x))
        return (r, angle)

    def from_polar(self, polar):
        """Sets x and y from a polar coordinates tuple."""
        if isinstance(polar, tuple) and len(polar) == 2:
            r = polar[0]
            angle_rad = _math.radians(polar[1])
            self.x = r * _math.cos(angle_rad)
            self.y = r * _math.sin(angle_rad)
        else:
            raise TypeError("Expected 2 element tuple (radius, angle), but got {}"
                            .format(polar))


class Vector3(object):
    """A 3-Dimensional Vector."""

    def __init__(self, *args):
        if len(args) == 0:
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
        elif len(args) == 1:
            if isinstance(args[0], _Number):
                self.x = args[0]
                self.y = 0.0
                self.z = 0.0
            elif isinstance(args[0], Vector3):
                self.x = args[0].x
                self.y = args[0].y
                self.z = args[0].z
            elif isinstance(args[0], _string_types):
                if args[0].startswith("<Vector3(") and args[0].endswith(")>"):
                    tokens = args[0][9:-2].split(",")
                    try:
                        self.x = float(tokens[0])
                        self.y = float(tokens[1])
                        self.z = float(tokens[2])
                    except ValueError:
                        raise TypeError("Invalid string arguments - not floats ({}).".
                                        format(args[0]))
                else:
                    raise TypeError("Invalid string argument - not like __repr__ ({}).".
                                    format(args[0]))
            elif len(args[0]) == 3:
                self.x = args[0][0]
                self.y = args[0][1]
                self.z = args[0][2]
            else:
                raise TypeError("Invalid argument length ({}).".format(len(args[0])))
        elif len(args) == 2:
            self.x = args[0]
            self.y = args[1]
            self.z = 0.0
        else:
            self.x = args[0]
            self.y = args[1]
            self.z = args[2]
        self.epsilon = _VECTOR_EPSILON

    def __repr__(self):
        return "<Vector3({}, {}, {})>".format(self._x, self._y, self._z)

    def __str__(self):
        return "[{}, {}, {}]".format(self._x, self._y, self._z)

    def __len__(self):
        return 3

    def __getitem__(self, key):
        """Provide indexed read access (vec[0] is x, vec[1] is y, vec[2] is z)."""
        return [self._x, self._y, self._z][key]

    def __setitem__(self, key, value):
        """Provide indexed modification."""
        if isinstance(value, Vector3):
            value = [value.x, value.y, value.z]
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
            elif key == 2:
                self.z = value
            else:
                raise IndexError("Out of range index requested: {}".format(key))
        else:
            raise TypeError("Invalid argument type")

    def __delitem__(self):
        """Item deletion not supported."""
        raise TypeError("Items may not be deleted.")

    def __eq__(self, other):
        if isinstance(other, Vector3):
            return (abs(self._x - other.x) < self._epsilon and
                    abs(self._y - other.y) < self._epsilon and
                    abs(self._z - other.z) < self._epsilon)
        elif hasattr(other, '__iter__'):
            try:
                other_v = Vector3(other)
                return self == other_v
            except TypeError:
                # Doesn't seem to be vector3-like, so NotImplemented
                return NotImplemented
        return NotImplemented

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self._x + other.x, self._y + other.y, self._z + other.z)
        elif hasattr(other, '__iter__'):
            try:
                other_v = Vector3(other)
                return self + other_v
            except TypeError:
                # Doesn't seem to be vector3-like, so NotImplemented
                return NotImplemented
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self._x - other.x, self._y - other.y, self._z - other.z)
        elif hasattr(other, '__iter__'):
            try:
                other_v = Vector3(other)
                return self - other_v
            except TypeError:
                # Doesn't seem to be vector3-like, so NotImplemented
                return NotImplemented
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Vector3):
            return Vector3(other.x - self._x, other.y - self._y, other.z - self._z)
        elif hasattr(other, '__iter__'):
            try:
                other_v = Vector3(other)
                return other_v - self
            except TypeError:
                # Doesn't seem to be vector3-like, so NotImplemented
                return NotImplemented
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, _Number):
            other = float(other)
            return Vector3(self._x * other, self._y * other, self._z * other)
        elif isinstance(other, Vector3):
            return self.dot(other)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, _Number):
            other = float(other)
            return Vector3(self._x / other, self._y / other, self._z / other)
        return NotImplemented

    __div__ = __truediv__  # for backwards compatibility with Python 2

    def __floordiv__(self, other):
        if isinstance(other, _Number):
            return Vector3(self._x // other, self._y // other, self._z // other)
        return NotImplemented

    def __bool__(self):
        """bool operator for Python 3."""
        return self._x != 0 or self._y != 0 or self._z != 0

    def __nonzero__(self):
        """bool operator for Python 2."""
        return self.__bool__()

    def __neg__(self):
        return Vector3(-self._x, -self._y, -self._z)

    def __pos__(self):
        return Vector3(self._x, self._y, self._z)

    def __iter__(self):
        return (coord for coord in [self._x, self._y, self._z])

    def __getattr_swizzle__(self, name):
        result = []
        for letter in name:
            if letter == 'x':
                result.append(self._x)
            elif letter == 'y':
                result.append(self._y)
            elif letter == 'z':
                result.append(self._z)
            else:
                raise AttributeError('Invalid swizzle request: {}.'.format(name))
        return tuple(result)

    def __setattr_swizzle__(self, name, value):

        def set_from_index(attr, index):
            if index < len(value):
                super(Vector3, self).__setattr__(attr, value[index])
            else:
                raise TypeError(
                    'Input too short for swizzle assignment: {}={}'
                    .format(name, value))

        if name[0] in ['x', 'y', 'z']:
            # might be a valid swizzle request
            if isinstance(value, _Number):
                value = [value]  # change to a list to work with loop below
            num_x, num_y, num_z = 0, 0, 0
            for index, char in enumerate(name):
                if char == 'x':
                    if num_x == 0:
                        set_from_index('_x', index)
                    num_x += 1
                elif char == 'y':
                    if num_y == 0:
                        set_from_index('_y', index)
                    num_y += 1
                elif char == 'z':
                    if num_z == 0:
                        set_from_index('_z', index)
                    num_z += 1
                else:
                    # might not be a swizzle request, so try other attributes
                    super(Vector3, self).__setattr__(name, value)
                    return
                if num_x > 1 or num_y > 1 or num_z > 1:
                    raise AttributeError(
                        'Attribute assignment conflicts with swizzling.: {}={}.'
                        .format(name, value))
        elif name.startswith('ww'):
            # This is just to make the unit tests happy!
            raise AttributeError('Invalid swizzle request: {}={}.'.format(name, value))
        else:
            super(Vector3, self).__setattr__(name, value)

    @property
    def x(self):
        """Vector x value."""
        return self._x

    @x.setter
    def x(self, value):
        if isinstance(value, _Number):
            self._x = value
        else:
            raise TypeError("Value {} is not a valid number.".format(value))

    @property
    def y(self):
        """Vector y value."""
        return self._y

    @y.setter
    def y(self, value):
        if isinstance(value, _Number):
            self._y = value
        else:
            raise TypeError("Value {} is not a valid number.".format(value))

    @property
    def z(self):
        """Vector z value."""
        return self._z

    @z.setter
    def z(self, value):
        if isinstance(value, _Number):
            self._z = value
        else:
            raise TypeError("Value {} is not a valid number.".format(value))

    @property
    def epsilon(self):
        """Small value used for vector comparisons."""
        return self._epsilon

    @epsilon.setter
    def epsilon(self, value):
        if isinstance(value, _Number):
            self._epsilon = value
        else:
            raise TypeError("Value {} is not a valid number.".format(value))

    def dot(self, vec):
        """calculates the dot- or scalar-product with the other vector.

        dot(Vector3) -> float.
        """
        if not isinstance(vec, Vector3):
            vec = Vector3(vec)
        return self._x * vec.x + self._y * vec.y + self._z * vec.z

    def cross(self, vec):
        """calculates the cross- or vector-product with the other vector.

        cross(Vector3) -> Vector3
        """
        if not isinstance(vec, Vector3):
            vec = Vector3(vec)
        return Vector3(
            self._y * vec.z - self._z * vec.y,
            self._z * vec.x - self._x * vec.z,
            self._x * vec.y - self._y * vec.x
        )

    def length(self):
        """returns the euclidic length of the vector."""
        return _math.sqrt(self._x * self._x + self._y * self._y + self._z * self._z)

    def length_squared(self):
        """returns the squared euclidic length of the vector."""
        return self._x * self._x + self._y * self._y + self._z * self._z

    def normalize(self):
        """returns a vector with the same direction but length 1."""
        length = self.length()
        if length >= self._epsilon:
            return Vector3(self._x/length, self._y/length, self._z/length)
        else:
            raise ValueError("Can't normalize Vector of length Zero")

    def normalize_ip(self):
        """normalizes the vector in place so that its length is 1."""
        norm_vec = self.normalize()
        self.x = norm_vec.x
        self.y = norm_vec.y
        self.z = norm_vec.z

    def is_normalized(self):
        """tests if the vector is normalized i.e. has length == 1."""
        length_squared = self.length_squared()
        return abs(length_squared - 1.0) < self._epsilon

    def scale_to_length(self, new_length):
        """scales the vector to a given length."""
        length = self.length()
        if length >= self._epsilon:
            new_vec = Vector3(self._x/length*new_length,
                              self._y/length*new_length,
                              self._z/length*new_length)
            self.x = new_vec.x
            self.y = new_vec.y
            self.z = new_vec.z
        else:
            raise ValueError("Cannot scale a vector with zero length")

    def reflect(self, normal):
        """returns a vector reflected around a given normal."""
        normal_vec = Vector3(normal).normalize()  # can't assume input is normalized
        dot_product = self.dot(normal_vec)
        result_vec = Vector3(self._x - 2 * normal_vec.x * dot_product,
                             self._y - 2 * normal_vec.y * dot_product,
                             self._z - 2 * normal_vec.z * dot_product)
        return result_vec

    def reflect_ip(self, normal):
        """reflect the vector around a given normal in place."""
        result_vec = self.reflect(normal)
        self.x = result_vec.x
        self.y = result_vec.y
        self.z = result_vec.z

    def distance_to(self, vec):
        """calculates the Euclidic distance to a given vector."""
        if not isinstance(vec, Vector3):
            vec = Vector3(vec)
        delta = self - vec
        return delta.length()

    def distance_squared_to(self, vec):
        """calculates the squared Euclidic distance to a given vector."""
        if not isinstance(vec, Vector3):
            vec = Vector3(vec)
        delta = self - vec
        return delta.length_squared()

    def lerp(self, vec, t):
        """returns a linear interpolation to the given vector, with t in [0..1]."""
        if t < 0 or t > 1:
            raise ValueError("Argument 't' must be in range [0, 1]")
        elif not isinstance(vec, Vector3):
            raise TypeError("Expected 'vec' to be of type Vector3")
        else:
            # check for special cases, exit early
            if t == 0:
                return self
            elif t == 1:
                return vec

            x = self._x * (1 - t) + vec.x * t
            y = self._y * (1 - t) + vec.y * t
            z = self._z * (1 - t) + vec.z * t
            return Vector3(x, y, z)

    def slerp(self, vec, t):
        """returns a spherical interpolation to the given vector, with t in [-1..1]."""
        if t < -1 or t > 1:
            raise ValueError("Argument 't' must be in range [-1, 1]")
        elif not isinstance(vec, Vector3):
            raise TypeError("Expected 'vec' to be of type Vector3")
        else:
            # check for special cases, exit early
            if t == 0:
                return self
            elif t == -1 or t == 1:
                return vec

            spherical_self = self.as_spherical()
            spherical_other = vec.as_spherical()
            if spherical_self[0] < self._epsilon or spherical_other[0] < self._epsilon:
                raise ValueError("Can't use slerp with zero vector")
            new_radius = spherical_self[0] * (1 - abs(t)) + spherical_other[0] * abs(t)
            theta_delta = (spherical_other[1] - spherical_self[1]) % 360.0
            phi_delta = (spherical_other[2] - spherical_self[2]) % 360.0
            if abs(theta_delta - 180) < self._epsilon:
                raise ValueError("Slerp with theta 180 degrees is undefined.")
            if abs(phi_delta - 180) < self._epsilon:
                raise ValueError("Slerp with phi 180 degrees is undefined.")
            if t >= 0:
                # take the shortest route
                if theta_delta > 180:
                    theta_delta -= 360
                if phi_delta > 180:
                    phi_delta -= 360
            else:
                # go the long way around
                if theta_delta < 180:
                    theta_delta = 360 - theta_delta
                if phi_delta < 180:
                    phi_delta = 360 - phi_delta
            new_theta = spherical_self[1] + theta_delta * t
            new_phi = spherical_self[2] + phi_delta * t
            result_vec = Vector3()
            result_vec.from_spherical((new_radius, new_theta, new_phi))
            return result_vec

    def elementwise(self):
        """Return object for an elementwise operation."""
        return _ElementwiseVector3Proxy(self)

    def rotate(self, angle, axis):
        """rotates a vector by a given angle in degrees around the given axis."""
        if not isinstance(axis, Vector3):
            axis = Vector3(axis)
        axis_length_sq = axis.length_squared()
        if axis_length_sq < self._epsilon:
            raise ValueError("Rotation Axis is to close to Zero")
        elif abs(axis_length_sq - 1) > self._epsilon:
            axis.normalize_ip()

        # make sure angle is in range [0, 360)
        angle = angle % 360.0

        # special-case rotation by 0, 90, 180 and 270 degrees
        if ((angle + self._epsilon) % 90.0) < 2 * self._epsilon:
            quad = int((angle + self._epsilon) / 90)
            if quad == 0 or quad == 4:  # 0 or 360 degrees
                x = self._x
                y = self._y
                z = self._z
            elif quad == 1:  # 90 degrees
                x = (self._x * (axis.x * axis.x) +
                     self._y * (axis.x * axis.y - axis.z) +
                     self._z * (axis.x * axis.z + axis.y))
                y = (self._x * (axis.x * axis.y + axis.z) +
                     self._y * (axis.y * axis.y) +
                     self._z * (axis.y * axis.z - axis.x))
                z = (self._x * (axis.x * axis.z - axis.y) +
                     self._y * (axis.y * axis.z + axis.x) +
                     self._z * (axis.z * axis.z))
            elif quad == 2:  # 180 degreees
                x = (self._x * (-1 + axis.x * axis.x * 2) +
                     self._y * (axis.x * axis.y * 2) +
                     self._z * (axis.x * axis.z * 2))
                y = (self._x * (axis.x * axis.y * 2) +
                     self._y * (-1 + axis.y * axis.y * 2) +
                     self._z * (axis.y * axis.z * 2))
                z = (self._x * (axis.x * axis.z * 2) +
                     self._y * (axis.y * axis.z * 2) +
                     self._z * (-1 + axis.z * axis.z * 2))
            elif quad == 3:  # 270 degrees
                x = (self._x * (axis.x * axis.x) +
                     self._y * (axis.x * axis.y + axis.z) +
                     self._z * (axis.x * axis.z - axis.y))
                y = (self._x * (axis.x * axis.y - axis.z) +
                     self._y * (axis.y * axis.y) +
                     self._z * (axis.y * axis.z + axis.x))
                z = (self._x * (axis.x * axis.z + axis.y) +
                     self._y * (axis.y * axis.z - axis.x) +
                     self._z * (axis.z * axis.z))
            else:
                # this should NEVER happen and means a bug in the code
                raise RuntimeError("Please report this bug in Vector3.rotate "
                                   "to the developers")
        else:
            angle_rad = _math.radians(angle)
            sin_value = _math.sin(angle_rad)
            cos_value = _math.cos(angle_rad)
            cos_complement = 1 - cos_value

            x = (self._x * (cos_value + axis.x * axis.x * cos_complement) +
                 self._y * (axis.x * axis.y * cos_complement - axis.z * sin_value) +
                 self._z * (axis.x * axis.z * cos_complement + axis.y * sin_value))
            y = (self._x * (axis.x * axis.y * cos_complement + axis.z * sin_value) +
                 self._y * (cos_value + axis.y * axis.y * cos_complement) +
                 self._z * (axis.y * axis.z * cos_complement - axis.x * sin_value))
            z = (self._x * (axis.x * axis.z * cos_complement - axis.y * sin_value) +
                 self._y * (axis.y * axis.z * cos_complement + axis.x * sin_value) +
                 self._z * (cos_value + axis.z * axis.z * cos_complement))

        return Vector3(x, y, z)

    def rotate_ip(self, angle, axis):
        """rotates the vector by a given angle in degrees around axis, in place."""
        new_vec = self.rotate(angle, axis)
        self.x = new_vec._x
        self.y = new_vec._y
        self.z = new_vec._z

    def rotate_x(self, angle):
        """rotates a vector around the x-axis by the angle in degrees."""
        y, z = _rotate_2d(self._y, self._z, angle, self._epsilon)
        return Vector3(self._x, y, z)

    def rotate_x_ip(self, angle):
        """rotates the vector around the x-axis by the angle in degrees in place."""
        new_vec = self.rotate_x(angle)
        self.x = new_vec._x
        self.y = new_vec._y
        self.z = new_vec._z

    def rotate_y(self, angle):
        """rotates a vector around the y-axis by the angle in degrees."""
        z, x = _rotate_2d(self._z, self._x, angle, self._epsilon)
        return Vector3(x, self._y, z)

    def rotate_y_ip(self, angle):
        """rotates the vector around the y-axis by the angle in degrees in place."""
        new_vec = self.rotate_y(angle)
        self.x = new_vec._x
        self.y = new_vec._y
        self.z = new_vec._z

    def rotate_z(self, angle):
        """rotates a vector around the z-axis by the angle in degrees."""
        x, y = _rotate_2d(self._x, self._y, angle, self._epsilon)
        return Vector3(x, y, self._z)

    def rotate_z_ip(self, angle):
        """rotates the vector around the z-axis by the angle in degrees in place."""
        new_vec = self.rotate_z(angle)
        self.x = new_vec._x
        self.y = new_vec._y
        self.z = new_vec._z

    def angle_to(self, vec):
        """calculates the minimum angle to a given vector in degrees."""
        if not isinstance(vec, Vector3):
            vec = Vector3(vec)
        scale = _math.sqrt(self.length_squared() * vec.length_squared())
        if scale == 0:
            raise ValueError("angle to zero vector is undefined.")
        cos_theta_rad = self.dot(vec) / scale
        theta_rad = _math.acos(cos_theta_rad)
        return _math.degrees(theta_rad)

    def as_spherical(self):
        """returns a tuple with radial distance, inclination and azimuthal angle."""
        r = self.length()
        if r == 0.0:
            return (0.0, 0.0, 0.0)
        theta = _math.degrees(_math.acos(self._z / r))
        phi = _math.degrees(_math.atan2(self._y, self._x))
        return (r, theta, phi)

    def from_spherical(self, spherical):
        """Sets x, y and z from a spherical coordinates 3-tuple."""
        if isinstance(spherical, tuple) and len(spherical) == 3:
            r = spherical[0]
            theta_rad = _math.radians(spherical[1])
            phi_rad = _math.radians(spherical[2])
            sin_theta = _math.sin(theta_rad)
            self.x = r * sin_theta * _math.cos(phi_rad)
            self.y = r * sin_theta * _math.sin(phi_rad)
            self.z = r * _math.cos(theta_rad)
        else:
            raise TypeError("Expected 3 element tuple (radius, theta, phi), but got {}"
                            .format(spherical))


class _ElementwiseVectorProxyBase(object):
    """Bases class used internally for elementwise vector operations."""

    def __radd__(self, other):
        return self.__add__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

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


class _ElementwiseVector2Proxy(_ElementwiseVectorProxyBase):
    """Class used internally for elementwise Vector2 operations."""

    def __init__(self, vector):
        self.vector = Vector2(vector)

    def __add__(self, other):
        if isinstance(other, _Number):
            return Vector2(self.vector.x + other, self.vector.y + other)
        elif isinstance(other, Vector2):
            return Vector2(self.vector.x + other.x, self.vector.y + other.y)
        elif isinstance(other, _ElementwiseVector2Proxy):
            return self.vector + other.vector
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, _Number):
            return Vector2(self.vector.x - other, self.vector.y - other)
        elif isinstance(other, Vector2):
            return Vector2(self.vector.x - other.x, self.vector.y - other.y)
        elif isinstance(other, _ElementwiseVector2Proxy):
            return self.vector - other.vector
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, _Number):
            return Vector2(other - self.vector.x, other - self.vector.y)
        elif isinstance(other, Vector2):
            return Vector2(other.x - self.vector.x, other.y - self.vector.y)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, _Number):
            return Vector2(self.vector.x * other, self.vector.y * other)
        elif isinstance(other, Vector2):
            return Vector2(self.vector.x * other.x, self.vector.y * other.y)
        elif isinstance(other, _ElementwiseVector2Proxy):
            return Vector2(self.vector.x * other.vector.x,
                           self.vector.y * other.vector.y)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, _Number):
            return Vector2(self.vector.x / other, self.vector.y / other)
        elif isinstance(other, Vector2):
            return Vector2(self.vector.x / other.x, self.vector.y / other.y)
        elif isinstance(other, _ElementwiseVector2Proxy):
            return Vector2(self.vector.x / other.vector.x,
                           self.vector.y / other.vector.y)
        return NotImplemented

    __div__ = __truediv__  # for backwards compatibility with Python 2

    def __rtruediv__(self, other):
        if isinstance(other, _Number):
            return Vector2(other / self.vector.x, other / self.vector.y)
        elif isinstance(other, Vector2):
            return Vector2(other.x / self.vector.x, other.y / self.vector.y)
        return NotImplemented

    __rdiv__ = __rtruediv__  # for backwards compatibility with Python 2

    def __floordiv__(self, other):
        if isinstance(other, _Number):
            return Vector2(self.vector.x // other, self.vector.y // other)
        elif isinstance(other, Vector2):
            return Vector2(self.vector.x // other.x, self.vector.y // other.y)
        elif isinstance(other, _ElementwiseVector2Proxy):
            return Vector2(self.vector.x // other.vector.x,
                           self.vector.y // other.vector.y)
        return NotImplemented

    def __rfloordiv__(self, other):
        if isinstance(other, _Number):
            return Vector2(other // self.vector.x, other // self.vector.y)
        elif isinstance(other, Vector2):
            return Vector2(other.x // self.vector.x, other.y // self.vector.y)
        return NotImplemented

    def __pow__(self, other):
        other_x = None
        other_y = None
        if isinstance(other, _Number):
            other_x = other_y = other
        elif isinstance(other, Vector2):
            other_x = other.x
            other_y = other.y
        elif isinstance(other, _ElementwiseVector2Proxy):
            other_x = other.vector.x
            other_y = other.vector.y
        if other_x is not None and other_y is not None:
            return Vector2(_pow_compat(self.vector.x, other_x),
                           _pow_compat(self.vector.y, other_y))
        else:
            return NotImplemented

    def __rpow__(self, other):
        other_x = None
        other_y = None
        if isinstance(other, _Number):
            other_x = other_y = other
        elif isinstance(other, Vector2):
            other_x = other.x
            other_y = other.y
        if other_x is not None and other_y is not None:
            return Vector2(_pow_compat(other_x, self.vector.x),
                           _pow_compat(other_y, self.vector.y))
        else:
            return NotImplemented

    def __mod__(self, other):
        if isinstance(other, _Number):
            return Vector2(self.vector.x % other, self.vector.y % other)
        elif isinstance(other, Vector2):
            return Vector2(self.vector.x % other.x, self.vector.y % other.y)
        elif isinstance(other, _ElementwiseVector2Proxy):
            return Vector2(self.vector.x % other.vector.x,
                           self.vector.y % other.vector.y)
        return NotImplemented

    def __rmod__(self, other):
        if isinstance(other, _Number):
            return Vector2(other % self.vector.x, other % self.vector.y)
        elif isinstance(other, Vector2):
            return Vector2(other.x % self.vector.x, other.y % self.vector.y)
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, _Number):
            dx = self.vector.x - other
            dy = self.vector.y - other
        elif isinstance(other, Vector2):
            dx = self.vector.x - other.x
            dy = self.vector.y - other.y
        elif isinstance(other, _ElementwiseVector2Proxy):
            dx = self.vector.x - other.vector.x
            dy = self.vector.y - other.vector.y
        else:
            return NotImplemented
        # Note: comparison of dx == dx and dy == dy is to check for NaN
        return (dx == dx and dy == dy and
                abs(dx) < self.vector.epsilon and
                abs(dy) < self.vector.epsilon)

    def __ne__(self, other):
        if isinstance(other, _Number):
            dx = self.vector.x - other
            dy = self.vector.y - other
        elif isinstance(other, Vector2):
            dx = self.vector.x - other.x
            dy = self.vector.y - other.y
        elif isinstance(other, _ElementwiseVector2Proxy):
            dx = self.vector.x - other.vector.x
            dy = self.vector.y - other.vector.y
        else:
            return NotImplemented
        # Note: comparison of dx != dx and dy != dy is to check for NaN
        return (dx != dx or dy != dy or
                abs(dx) >= self.vector.epsilon or
                abs(dy) >= self.vector.epsilon)

    def __gt__(self, other):
        if isinstance(other, _Number):
            return self.vector.x > other and self.vector.y > other
        elif isinstance(other, Vector2):
            return self.vector.x > other.x and self.vector.y > other.y
        elif isinstance(other, _ElementwiseVector2Proxy):
            return self.vector.x > other.vector.x and self.vector.y > other.vector.y
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, _Number):
            return self.vector.x < other and self.vector.y < other
        elif isinstance(other, Vector2):
            return self.vector.x < other.x and self.vector.y < other.y
        elif isinstance(other, _ElementwiseVector2Proxy):
            return self.vector.x < other.vector.x and self.vector.y < other.vector.y
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, _Number):
            return self.vector.x >= other and self.vector.y >= other
        elif isinstance(other, Vector2):
            return self.vector.x >= other.x and self.vector.y >= other.y
        elif isinstance(other, _ElementwiseVector2Proxy):
            return self.vector.x >= other.vector.x and self.vector.y >= other.vector.y
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, _Number):
            return self.vector.x <= other and self.vector.y <= other
        elif isinstance(other, Vector2):
            return self.vector.x <= other.x and self.vector.y <= other.y
        elif isinstance(other, _ElementwiseVector2Proxy):
            return self.vector.x <= other.vector.x and self.vector.y <= other.vector.y
        return NotImplemented

    def __abs__(self):
        return Vector2(abs(self.vector.x), abs(self.vector.y))


class _ElementwiseVector3Proxy(_ElementwiseVectorProxyBase):
    """Class used internally for elementwise Vector3 operations."""

    def __init__(self, vector):
        self.vector = Vector3(vector)

    def __add__(self, other):
        if isinstance(other, _Number):
            return Vector3(self.vector.x + other,
                           self.vector.y + other,
                           self.vector.z + other)
        elif isinstance(other, Vector3):
            return Vector3(self.vector.x + other.x,
                           self.vector.y + other.y,
                           self.vector.z + other.z)
        elif isinstance(other, _ElementwiseVector3Proxy):
            return self.vector + other.vector
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, _Number):
            return Vector3(self.vector.x - other,
                           self.vector.y - other,
                           self.vector.z - other)
        elif isinstance(other, Vector3):
            return Vector3(self.vector.x - other.x,
                           self.vector.y - other.y,
                           self.vector.z - other.z)
        elif isinstance(other, _ElementwiseVector3Proxy):
            return self.vector - other.vector
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, _Number):
            return Vector3(other - self.vector.x,
                           other - self.vector.y,
                           other - self.vector.z)
        elif isinstance(other, Vector3):
            return Vector3(other.x - self.vector.x,
                           other.y - self.vector.y,
                           other.z - self.vector.z)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, _Number):
            return Vector3(self.vector.x * other,
                           self.vector.y * other,
                           self.vector.z * other)
        elif isinstance(other, Vector3):
            return Vector3(self.vector.x * other.x,
                           self.vector.y * other.y,
                           self.vector.z * other.z)
        elif isinstance(other, _ElementwiseVector3Proxy):
            return Vector3(self.vector.x * other.vector.x,
                           self.vector.y * other.vector.y,
                           self.vector.z * other.vector.z)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, _Number):
            return Vector3(self.vector.x / other,
                           self.vector.y / other,
                           self.vector.z / other)
        elif isinstance(other, Vector3):
            return Vector3(self.vector.x / other.x,
                           self.vector.y / other.y,
                           self.vector.z / other.z)
        elif isinstance(other, _ElementwiseVector3Proxy):
            return Vector3(self.vector.x / other.vector.x,
                           self.vector.y / other.vector.y,
                           self.vector.z / other.vector.z)
        return NotImplemented

    __div__ = __truediv__  # for backwards compatibility with Python 2

    def __rtruediv__(self, other):
        if isinstance(other, _Number):
            return Vector3(other / self.vector.x,
                           other / self.vector.y,
                           other / self.vector.z)
        elif isinstance(other, Vector3):
            return Vector3(other.x / self.vector.x,
                           other.y / self.vector.y,
                           other.z / self.vector.z)
        return NotImplemented

    __rdiv__ = __rtruediv__  # for backwards compatibility with Python 2

    def __floordiv__(self, other):
        if isinstance(other, _Number):
            return Vector3(self.vector.x // other,
                           self.vector.y // other,
                           self.vector.z // other)
        elif isinstance(other, Vector3):
            return Vector3(self.vector.x // other.x,
                           self.vector.y // other.y,
                           self.vector.z // other.z)
        elif isinstance(other, _ElementwiseVector3Proxy):
            return Vector3(self.vector.x // other.vector.x,
                           self.vector.y // other.vector.y,
                           self.vector.z // other.vector.z)
        return NotImplemented

    def __rfloordiv__(self, other):
        if isinstance(other, _Number):
            return Vector3(other // self.vector.x,
                           other // self.vector.y,
                           other // self.vector.z)
        elif isinstance(other, Vector3):
            return Vector3(other.x // self.vector.x,
                           other.y // self.vector.y,
                           other.z // self.vector.z)
        return NotImplemented

    def __pow__(self, other):
        other_x = None
        other_y = None
        other_z = None
        if isinstance(other, _Number):
            other_x = other_y = other_z = other
        elif isinstance(other, Vector3):
            other_x = other.x
            other_y = other.y
            other_z = other.z
        elif isinstance(other, _ElementwiseVector3Proxy):
            other_x = other.vector.x
            other_y = other.vector.y
            other_z = other.vector.z
        if other_x is not None and other_y is not None and other_z is not None:
            return Vector3(_pow_compat(self.vector.x, other_x),
                           _pow_compat(self.vector.y, other_y),
                           _pow_compat(self.vector.z, other_z))
        else:
            return NotImplemented

    def __rpow__(self, other):
        other_x = None
        other_y = None
        other_z = None
        if isinstance(other, _Number):
            other_x = other_y = other_z = other
        elif isinstance(other, Vector3):
            other_x = other.x
            other_y = other.y
            other_z = other.z
        if other_x is not None and other_y is not None and other_z is not None:
            return Vector3(_pow_compat(other_x, self.vector.x),
                           _pow_compat(other_y, self.vector.y),
                           _pow_compat(other_z, self.vector.z))
        else:
            return NotImplemented

    def __mod__(self, other):
        if isinstance(other, _Number):
            return Vector3(self.vector.x % other,
                           self.vector.y % other,
                           self.vector.z % other)
        elif isinstance(other, Vector3):
            return Vector3(self.vector.x % other.x,
                           self.vector.y % other.y,
                           self.vector.z % other.z)
        elif isinstance(other, _ElementwiseVector3Proxy):
            return Vector3(self.vector.x % other.vector.x,
                           self.vector.y % other.vector.y,
                           self.vector.z % other.vector.z)
        return NotImplemented

    def __rmod__(self, other):
        if isinstance(other, _Number):
            return Vector3(other % self.vector.x,
                           other % self.vector.y,
                           other % self.vector.z)
        elif isinstance(other, Vector3):
            return Vector3(other.x % self.vector.x,
                           other.y % self.vector.y,
                           other.z % self.vector.z)
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, _Number):
            dx = self.vector.x - other
            dy = self.vector.y - other
            dz = self.vector.z - other
        elif isinstance(other, Vector3):
            dx = self.vector.x - other.x
            dy = self.vector.y - other.y
            dz = self.vector.z - other.z
        elif isinstance(other, _ElementwiseVector3Proxy):
            dx = self.vector.x - other.vector.x
            dy = self.vector.y - other.vector.y
            dz = self.vector.z - other.vector.z
        else:
            return NotImplemented
        # Note: comparisons like dx == dx are to check for NaN
        return (dx == dx and dy == dy and dz == dz and
                abs(dx) < self.vector.epsilon and
                abs(dy) < self.vector.epsilon and
                abs(dz) < self.vector.epsilon)

    def __ne__(self, other):
        if isinstance(other, _Number):
            dx = self.vector.x - other
            dy = self.vector.y - other
            dz = self.vector.z - other
        elif isinstance(other, Vector3):
            dx = self.vector.x - other.x
            dy = self.vector.y - other.y
            dz = self.vector.z - other.z
        elif isinstance(other, _ElementwiseVector3Proxy):
            dx = self.vector.x - other.vector.x
            dy = self.vector.y - other.vector.y
            dz = self.vector.z - other.vector.z
        else:
            return NotImplemented
        # Note: comparisons like dx != dx are to check for NaN
        return (dx != dx or dy != dy or dz != dz or
                abs(dx) >= self.vector.epsilon or
                abs(dy) >= self.vector.epsilon or
                abs(dz) >= self.vector.epsilon)

    def __gt__(self, other):
        if isinstance(other, _Number):
            return (self.vector.x > other and
                    self.vector.y > other and
                    self.vector.z > other)
        elif isinstance(other, Vector3):
            return (self.vector.x > other.x and
                    self.vector.y > other.y and
                    self.vector.z > other.z)
        elif isinstance(other, _ElementwiseVector3Proxy):
            return (self.vector.x > other.vector.x and
                    self.vector.y > other.vector.y and
                    self.vector.z > other.vector.z)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, _Number):
            return (self.vector.x < other and
                    self.vector.y < other and
                    self.vector.z < other)
        elif isinstance(other, Vector3):
            return (self.vector.x < other.x and
                    self.vector.y < other.y and
                    self.vector.z < other.z)
        elif isinstance(other, _ElementwiseVector3Proxy):
            return (self.vector.x < other.vector.x and
                    self.vector.y < other.vector.y and
                    self.vector.z < other.vector.z)
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, _Number):
            return (self.vector.x >= other and
                    self.vector.y >= other and
                    self.vector.z >= other)
        elif isinstance(other, Vector3):
            return (self.vector.x >= other.x and
                    self.vector.y >= other.y and
                    self.vector.z >= other.z)
        elif isinstance(other, _ElementwiseVector3Proxy):
            return (self.vector.x >= other.vector.x and
                    self.vector.y >= other.vector.y and
                    self.vector.z >= other.vector.z)
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, _Number):
            return (self.vector.x <= other and
                    self.vector.y <= other and
                    self.vector.z <= other)
        elif isinstance(other, Vector3):
            return (self.vector.x <= other.x and
                    self.vector.y <= other.y and
                    self.vector.z <= other.z)
        elif isinstance(other, _ElementwiseVector3Proxy):
            return (self.vector.x <= other.vector.x and
                    self.vector.y <= other.vector.y and
                    self.vector.z <= other.vector.z)
        return NotImplemented

    def __abs__(self):
        return Vector3(abs(self.vector.x),
                       abs(self.vector.y),
                       abs(self.vector.z))


def _rotate_2d(u, v, angle, epsilon):
    """Utility to rotate a 2D co-ord by a given angle in degrees.  Returns new (u, v)"""
    # make sure angle is in range [0, 360)
    angle = angle % 360.0

    # special-case rotation by 0, 90, 180 and 270 degrees
    if ((angle + epsilon) % 90.0) < 2 * epsilon:
        quad = int((angle + epsilon) / 90)
        if quad == 0 or quad == 4:  # 0 or 360 degrees
            u_new = u
            v_new = v
        elif quad == 1:  # 90 degrees
            u_new = -v
            v_new = u
        elif quad == 2:  # 180 degreees
            u_new = -u
            v_new = -v
        elif quad == 3:  # 270 degrees
            u_new = v
            v_new = -u
        else:
            # this should NEVER happen and means a bug in the code
            raise RuntimeError("Please report this bug in _rotate_2d "
                               "to the developers")
    else:
        angle_rad = _math.radians(angle)
        sin_value = _math.sin(angle_rad)
        cos_value = _math.cos(angle_rad)
        u_new = cos_value * u - sin_value * v
        v_new = sin_value * u + cos_value * v

    return (u_new, v_new)
