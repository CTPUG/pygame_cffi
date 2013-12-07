import os
import sys

try:
    import MacOS
except:
    MacOS = None

import cffi


ffi = cffi.FFI()
ffi.cdef("""
const char* WMEnable(void);
int RunningFromBundleWithNSApplication(void);
int InstallNSApplication(void);
""")

sdlmain_osx = ffi.verify(
    libraries=['SDL', 'sdlmain_osx'],
    library_dirs=[os.path.dirname(__file__)],
    include_dirs=[
        '/usr/local/include/SDL',
        '/usr/include/SDL',
        os.path.dirname(__file__),
    ],
    source='#include "sdlmain_osx.h"')


def pre_video_init():
    """Do a bunch of OSX display initialisation magic.
    """

    if MacOS and not MacOS.WMAvailable():
        errstr = sdlmain_osx.WMEnable()
        if errstr != ffi.NULL:
            raise Exception(ffi.string(errstr))

    if not sdlmain_osx.RunningFromBundleWithNSApplication():
        # TODO: default icon thing.
        sdlmain_osx.InstallNSApplication()

    if (os.getcwd() == '/') and len(sys.argv) > 1:
        os.chdir(os.path.dirname(sys.argv[0]))
