
import platform

import cffi

ffi = cffi.FFI()

ffi.cdef("""

// base types

typedef uint32_t Uint32;
typedef uint8_t Uint8;

// constants

#define SDL_INIT_EVERYTHING ...
#define SDL_INIT_TIMER ...
#define SDL_INIT_VIDEO ...
#define SDL_INIT_AUDIO ...
#define SDL_INIT_NOPARACHUTE ...

#define SDL_APPACTIVE ...

#define SDL_SWSURFACE ...
#define SDL_ANYFORMAT ...

#define SDL_ALLEVENTS ...

#define SDL_SWSURFACE ...
#define SDL_HWSURFACE ...

#define SDL_RLEACCEL ...
#define SDL_RLEACCELOK ...

#define SDL_HAT_UP ...
#define SDL_HAT_DOWN ...
#define SDL_HAT_RIGHT ...
#define SDL_HAT_LEFT ...

#define SDL_SRCALPHA ...
#define SDL_SRCCOLORKEY ...

#define SDL_FULLSCREEN ...

#define SDL_QUERY ...
#define SDL_IGNORE ...
#define SDL_DISABLE ...
#define SDL_ENABLE ...

#define SDL_PHYSPAL ...

#define SDL_BYTEORDER ...
#define SDL_LIL_ENDIAN ...

// OpenGL constants

#define SDL_OPENGL ...

// enums

typedef enum {
    SDL_FALSE = 0,
    SDL_TRUE  = 1
} SDL_bool;

typedef enum {
    SDL_GL_RED_SIZE,
    SDL_GL_GREEN_SIZE,
    SDL_GL_BLUE_SIZE,
    SDL_GL_ALPHA_SIZE,
    SDL_GL_BUFFER_SIZE,
    SDL_GL_DOUBLEBUFFER,
    SDL_GL_DEPTH_SIZE,
    SDL_GL_STENCIL_SIZE,
    SDL_GL_ACCUM_RED_SIZE,
    SDL_GL_ACCUM_GREEN_SIZE,
    SDL_GL_ACCUM_BLUE_SIZE,
    SDL_GL_ACCUM_ALPHA_SIZE,
    SDL_GL_STEREO,
    SDL_GL_MULTISAMPLEBUFFERS,
    SDL_GL_MULTISAMPLESAMPLES,
    SDL_GL_ACCELERATED_VISUAL,
    SDL_GL_SWAP_CONTROL
} SDL_GLattr;

// NOTE: The full definitions of the following key enums are in _sdl_keys.py.
//       They take many long seconds to build and they don't change at all, so
//       having them in a separate FFI unit makes startup faster when we've
//       changed the cdef and have to rebuild.
typedef enum {
    SDLK_UNKNOWN,
    SDLK_LAST,
    ...
} SDLKey;

typedef enum {
    KMOD_NONE,
    KMOD_RESERVED,
    ...
} SDLMod;

// structs

typedef struct SDL_Rect {
    int16_t x, y;
    uint16_t w, h;
} SDL_Rect;

typedef struct SDL_Color {
   uint8_t r;
   uint8_t b;
   uint8_t g;
   ...;
} SDL_Color;

typedef struct{
    int ncolors;
    SDL_Color *colors;
} SDL_Palette;

typedef struct SDL_PixelFormat {
    SDL_Palette *palette;
    uint8_t BitsPerPixel;
    uint8_t BytesPerPixel;
    uint8_t Rloss, Gloss, Bloss, Aloss;
    uint8_t Rshift, Gshift, Bshift, Ashift;
    uint32_t Rmask, Gmask, Bmask, Amask;
    uint32_t colorkey;
    uint8_t alpha;
} SDL_PixelFormat;

typedef struct SDL_Surface {
    SDL_PixelFormat* format;
    int w, h;
    void *pixels;
    uint16_t pitch;
    uint32_t flags;
    ...;
} SDL_Surface;

typedef struct SDL_keysym {
    uint8_t scancode;    /**< hardware specific scancode */
    SDLKey sym;      /**< SDL virtual keysym */
    SDLMod mod;      /**< current key modifiers */
    uint16_t unicode;  /**< translated character */
} SDL_keysym;

typedef struct SDL_ActiveEvent {
    uint8_t type;       /**< SDL_ACTIVEEVENT */
    uint8_t gain;       /**< Whether given states were gained or lost (1/0) */
    uint8_t state;      /**< A mask of the focus states */
} SDL_ActiveEvent;

/** Keyboard event structure */
typedef struct SDL_KeyboardEvent {
    uint8_t type;       /**< SDL_KEYDOWN or SDL_KEYUP */
    uint8_t which;      /**< The keyboard device index */
    uint8_t state;      /**< SDL_PRESSED or SDL_RELEASED */
    SDL_keysym keysym;
} SDL_KeyboardEvent;

/** Mouse motion event structure */
typedef struct SDL_MouseMotionEvent {
    uint8_t type;	/**< SDL_MOUSEMOTION */
    uint8_t which;	/**< The mouse device index */
    uint8_t state;	/**< The current button state */
    uint16_t x, y;	/**< The X/Y coordinates of the mouse */
    int16_t xrel;	/**< The relative motion in the X direction */
    int16_t yrel;	/**< The relative motion in the Y direction */
} SDL_MouseMotionEvent;

/** Mouse button event structure */
typedef struct SDL_MouseButtonEvent {
    uint8_t type;	/**< SDL_MOUSEBUTTONDOWN or SDL_MOUSEBUTTONUP */
    uint8_t which;	/**< The mouse device index */
    uint8_t button;	/**< The mouse button index */
    uint8_t state;	/**< SDL_PRESSED or SDL_RELEASED */
    uint16_t x, y;	/**< The X/Y coordinates of the mouse at press time */
} SDL_MouseButtonEvent;

/** Joystick axis motion event structure */
typedef struct SDL_JoyAxisEvent {
    uint8_t type;	/**< SDL_JOYAXISMOTION */
    uint8_t which;	/**< The joystick device index */
    uint8_t axis;	/**< The joystick axis index */
    int16_t value;	/**< The axis value (range: -32768 to 32767) */
} SDL_JoyAxisEvent;

/** Joystick trackball motion event structure */
typedef struct SDL_JoyBallEvent {
    uint8_t type;	/**< SDL_JOYBALLMOTION */
    uint8_t which;	/**< The joystick device index */
    uint8_t ball;	/**< The joystick trackball index */
    int16_t xrel;	/**< The relative motion in the X direction */
    int16_t yrel;	/**< The relative motion in the Y direction */
} SDL_JoyBallEvent;

/** Joystick hat position change event structure */
typedef struct SDL_JoyHatEvent {
    uint8_t type;	/**< SDL_JOYHATMOTION */
    uint8_t which;	/**< The joystick device index */
    uint8_t hat;	/**< The joystick hat index */
    uint8_t value;	/**< The hat position value:
			 *   SDL_HAT_LEFTUP   SDL_HAT_UP       SDL_HAT_RIGHTUP
			 *   SDL_HAT_LEFT     SDL_HAT_CENTERED SDL_HAT_RIGHT
			 *   SDL_HAT_LEFTDOWN SDL_HAT_DOWN     SDL_HAT_RIGHTDOWN
			 *  Note that zero means the POV is centered.
			 */
} SDL_JoyHatEvent;

/** Joystick button event structure */
typedef struct SDL_JoyButtonEvent {
    uint8_t type;	/**< SDL_JOYBUTTONDOWN or SDL_JOYBUTTONUP */
    uint8_t which;	/**< The joystick device index */
    uint8_t button;	/**< The joystick button index */
    uint8_t state;	/**< SDL_PRESSED or SDL_RELEASED */
} SDL_JoyButtonEvent;

/** The "window resized" event
 *  When you get this event, you are responsible for setting a new video
 *  mode with the new width and height.
 */
typedef struct SDL_ResizeEvent {
    uint8_t type;	/**< SDL_VIDEORESIZE */
	int w;		/**< New width */
	int h;		/**< New height */
} SDL_ResizeEvent;

/** The "screen redraw" event */
typedef struct SDL_ExposeEvent {
    uint8_t type;	/**< SDL_VIDEOEXPOSE */
} SDL_ExposeEvent;

/** The "quit requested" event */
typedef struct SDL_QuitEvent {
    uint8_t type;	/**< SDL_QUIT */
} SDL_QuitEvent;

/** A user-defined event type */
typedef struct SDL_UserEvent {
    uint8_t type;	/**< SDL_USEREVENT through SDL_NUMEVENTS-1 */
	int code;	/**< User defined event code */
	void *data1;	/**< User defined data pointer */
	void *data2;	/**< User defined data pointer */
} SDL_UserEvent;

/** If you want to use this event, you should include SDL_syswm.h */
struct SDL_SysWMmsg;
typedef struct SDL_SysWMmsg SDL_SysWMmsg;
typedef struct SDL_SysWMEvent {
    uint8_t type;
	SDL_SysWMmsg *msg;
} SDL_SysWMEvent;

/** struct for read/write operations */
typedef struct SDL_RWops {
   ...;
} SDL_RWops;

typedef union SDL_Event {
    uint8_t type;
    SDL_ActiveEvent active;
    SDL_KeyboardEvent key;
    SDL_MouseMotionEvent motion;
    SDL_MouseButtonEvent button;
    SDL_JoyAxisEvent jaxis;
    SDL_JoyBallEvent jball;
    SDL_JoyHatEvent jhat;
    SDL_JoyButtonEvent jbutton;
    SDL_ResizeEvent resize;
    SDL_ExposeEvent expose;
    SDL_QuitEvent quit;
    SDL_UserEvent user;
    SDL_SysWMEvent syswm;
} SDL_Event;

typedef enum {
    SDL_NOEVENT,
    SDL_ACTIVEEVENT,
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_MOUSEMOTION,
    SDL_MOUSEBUTTONDOWN,
    SDL_MOUSEBUTTONUP,
    SDL_JOYAXISMOTION,
    SDL_JOYBALLMOTION,
    SDL_JOYHATMOTION,
    SDL_JOYBUTTONDOWN,
    SDL_JOYBUTTONUP,
    SDL_QUIT,
    SDL_SYSWMEVENT,
    SDL_EVENT_RESERVEDA,
    SDL_EVENT_RESERVEDB,
    SDL_VIDEORESIZE,
    SDL_VIDEOEXPOSE,
    SDL_EVENT_RESERVED2,
    SDL_EVENT_RESERVED3,
    SDL_EVENT_RESERVED4,
    SDL_EVENT_RESERVED5,
    SDL_EVENT_RESERVED6,
    SDL_EVENT_RESERVED7,
    SDL_USEREVENT,
    SDL_NUMEVENTS,
    ...
} SDL_EventType;

typedef struct SDL_VideoInfo {
    Uint32 hw_available:1;
    Uint32 wm_available:1;
    Uint32 blit_hw:1;
    Uint32 blit_hw_CC:1;
    Uint32 blit_hw_A:1;
    Uint32 blit_sw:1;
    Uint32 blit_sw_CC:1;
    Uint32 blit_sw_A:1;
    Uint32 blit_fill:1;
    Uint32 video_mem;
    SDL_PixelFormat* vfmt;
    int current_w;
    int current_h;
} SDL_VideoInfo;

typedef struct SDL_version {
        Uint8 major;
        Uint8 minor;
        Uint8 patch;
} SDL_version;

// misc other typdefs

typedef enum {
  SDL_ADDEVENT,
  SDL_PEEKEVENT,
  SDL_GETEVENT
} SDL_eventaction;

typedef struct _SDL_TimerID *SDL_TimerID;

typedef Uint32 (*SDL_NewTimerCallback)(Uint32 interval, void *param);

// functions

int SDL_Init(Uint32 flags);
int SDL_InitSubSystem(Uint32 flags);
void SDL_Quit(void);
void SDL_QuitSubSystem(Uint32 flags);
SDL_Surface *SDL_SetVideoMode(int width, int height, int bpp, uint32_t flags);
int SDL_VideoModeOK(int width, int height, int bpp, Uint32 flags);
uint32_t SDL_WasInit(uint32_t flags);
char *SDL_GetError(void);
void SDL_SetError(const char *fmt, ...);
const SDL_version* SDL_Linked_Version();
uint8_t SDL_GetAppState(void);
int SDL_WM_IconifyWindow(void);
int SDL_WM_ToggleFullScreen(SDL_Surface *surface);

uint32_t SDL_MapRGBA(
    SDL_PixelFormat *fmt, uint8_t r, uint8_t g, uint8_t b, uint8_t a);

SDL_Surface* SDL_GetVideoSurface(void);
const SDL_VideoInfo* SDL_GetVideoInfo(void);
char *SDL_VideoDriverName(char *namebuf, int maxlen);
SDL_Rect **SDL_ListModes(SDL_PixelFormat *format, Uint32 flags);

int SDL_LockSurface(SDL_Surface*);
void SDL_UnlockSurface(SDL_Surface*);
int SDL_FillRect(SDL_Surface *dst, SDL_Rect *dsrect, uint32_t color);

SDL_Surface  *SDL_CreateRGBSurface(Uint32 flags, int width, int height,
       int depth, Uint32 Rmask, Uint32 Gmask, Uint32 Bmask, Uint32 Amask);
SDL_Surface  *SDL_CreateRGBSurfaceFrom(void  *pixels,  int  width,  int
       height, int depth, int pitch, Uint32 Rmask, Uint32 Gmask, Uint32 Bmask,
       Uint32 Amask);
SDL_Surface *SDL_DisplayFormatAlpha(SDL_Surface *surface);
SDL_Surface *SDL_DisplayFormat(SDL_Surface *surface);
void SDL_GetRGBA(Uint32 pixel, SDL_PixelFormat *fmt,  Uint8  *r,  Uint8
                 *g, Uint8 *b, Uint8 *a);
SDL_Surface *SDL_ConvertSurface(SDL_Surface *src, SDL_PixelFormat *fmt,
       Uint32 flags);
void SDL_FreeSurface(SDL_Surface *surface);
int SDL_SetPalette(SDL_Surface *surface, int flags, SDL_Color *colors,
       int firstcolor, int ncolors);

int SDL_BlitSurface(SDL_Surface *src,  SDL_Rect  *srcrect,  SDL_Surface
       *dst, SDL_Rect *dstrect);
int SDL_SetAlpha(SDL_Surface *surface, Uint32 flag, Uint8 alpha);
int SDL_SetGamma(float redgamma, float greengamma, float bluegamma);
int SDL_SetGammaRamp(uint16_t *redtable,  uint16_t *greentable,  uint16_t *bluetable);

int SDL_GL_GetAttribute(SDL_GLattr attr, int *value);
int SDL_GL_SetAttribute(SDL_GLattr attr, int value);

int SDL_Flip(SDL_Surface*);

void SDL_UpdateRect(SDL_Surface *screen, int x, int y, int  w, int h);
void  SDL_UpdateRects(SDL_Surface  *screen,  int   numrects,   SDL_Rect *rects);

Uint32 SDL_GetTicks(void);
void SDL_Delay(Uint32 ms);

void SDL_PumpEvents(void);
int  SDL_PeepEvents(
    SDL_Event  *events,  int  numevents,  SDL_eventaction action, Uint32 mask);
int SDL_PushEvent(SDL_Event *event);

SDL_TimerID SDL_AddTimer(
    Uint32 interval, SDL_NewTimerCallback callback, void *param);
SDL_bool SDL_RemoveTimer(SDL_TimerID id);

int SDL_SetColorKey(SDL_Surface *surface, Uint32 flag, Uint32 key);

void SDL_WM_GetCaption(char **title, char **icon);
void SDL_WM_SetCaption(const char *title, const char *icon);
void SDL_WM_SetIcon(SDL_Surface *icon, Uint8 *mask);

typedef enum {
    SDL_GRAB_QUERY,
    SDL_GRAB_OFF,
    SDL_GRAB_ON,
    ...
} SDL_GrabMode;

SDL_GrabMode SDL_WM_GrabInput(SDL_GrabMode mode);

Uint8 SDL_GetMouseState(int *x, int *y);

int SDL_PollEvent(SDL_Event *event);
Uint8 SDL_EventState(Uint8 type, int state);

// Wrapper around SDL_BUTTON() macro.
Uint8 _pygame_SDL_BUTTON(Uint8 X);
int SDL_ShowCursor(int toggle);

SDL_Surface * IMG_LoadTyped_RW(SDL_RWops *src, int freesrc, char *type);
SDL_Surface * IMG_Load(const char *file);

typedef struct _TTF_Font TTF_Font;

#define TTF_STYLE_NORMAL ...
#define TTF_STYLE_BOLD ...
#define TTF_STYLE_ITALIC ...
#define TTF_STYLE_UNDERLINE ...
#define TTF_STYLE_STRIKETHROUGH ...

int TTF_Init(void);
int TTF_WasInit(void);
void TTF_Quit(void);

TTF_Font * TTF_OpenFont(const char *file, int ptsize);
SDL_Surface * TTF_RenderUTF8_Solid(TTF_Font *font, const char *text, SDL_Color fg);
SDL_Surface * TTF_RenderUTF8_Shaded(TTF_Font *font, const char *text, SDL_Color fg, SDL_Color bg);
SDL_Surface * TTF_RenderUTF8_Blended(TTF_Font *font, const char *text, SDL_Color fg);
int TTF_GetFontStyle(const TTF_Font *font);
void TTF_SetFontStyle(TTF_Font *font, int style);
int TTF_SizeUTF8(TTF_Font *font, const char *text, int *w, int *h);

typedef struct Mix_Chunk {
   ...;
} Mix_Chunk;

typedef struct _Mix_Music Mix_Music;

#define AUDIO_U8      ...
#define AUDIO_S8      ...
#define AUDIO_U16SYS  ...
#define AUDIO_S16SYS  ...

SDL_RWops * SDL_RWFromFile(const char *file, const char *mode);

int Mix_PlayChannelTimed(int channel, Mix_Chunk *chunk, int loops, int ticks);
int Mix_FadeInChannelTimed(int channel, Mix_Chunk *chunk, int loops, int ms, int ticks);
int Mix_Volume(int channel, int volume);
int Mix_VolumeMusic(int volume);
int Mix_QuerySpec(int *frequency, uint16_t *format,int *channels);
int Mix_OpenAudio(int frequency, uint16_t format, int channels, int chunksize);
Mix_Chunk * Mix_LoadWAV_RW(SDL_RWops *src, int freesrc);

int Mix_HaltMusic(void);
void Mix_PauseMusic(void);
void Mix_ResumeMusic(void);
int Mix_FadeInMusicPos(Mix_Music *music, int loops, int ms, double position);
Mix_Music * Mix_LoadMUS(const char *file);
void Mix_FreeMusic(Mix_Music *music);
int Mix_PlayingMusic(void);
int Mix_Playing(int channel);
int Mix_GroupAvailable(int tag);
int Mix_GroupOldest(int tag);
int Mix_GroupChannel(int which, int tag);
void Mix_Pause(int channel);
void Mix_Resume(int channel);
int Mix_HaltChannel(int channel);
int Mix_SetPanning(int channel, Uint8 left, Uint8 right);
void Mix_HookMusicFinished(void (*music_finished)(void));

""")

sdl = ffi.verify(
    libraries=['SDL', 'SDL_image', 'SDL_ttf', 'SDL_mixer'],
    include_dirs=['/usr/include/SDL', '/usr/local/include/SDL'],
    source="""
    #include <SDL.h>
    #include <SDL_image.h>
    #include <SDL_ttf.h>
    #include <SDL_mixer.h>

    Uint8 _pygame_SDL_BUTTON(Uint8 X) {
        return SDL_BUTTON(X);
    }

    """
)


def LockSurface(c_surface):
    res = sdl.SDL_LockSurface(c_surface)
    if res == -1:
        raise RuntimeError("error locking surface")


def FillRect(dst, dstrect, color):
    from pygame._error import SDLError

    res = sdl.SDL_FillRect(dst, dstrect, color)
    if res == -1:
        raise SDLError.from_sdl_error()


def BlitSurface(src, srcrect, dst, dstrect, extra_flags):
    from pygame._error import SDLError

    if dst.subsurfacedata is not None:
        xxx
    res = sdl.SDL_BlitSurface(src._c_surface, srcrect, dst._c_surface, dstrect)
    if res < 0:
        raise SDLError.from_sdl_error()


class locked(object):
    def __init__(self, c_surface):
        self.c_surface = c_surface

    def __enter__(self):
        LockSurface(self.c_surface)

    def __exit__(self, *args):
        sdl.SDL_UnlockSurface(self.c_surface)


if platform.system().startswith('Darwin'):
    from pygame.macosx import pre_video_init
else:
    def pre_video_init():
        pass
