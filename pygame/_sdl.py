""" CFFI wrapper for libSDL.
"""

import cffi

ffi = cffi.FFI()

ffi.cdef("""
int SDL_Init(uint32_t flags);
void SDL_Quit(void);
""")

ffi.verify(source="""
#include <SDL.h>
""",
libraries=['SDL'],
include_dirs=['/usr/include/SDL'])
