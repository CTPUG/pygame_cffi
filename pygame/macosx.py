import os
import sys

from _macosx_c import ffi
from _macosx_c import lib as sdlmain_osx

try:
    import MacOS
except:
    MacOS = None


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
