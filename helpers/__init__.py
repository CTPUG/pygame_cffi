import os
import sys
import platform

# Various helpers for the build scripts

def get_lib_dir():
    """Return the library path for SDL and other libraries.

       Assumes we're using the pygame prebuilt zipfile on windows"""
    if sys.platform.startswith("win"):
        if platform.architecture()[0] == '32bit':
            # 32 bit
            return ['prebuilt-x86/lib']
        else:
            # 64 bit
            return ['prebuilt-x64/lib']
    return ['/usr/lib','/usr/local/lib']


def get_inc_dir():
    """Return the include directories for the SDL and other libraries.

       Assumes we're using the pygame prebuilt zipfile on windows"""
    if sys.platform.startswith("win"):
        if platform.architecture()[0] == '32bit':
            # 32 bit
            return ['prebuilt-x86/include', 'prebuilt-x86/include/SDL']
        else:
            return ['prebuilt-x64/include', 'prebuilt-x64/include/SDL']
    return ['/usr/include', '/usr/include/SDL', '/usr/local/include/SDL']


def get_c_lib(name):
    """Return the contents of a C library."""
    filename = os.path.join(
        os.path.dirname(__file__), '..', 'cffi_builders', 'lib', name)
    with open(filename) as lib:
        return lib.read()


__all__ = [get_inc_dir, get_lib_dir, get_c_lib]
