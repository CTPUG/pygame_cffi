""" The pygame font module """

import os
import sys

from pygame._sdl import sdl, ffi
from pygame._error import SDLError
from pygame.base import register_quit
from pygame.color import Color
from pygame.pkgdata import getResource
from pygame.rwobject import (rwops_from_file, rwops_encode_file_path,
                             rwops_from_file_path)
from pygame.surface import Surface
from pygame.sysfont import get_fonts, match_font, SysFont

# SDL doesn't stop multiple calls to TTF_Init, so we need to track
# our own status to ensure we don't accidently call TTF_Quit on a
# TTF_Init called outside our control.
_font_initialised = 0

_font_defaultname = "freesansbold.ttf"


if sys.maxunicode == 1114111:
    def is_ucs_2(ch):
        return ord(ch) < 0x10000L
else:
    def is_ucs_2(ch):
        return True


def utf_8_needs_UCS_4(text):
    first = ord('\xF0')
    for ch in text:
        if ord(ch) >= first:
            return True
    return False


def autoinit():
    global _font_initialised
    if not _font_initialised:
        register_quit(autoquit)
        if sdl.TTF_Init():
            return False
        _font_initialised = 1
    return bool(_font_initialised)


def autoquit():
    global _font_initialised
    if _font_initialised:
        _font_initialised = 0
        sdl.TTF_Quit()


def init():
    """pygame.font.init(): return None
       initialize the font module"""
    if not autoinit():
        raise SDLError.from_sdl_error()


def get_init():
    """pygame.font.get_init(): return bool

       true if the font module is initialized"""
    return _font_initialised > 0


def quit():
    """pygame.font.quit(): return None
       uninitialize the font module"""
    autoquit()


def check_font():
    """Helper function to test if the font module was initialised
       and raises an error if not"""
    if not get_init():
        raise SDLError("font not initialized")


def get_default_font():
    """ get_default_font() -> string
    get the filename of the default font
    """
    return _font_defaultname


class Font(object):
    """ pygame.font.Font(filename, size): return Font
        pygame.font.Font(object, size): return Font

        create a new Font object from a file"""

    _sdl_font = None
    _font_file = None

    def __init__(self, font, fontsize):
        check_font()
        if not isinstance(fontsize, int):
            raise TypeError("expected an integer, but got %r" % type(fontsize))

        if fontsize < 1:
            fontsize = 1

        file_obj = None
        if font is None or font == _font_defaultname:
            file_obj = getResource(_font_defaultname)
            self._font_file = file_obj
            # Scaling as from pygame/src/font.c
            fontsize = int(fontsize * 0.6875)
            if fontsize < 1:
                fontsize = 1
        elif isinstance(font, basestring):
            filepath = rwops_encode_file_path(font)
            # According to the pygame comments, we need to ensure the
            # file exists and is readable before calling out to SDL
            f = open(filepath, 'r')
            # pygame raises IOError if this fails, so we don't catch the
            # exception
            f.close()
            self._sdl_font = sdl.TTF_OpenFont(filepath, fontsize)
        else:
            file_obj = font

        if file_obj:
            # Get a new handle on the file to load the font from.
            # Otherwise, if the file handle is closed elsewhere, font
            # rendering will segfault.
            if self._font_file is None:
                file_obj = open(os.path.abspath(file_obj.name))
                self._font_file = file_obj

            rwops = rwops_from_file(file_obj)
            self._sdl_font = sdl.TTF_OpenFontRW(rwops, 1, fontsize)

        if not self._sdl_font:
            raise SDLError.from_sdl_error()

    def __del__(self):
        if _font_initialised and self._sdl_font:
            sdl.TTF_CloseFont(self._sdl_font)
        if self._font_file:
            self._font_file.close()
        self._font_file = None
        self._sdl_font = None

    def set_bold(self, bold):
        """Font.set_bold(bool): return None
           enable fake rendering of bold text"""
        style = sdl.TTF_GetFontStyle(self._sdl_font)
        if bold:
            style = style | sdl.TTF_STYLE_BOLD
        elif style & sdl.TTF_STYLE_BOLD:
            style = style ^ sdl.TTF_STYLE_BOLD
        sdl.TTF_SetFontStyle(self._sdl_font, style)

    def get_bold(self):
        """Font.get_bold(): return bool
           check if text will be rendered bold"""
        style = sdl.TTF_GetFontStyle(self._sdl_font)
        return style & sdl.TTF_STYLE_BOLD != 0

    def set_underline(self, underline):
        """Font.set_underline(bool): return None
           control if text is rendered with an underline"""
        style = sdl.TTF_GetFontStyle(self._sdl_font)
        if underline:
            style = style | sdl.TTF_STYLE_UNDERLINE
        elif style & sdl.TTF_STYLE_UNDERLINE:
            style = style ^ sdl.TTF_STYLE_UNDERLINE
        sdl.TTF_SetFontStyle(self._sdl_font, style)

    def get_underline(self):
        """Font.get_underline(): return bool
           check if text will be rendered with an underline"""
        style = sdl.TTF_GetFontStyle(self._sdl_font)
        return style & sdl.TTF_STYLE_UNDERLINE != 0

    def set_italic(self, italic):
        """Font.set_italic(bool): return None
           enable fake rendering of italic text"""
        style = sdl.TTF_GetFontStyle(self._sdl_font)
        if italic:
            style = style | sdl.TTF_STYLE_ITALIC
        elif style & sdl.TTF_STYLE_ITALIC:
            style = style ^ sdl.TTF_STYLE_ITALIC
        sdl.TTF_SetFontStyle(self._sdl_font, style)

    def get_italic(self):
        """Font.get_italic(): return bool
           check if text will be rendered italic"""
        style = sdl.TTF_GetFontStyle(self._sdl_font)
        return style & sdl.TTF_STYLE_ITALIC != 0

    def metrics(self, text):
        """ metrics(text) -> list
        Gets the metrics for each character in the pased string.
        """
        if not isinstance(text, basestring):
            raise TypeError("text must be a string or unicode")
        text = unicode(text)
        results = []
        minx, maxx, miny, maxy, advance = [ffi.new('int*') for i in range(5)]
        for i, ch in enumerate(text):
            if is_ucs_2(ch) and not \
                    sdl.TTF_GlyphMetrics(self._sdl_font, ord(ch),
                                         minx, maxx, miny, maxy,
                                         advance):
                results.append((minx[0], maxx[0], miny[0],
                                maxy[0], advance[0]))
            else:
                results.append(None)
        return results

    def get_linesize(self):
        """ get_linesize() -> int
        get the line space of the font text
        """
        return sdl.TTF_FontLineSkip(self._sdl_font)

    def get_height(self):
        """ get_height() -> int
        get the height of the font
        """
        return sdl.TTF_FontHeight(self._sdl_font)

    def get_ascent(self):
        """ get_ascent() -> int
        get the ascent of the font
        """
        return sdl.TTF_FontAscent(self._sdl_font)

    def get_descent(self):
        """ get_descent() -> int
        get the descent of the font
        """
        return sdl.TTF_FontDescent(self._sdl_font)

    def size(self, text):
        """Font.size(text): return (width, height)
           determine the amount of space needed to render text"""
        if not isinstance(text, basestring):
            raise TypeError("text must be a string or unicode")
        if isinstance(text, unicode):
            text = text.encode('utf-8', 'replace')
        w = ffi.new("int*")
        h = ffi.new("int*")
        ecode = sdl.TTF_SizeUTF8(self._sdl_font, text, w, h)
        if ecode == -1:
            raise SDLError(ffi.string(sdl.TTF_GetError()))

        return int(w[0]), int(h[0])

    def render(self, text, antialias, color, background=None):
        """Font.render(text, antialias, color, background=None): return Surface
           draw text on a new Surface"""
        color = Color(color)
        fg = ffi.new("SDL_Color [1]")
        bg = ffi.new("SDL_Color [1]")
        fg[0].r = color.r
        fg[0].g = color.g
        fg[0].b = color.b
        if background:
            try:
                background = Color(background)
                bg[0].r = background.r
                bg[0].g = background.g
                bg[0].b = background.b
            except (TypeError, ValueError):
                # Same error behaviour as pygame
                bg[0].r = 0
                bg[0].g = 0
                bg[0].b = 0
        else:
            bg[0].r = 0
            bg[0].g = 0
            bg[0].b = 0

        if text is None or text == '':
            # Just return a surface of width 1 x font height
            height = sdl.TTF_FontHeight(self._sdl_font)
            surf = Surface((1, height))
            if background and isinstance(background, Color):
                surf.fill(background)
            else:
                # clear the colorkey
                surf.set_colorkey(flags=sdl.SDL_SRCCOLORKEY)
            return surf

        if not isinstance(text, basestring):
            raise TypeError("text must be a string or unicode")
        if '\x00' in text:
            raise ValueError("A null character was found in the text")
        if isinstance(text, unicode):
            text = text.encode('utf-8', 'replace')
            if utf_8_needs_UCS_4(text):
                raise UnicodeError("A Unicode character above '\\uFFFF' was found;"
                                   " not supported")
        if antialias:
            if background is None:
                sdl_surf = sdl.TTF_RenderUTF8_Blended(self._sdl_font,
                                                      text, fg[0])
            else:
                sdl_surf = sdl.TTF_RenderUTF8_Shaded(self._sdl_font,
                                                     text, fg[0], bg[0])
        else:
            sdl_surf = sdl.TTF_RenderUTF8_Solid(self._sdl_font,
                                                 text, fg[0])
        if not sdl_surf:
            raise SDLError(ffi.string(sdl.TTF_GetError()))
        surf = Surface._from_sdl_surface(sdl_surf)
        if not antialias and background is not None:
            surf.set_colorkey()
            surf.set_palette([(bg[0].r, bg[0].g, bg[0].b)])
        return surf


# for ftfont to be used as drop-in replacement
FontType = Font
