"""
Module for the rectangle object
"""

from pygame._sdl import ffi

class Rect(object):

   def __init__(self, *args):
      if len(args) == 1 and isintance(args[0], Rect):
          # Copy the rect parameters
          self._sdlrect = other._sdlrect
      elif len(args) == 4:
          self._sdlrect = new_rect(*args)
      elif len(args) == 2:
          if not isinstance(args[0], tuple) or len(args[0]) != 2:
              raise TypeError("Argument must be rect style object")
          if not isinstance(args[1], tuple) or len(args[1]) != 2:
              raise TypeError("Argument must be rect style object")
          self._sdlrect = new_rect(args[0][0], args[0][1],
                                   args[1][0], args[1][1])


def new_rect(x, y, w, h):
    sdlrect = ffi.new('SDL_Rect*')
    sdlrect.x = x
    sdlrect.y = y
    sdlrect.w = w
    sdlrect.h = h
    return sdlrect
