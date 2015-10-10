import os
import sys

from pygame._macosx_c import ffi
from pygame._macosx_c import lib as sdlmain_osx

try:
    from MacOS import WMAvailable
except ImportError:
    def WMAvailable():
        if sdlmain_osx.CGMainDisplayID() == 0:
            return False
        psn = ffi.new("ProcessSerialNumber[1]")
        if (sdlmain_osx.GetCurrentProcess(psn) < 0 or
            sdlmain_osx.SetFrontProcess(psn) < 0):
            return False
        return True

def pre_video_init():
    """Do a bunch of OSX display initialisation magic.
    """

    if not WMAvailable():
        errstr = sdlmain_osx.WMEnable()
        if errstr != ffi.NULL:
            raise Exception(ffi.string(errstr))

    if not sdlmain_osx.RunningFromBundleWithNSApplication():
        # TODO: default icon thing.
        sdlmain_osx.InstallNSApplication()

    if (os.getcwd() == '/') and len(sys.argv) > 1:
        os.chdir(os.path.dirname(sys.argv[0]))
