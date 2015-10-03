# Implement the pygame API for the bitmask functions

from pygame._sdl import sdl, ffi


class Mask(object):
    """pygame.Mask((width, height)): return Mask

       pygame object for representing 2d bitmask"""

    def __init__(self, size):
        pass

    def angle(self):
        """angle() -> theta

           Returns the orientation of the pixels"""
        pass

    def centroid(self):
        """centroid() -> (x, y)

           Returns the centroid of the pixels in a Mask"""
        pass

    def clear(self):
        """clear() -> None

        Sets all bits to 0"""
        pass

    def connected_component(self, pos=None):
        """connected_component((x,y) = None) -> Mask

        Returns a mask of a connected region of pixels."""
        pass

    def connected_components(self, min=0):
        """connected_components(min = 0) -> [Masks]

           Returns a list of masks of connected regions of pixels."""
        pass

    def convolve(self, othermask, outputmask=None, offset=(0, 0)):
        """convolve(othermask, outputmask = None, offset = (0,0)) -> Mask

           Return the convolution of self with another mask."""
        pass

    def count(self):
        """count() -> pixels

        Returns the number of set pixels"""
        pass

    def draw(self, othermask, offset):
        """draw(othermask, offset) -> None

           Draws a mask onto another"""
        pass

    def erase(self, othermask, offset):
        """erase(othermask, offset) -> None

        Erases a mask from another"""
        pass

    def fill(self):
        """fill() -> None

           Sets all bits to 1"""
        pass

    def get_at(self, pos):
        """get_at((x,y)) -> int

           Returns nonzero if the bit at (x,y) is set."""
        pass

    def get_bounding_rects(self):
        """get_bounding_rects() -> Rects

           Returns a list of bounding rects of regions of set pixels."""
        pass

    def get_size(self):
        """get_size() -> width,height

           Returns the size of the mask."""
        pass

    def invert(self):
        """invert() -> None

           Flips the bits in a Mask"""
        pass

    def outline(self, every=1):
        """outline(every = 1) -> [(x,y), (x,y) ...]

           list of points outlining an object"""
        pass

    def overlap(self, offset):
        """overlap(othermask, offset) -> x,y

           Returns the point of intersection if the masks overlap with
           the given offset - or None if it does not overlap."""
        pass

    def overlap_area(self, othermask, offest):
        """overlap_area(othermask, offset) -> numpixels

           Returns the number of overlapping 'pixels'."""
        pass

    def overlap_mask(self, othermask, offset):
        """overlap_mask(othermask, offset) -> Mask

            Returns a mask of the overlapping pixels"""
        pass

    def scale(self, new_size):
        """scale((x, y)) -> Mask

        Resizes a mask"""
        pass

    def set_at(self, pos, value):
        """ set_at((x,y),value) -> None

        Sets the position in the mask given by x and y."""
        pass


def from_surface(Surface, threshold=127):
    """from_surface(Surface, threshold = 127) -> Mask

       Returns a Mask from the given surface"""

    pass

def from_threshold(Surface, color, threshold=(0, 0, 0, 255), othersurface=None, palette_colors=1):
    """from_threshold(Surface, color, threshold = (0,0,0,255), othersurface = None, palette_colors = 1) -> Mask

        Creates a mask by thresholding Surfaces"""
    pass
