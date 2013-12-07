
import platform

import cffi

ffi = cffi.FFI()

ffi.cdef("""

// constants

#define SDL_INIT_EVERYTHING ...
#define SDL_INIT_TIMER ...
#define SDL_INIT_VIDEO ...

#define SDL_SWSURFACE ...
#define SDL_ANYFORMAT ...

#define SDL_ALLEVENTS ...

#define SDL_SWSURFACE ...
#define SDL_HWSURFACE ...

#define SDL_HAT_UP ...
#define SDL_HAT_DOWN ...
#define SDL_HAT_RIGHT ...
#define SDL_HAT_LEFT ...

// enums

typedef enum {
    SDL_FALSE = 0,
    SDL_TRUE  = 1
} SDL_bool;

typedef enum {
    SDLK_ESCAPE,
    SDLK_LAST,
    ...
} SDLKey;

typedef enum {
    KMOD_NONE,
    KMOD_RESERVED,
    ...
} SDLMod;

// structs

typedef struct SDL_PixelFormat {
    uint8_t BitsPerPixel;
    uint8_t BytesPerPixel;
    uint32_t Rmask, Gmask, Bmask, Amask;
    ...;
} SDL_PixelFormat;

typedef struct SDL_Rect {
    int16_t x, y;
    uint16_t w, h;
} SDL_Rect;

typedef struct SDL_Surface {
    SDL_PixelFormat* format;
    int w, h;
    void *pixels;
    uint16_t pitch;

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
    SDL_PixelFormat* vfmt;
    ...;
} SDL_VideoInfo;

// misc other typdefs

typedef enum {
  SDL_ADDEVENT,
  SDL_PEEKEVENT,
  SDL_GETEVENT
} SDL_eventaction;

typedef struct _SDL_TimerID *SDL_TimerID;

typedef uint32_t Uint32;
typedef uint8_t Uint8;

typedef Uint32 (*SDL_NewTimerCallback)(Uint32 interval, void *param);

// functions

int SDL_Init(Uint32 flags);
int SDL_InitSubSystem(Uint32 flags);
void SDL_Quit(void);
SDL_Surface *SDL_SetVideoMode(int width, int height, int bpp, uint32_t flags);
int SDL_VideoModeOK(int width, int height, int bpp, Uint32 flags);
uint32_t SDL_WasInit(uint32_t flags);
char *SDL_GetError(void);

uint32_t SDL_MapRGBA(
    SDL_PixelFormat *fmt, uint8_t r, uint8_t g, uint8_t b, uint8_t a);

SDL_Surface* SDL_GetVideoSurface(void);
const SDL_VideoInfo* SDL_GetVideoInfo(void);

int SDL_LockSurface(SDL_Surface*);
void SDL_UnlockSurface(SDL_Surface*);
int SDL_FillRect(SDL_Surface *dst, SDL_Rect *dsrect, uint32_t color);

SDL_Surface  *SDL_CreateRGBSurface(Uint32 flags, int width, int height,
       int depth, Uint32 Rmask, Uint32 Gmask, Uint32 Bmask, Uint32 Amask);

int SDL_BlitSurface(SDL_Surface *src,  SDL_Rect  *srcrect,  SDL_Surface
       *dst, SDL_Rect *dstrect);

int SDL_Flip(SDL_Surface*);

Uint32 SDL_GetTicks(void);
void SDL_Delay(Uint32 ms);

void SDL_PumpEvents(void);
int  SDL_PeepEvents(
    SDL_Event  *events,  int  numevents,  SDL_eventaction action, Uint32 mask);

SDL_TimerID SDL_AddTimer(
    Uint32 interval, SDL_NewTimerCallback callback, void *param);
SDL_bool SDL_RemoveTimer(SDL_TimerID id);

void SDL_WM_GetCaption(char **title, char **icon);

void SDL_WM_SetCaption(const char *title, const char *icon);
Uint8 SDL_GetMouseState(int *x, int *y);

int SDL_PollEvent(SDL_Event *event);

// Wrapper around SDL_BUTTON() macro.
Uint8 _pygame_SDL_BUTTON(Uint8 X);
""")

sdl = ffi.verify(
    libraries=['SDL'],
    include_dirs=['/usr/include/SDL', '/usr/local/include/SDL'],
    source="""
    #include <SDL.h>

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
    from pygame.error import SDLError

    res = sdl.SDL_FillRect(dst, dstrect, color)
    if res == -1:
        raise SDLError.from_sdl_error()


def BlitSurface(src, srcrect, dst, dstrect):
    from pygame.error import SDLError

    res = sdl.SDL_BlitSurface(src, srcrect, dst, dstrect)
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
