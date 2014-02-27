"""pygame module with software blit functions"""

from pygame._error import SDLError
from pygame._sdl import sdl, ffi
from pygame.surflock import locked


class BlitInfo(object):
    def __init__(self, width, height, s_pixels, s_pxskip,
                 s_skip, d_pixels, d_pxskip, d_skip,
                 src, dst, src_flags, dst_flags):
        self.width = width
        self.height = height
        self.s_pixels = s_pixels
        self.s_pxskip = s_pxskip
        self.s_skip = s_skip
        self.d_pixels = d_pxskip
        self.d_skip = d_skip
        self.src = src
        self.dst = dst
        self.src_flags = src_flags
        self.dst_flags = dst_flags


def soft_blit(src, srcrect, dst, dstrect, flags):
    # don't want code to be deeply nested
    dst_lock = locked(dst)
    src_lock = locked(src)
    dst_lock.__enter__()
    src_lock.__enter__()

    s_pixels = ffi.cast('uint8_t*', src.pixels)
    s_pixels = s_pixels[src.offset +
                        ffi.cast('uint16_t', srcrect.y) * src.pitch +
                        ffi.cast('uint16_t', srcrect.x) * src.format.BytesPerPixel]
    d_pixels = ffi.cast('uint8_t*', dst.pixels)
    d_pixels = d_pixels[dst.offset +
                        ffi.cast('uint16_t', dstrect.y) * dst.pitch +
                        ffi.cast('uint16_t', dstrect.x) * src.format.BytesPerPixel]
    info = BlitInfo(
        srcrect.w, srcrect.h,
        s_pixels, src.format.BytesPerPixel,
        src.pitch - srcrect.w * src.format.BytesPerPixel,
        d_pixels, dst.format.BytesPerPixel,
        dst.pitch - srcrect.width * dst.format.BytesPerPixel,
        src.format, dst.format, src.flags, dst.flags
    )

    if info.d_pixels > info.s_pixels:
        span = info.width * info.src.BytesPerPixel
        pass

    src_lock.__exit__()
    dst_lock.__exit__()

def blit():
    pass


def alphablit():
    pass