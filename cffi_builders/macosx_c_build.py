import os

import cffi


ffi = cffi.FFI()
ffi.cdef("""
const char* WMEnable(void);
int RunningFromBundleWithNSApplication(void);
int InstallNSApplication(void);
""")


sdlmain_osx = ffi.set_source(
    "pygame._macosx_c",
    libraries=['SDL', 'sdlmain_osx'],
    library_dirs=[os.path.dirname(__file__)],
    include_dirs=[
        '/usr/local/include/SDL',
        '/usr/include/SDL',
        os.path.join(os.path.dirname(__file__), 'lib'),
    ],
    source='#include "sdlmain_osx.h"')


if __name__ == "__main__":
    ffi.compile()
