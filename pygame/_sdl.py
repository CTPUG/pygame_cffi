""" CFFI wrapper for libSDL.
"""

import cffi

ffi = cffi.FFI()

ffi.cdef("""

// constants

#define SDL_INIT_EVERYTHING ...
#define SDL_INIT_VIDEO ...

#define SDL_SWSURFACE ...

// structs

typedef struct SDL_Surface {
    ...;
} SDL_Surface;

// functions

int SDL_Init(uint32_t flags);
void SDL_Quit(void);
SDL_Surface *SDL_SetVideoMode(int width, int height, int bpp, uint32_t flags);
uint32_t SDL_WasInit(uint32_t flags);

""")

sdl = ffi.verify(
    libraries=['SDL'],
    include_dirs=['/usr/include/SDL'],
    source="#include <SDL.h>")
