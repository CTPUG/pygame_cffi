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
