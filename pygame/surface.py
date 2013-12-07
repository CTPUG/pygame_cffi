""" XXX """

from pygame.error import SDLError, unpack_rect


class Surface(object):
    """ Surface((width, height), flags=0, depth=0, masks=None) -> Surface
    Surface((width, height), flags=0, Surface) -> Surface

    pygame object for representing images
    """
    def __init__(self, size, flags=0, depth=0, masks=None):
        w, h = unpack_rect(size)
        if isinstance(depth, Surface):
            surface = depth
            depth = 0
        else:
            surface = None

        if depth or masks:
            raise SDLError("XXX: Not implemented!")

    @classmethod
    def _from_sdl_surface(cls, c_surface):
        surface = cls.__new__(cls)
        surface._c_surface = c_surface
        return surface
