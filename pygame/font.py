""" The pygame font module """

from pygame._sdl import sdl, ffi
from pygame._error import SDLError
from pygame.color import Color
from pygame.surface import Surface
from pygame.pkgdata import getResource

# SDL doesn't stop multiple calls to TTF_Init, so we need to track
# our own status to ensure we don't accidently call TTF_Quit on a
# TTF_Init called outside our control.
_font_initialised = 0

_font_defaultname = "freesansbold.ttf"


def init():
    """pygame.font.init(): return None
       initialize the font module"""
    global _font_initialised
    if _font_initialised == 0:
        res = sdl.TTF_Init()
        if res == -1:
            raise SDLError.from_sdl_error()
        _font_initialised += 1


def get_init():
    """pygame.font.get_init(): return bool

       true if the font module is initialized"""
    return _font_initialised > 0


def quit():
    """pygame.font.quit(): return None
       uninitialize the font module"""
    if _font_initialised:
        sdl.TTF_Quit()


def check_font():
    """Helper function to test if the font module was initialised
       and raises an error if not"""
    if not get_init():
        raise SDLError("font not initialized")


class Font(object):
    """ pygame.font.Font(filename, size): return Font
        pygame.font.Font(object, size): return Font

        create a new Font object from a file"""

    def __init__(self, font, fontsize):
        check_font()
        if not isinstance(fontsize, int):
            raise TypeError("expected an integer, but got %r" % type(fontsize))

        if font is None or font == _font_defaultname:
            f = getResource(_font_defaultname)
            # Scaling as from pygame/src/font.c
            fontsize = int(fontsize * 0.6875)
            # XXX: Hackery until we add in conversion between file objects
            # and SDL RWops
            font = f.name
            f.close()
        if fontsize < 1:
            fontsize = 1
        if isinstance(font, basestring):
            # According to the pygame comments, we need to ensure the
            # file exists and is readable before calling out to SDL
            f = open(font, 'r')
            # pygame raises IOError if this fails, so we don't catch the
            # exception
            f.close()
            self._sdl_font = sdl.TTF_OpenFont(font, fontsize)
            if not self._sdl_font:
                raise SDLError.from_sdl_error()

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

    def size(self, text):
        """Font.size(text): return (width, height)
           determine the amount of space needed to render text"""
        if not isinstance(text, basestring):
            raise TypeError("text must be a string or unicode")
        w = ffi.new("int*")
        h = ffi.new("int*")
        ecode = sdl.TTF_SizeUTF8(self._sdl_font, text, w, h)
        if ecode == -1:
            raise SDLError.from_sdl_error()

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
            except ValueError:
                # Same error behaviour as pygame
                bg[0].r = 0
                bg[0].g = 0
                bg[0].b = 0
        else:
            bg[0].r = 0
            bg[0].g = 0
            bg[0].b = 0

        if not text:
            # Just return a surface of width 1 x font height
            height = sdl.TTF_FontHeight(self._sdl_font)
            surf = Surface((1, height))
            if background and isinstance(background, Color):
                surf.full(background)
            return surf
        if not isinstance(text, basestring):
            raise TypeError("text must be a string or unicode")
        if isinstance(text, unicode):
            text = text.encode('utf-8', 'replace')
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
        # XXX: We skip the transparency fiddling for now
        if not sdl_surf:
            raise SDLError.from_sdl_error()
        return Surface._from_sdl_surface(sdl_surf)
