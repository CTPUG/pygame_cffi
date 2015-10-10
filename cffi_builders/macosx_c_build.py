import os

import cffi


def _get_c_lib(name):
    """Return the contents of a C library."""
    filename = os.path.join(
        os.path.dirname(__file__), 'lib', name)
    with open(filename) as lib:
        return lib.read()


ffi = cffi.FFI()
ffi.cdef("""
typedef struct ProcessSerialNumber {
   ...;
} ProcessSerialNumber;

const char* WMEnable(void);
int CGMainDisplayID(void);
int GetCurrentProcess(ProcessSerialNumber*);
int SetFrontProcess(ProcessSerialNumber*);
int RunningFromBundleWithNSApplication(void);
int InstallNSApplication(void);
""")


sdlmain_osx = ffi.set_source(
    "pygame._macosx_c",
    libraries=['SDL', 'objc'],
    include_dirs=[
        '/usr/include/SDL',
        '/usr/local/include/SDL',
    ],
    extra_link_args=["-framework", "Cocoa"],
    source=_get_c_lib("sdlmain_osx.m"),
    source_extension=".m")


if __name__ == "__main__":
    ffi.compile()
