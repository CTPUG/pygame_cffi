# pygame_cffi - a cffi implementation of the pygame library
# Copyright (C) 2015  Stefano Rivera
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

"""Python 2.x/3.x compatibility tools"""

import sys

__all__ = ['geterror', 'long_', 'string_types', 'xrange_', 'ord_',
           'unichr_', 'unicode_', 'raw_input_']

def geterror ():
    return sys.exc_info()[1]

try:
    long_ = long
except NameError:
    long_ = int

try:
    xrange_ = xrange
except NameError:
    xrange_ = range

def get_BytesIO():
    try:
        from cStringIO import StringIO as BytesIO
    except ImportError:
        from io import BytesIO
    return BytesIO

def get_StringIO():
    try:
        from cStringIO import StringIO
    except ImportError:
        from io import StringIO
    return StringIO

def ord_(o):
    try:
        return ord(o)
    except TypeError:
        return o

if sys.version_info >= (3, 0, 0):
    def chr_(o):
        return bytes((o,))
else:
    chr_ = chr

try:
    unichr_ = unichr
except NameError:
    unichr_ = chr

try:
    unicode_ = unicode
except NameError:
    unicode_ = str

try:
    bytes_ = bytes
except NameError:
    bytes_ = str

try:
    string_types = basestring
except NameError:
    string_types = str

try:
    raw_input_ = raw_input
except NameError:
    raw_input_ = input

if sys.platform == 'win32':
    filesystem_errors = "replace"
elif sys.version_info >= (3, 0, 0):
    filesystem_errors = "surrogateescape"
else:
    filesystem_errors = "strict"

def filesystem_encode(u):
    return u.encode(sys.getfilesystemencoding(), filesystem_errors)

# Include a next compatible function for Python versions < 2.6
try:
    next_ = next
except NameError:
    def next_(i, *args):
        try:
            return i.next()
        except StopIteration:
            if args:
                return args[0]
            raise

# itertools.imap is missing in 3.x
try:
    import itertools.imap as imap_
except ImportError:
    imap_ = map


# The behaviour of the power operator, '**' and built-in pow() function,
# changed in Python 3.x.  In Python 3.x raising a negative number to a
# fractional power results in a complex number, while in earlier versions
# it raised a ValueError.  Matching the behaviour of pygame requires
# the ValueError instead of a complex result.  The compatibility function
# defined below is provided for this purpose.
try:
    (-2.2) ** 1.1

    def pow_compat(x, y):
        """Return x ** y, with Python 2.x compatible exceptions."""
        if x < 0 and not float(y).is_integer():
            raise ValueError("negative number cannot be raised to a fractional power")
        else:
            return x ** y

except ValueError:

    def pow_compat(x, y):
        """Return x ** y, with Python 2.x compatible exceptions."""
        return x ** y
