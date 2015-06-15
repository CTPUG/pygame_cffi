import os
import cffi


def _get_c_lib(name):
    """Return the contents of a C library."""
    filename = os.path.join(
        os.path.dirname(__file__), 'lib', name)
    with open(filename) as lib:
        return lib.read()


ffi = cffi.FFI()

ffi.cdef("""

// base types

typedef uint32_t Uint32;
typedef uint8_t Uint8;

void free (void* ptr);
void *memmove(void *dest, const void *src, size_t n);

// constants

#define SDL_INIT_EVERYTHING ...
#define SDL_INIT_TIMER ...
#define SDL_INIT_VIDEO ...
#define SDL_INIT_AUDIO ...
#define SDL_INIT_NOPARACHUTE ...

#define SDL_APPACTIVE ...
#define SDL_APPMOUSEFOCUS ...
#define SDL_APPINPUTFOCUS ...

#define SDL_ANYFORMAT ...
#define SDL_ALLEVENTS ...
#define SDL_ASYNCBLIT ...
#define SDL_HWPALETTE ...

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
#define SDL_RESIZABLE ...
#define SDL_NOFRAME ...

#define SDL_DOUBLEBUF ...
#define SDL_HWACCEL ...
#define SDL_PREALLOC ...

#define SDL_QUERY ...
#define SDL_IGNORE ...
#define SDL_DISABLE ...
#define SDL_ENABLE ...

#define SDL_PHYSPAL ...
#define SDL_LOGPAL ...

#define SDL_BYTEORDER ...
#define SDL_LIL_ENDIAN ...

#define SDL_INIT_EVENTTHREAD ...

// OpenGL constants

#define SDL_OPENGL ...
#define SDL_OPENGLBLIT ...

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
    int offset;
    void *pixels;
    uint16_t pitch;
    uint32_t flags;
    SDL_Rect clip_rect;
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

typedef struct WMcursor WMcursor;   /**< Implementation dependent */
typedef struct SDL_Cursor {
    SDL_Rect area;          /**< The area of the mouse cursor */
    int16_t hot_x, hot_y;    /**< The "tip" of the cursor */
    uint8_t *data;            /**< B/W cursor data */
    uint8_t *mask;            /**< B/W cursor mask */
    uint8_t *save[2];         /**< Place to save cursor area */
    WMcursor *wm_cursor;    /**< Window-manager cursor */
} SDL_Cursor;

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
    SDL_NOEVENT = 0,
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
    SDL_USEREVENT = 24,
    SDL_NUMEVENTS = 32
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
int SDL_EnableUNICODE(int enable);
void SDL_ClearError(void);

int SDL_EnableKeyRepeat(int delay, int interval);
void SDL_GetKeyRepeat(int *delay,int *interval);
uint8_t *SDL_GetKeyState(int *numkeys);
char *SDL_GetKeyName(SDLKey key);
SDLMod SDL_GetModState(void);
void SDL_SetModState(SDLMod modstate);

uint32_t SDL_MapRGBA(
    SDL_PixelFormat *fmt, uint8_t r, uint8_t g, uint8_t b, uint8_t a);

SDL_Surface* SDL_GetVideoSurface(void);
const SDL_VideoInfo* SDL_GetVideoInfo(void);
char *SDL_VideoDriverName(char *namebuf, int maxlen);
int SDL_VideoInit(const char* driver_name, uint32_t flags);
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
void SDL_GL_SwapBuffers(void);

int SDL_Flip(SDL_Surface*);

void SDL_UpdateRect(SDL_Surface *screen, int x, int y, int  w, int h);
void  SDL_UpdateRects(SDL_Surface  *screen,  int   numrects,   SDL_Rect *rects);

void SDL_GetClipRect(SDL_Surface *surface, SDL_Rect *rect);
void SDL_SetClipRect(SDL_Surface *surface, SDL_Rect *rect);

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
int SDL_SetColors(SDL_Surface *surface, SDL_Color *colors,  int  first_color, int ncolors);

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

uint8_t SDL_GetMouseState(int *x, int *y);
uint8_t SDL_GetRelativeMouseState(int *x, int *y);
void SDL_WarpMouse(uint16_t x, uint16_t y);

int SDL_PollEvent(SDL_Event *event);
int SDL_WaitEvent(SDL_Event *event);
Uint8 SDL_EventState(Uint8 type, int state);

// Wrapper around SDL_BUTTON() macro.
Uint8 _pygame_SDL_BUTTON(Uint8 X);
int SDL_ShowCursor(int toggle);
void SDL_SetCursor(SDL_Cursor *cursor);
SDL_Cursor *SDL_GetCursor(void);
SDL_Cursor *SDL_CreateCursor(Uint8  *data,  Uint8 *mask, int w, int h,
    int hot_x, int hot_y);
void SDL_FreeCursor(SDL_Cursor *cursor);

SDL_Surface * IMG_LoadTyped_RW(SDL_RWops *src, int freesrc, char *type);
SDL_Surface * IMG_Load(const char *file);
char *IMG_GetError();
SDL_Surface* SDL_LoadBMP_RW(SDL_RWops* src, int freesrc);
SDL_Surface* SDL_LoadBMP(const char* file);
int SDL_SaveBMP(SDL_Surface *surface, const char *file);
static int _pygame_SaveTGA_RW (SDL_Surface *surface, SDL_RWops *out, int rle);

typedef struct _TTF_Font TTF_Font;

#define TTF_STYLE_NORMAL ...
#define TTF_STYLE_BOLD ...
#define TTF_STYLE_ITALIC ...
#define TTF_STYLE_UNDERLINE ...
#define TTF_STYLE_STRIKETHROUGH ...

int TTF_Init(void);
int TTF_WasInit(void);
void TTF_Quit(void);

char* TTF_GetError();
TTF_Font * TTF_OpenFont(const char *file, int ptsize);
TTF_Font *TTF_OpenFontIndexRW(SDL_RWops *src, int freesrc, int ptsize, long index);
TTF_Font *TTF_OpenFontRW(SDL_RWops *src, int freesrc, int ptsize);
void TTF_CloseFont(TTF_Font* font);
SDL_Surface * TTF_RenderUTF8_Solid(TTF_Font *font, const char *text, SDL_Color fg);
SDL_Surface * TTF_RenderUTF8_Shaded(TTF_Font *font, const char *text, SDL_Color fg, SDL_Color bg);
SDL_Surface * TTF_RenderUTF8_Blended(TTF_Font *font, const char *text, SDL_Color fg);
int TTF_GetFontStyle(const TTF_Font *font);
void TTF_SetFontStyle(TTF_Font *font, int style);
int TTF_SizeUTF8(TTF_Font *font, const char *text, int *w, int *h);
int TTF_FontHeight(TTF_Font *font);
int TTF_FontAscent(TTF_Font *font);
int TTF_FontDescent(TTF_Font *font);
int TTF_FontLineSkip(TTF_Font *font);
int TTF_GlyphMetrics(TTF_Font *font, uint16_t ch, int *minx, int *maxx, int *miny, int *maxy, int *advance);

typedef struct Mix_Chunk {
    uint8_t *abuf;
    uint32_t alen;
    ...;
} Mix_Chunk;

typedef struct _Mix_Music Mix_Music;

#define AUDIO_U8      ...
#define AUDIO_S8      ...
#define AUDIO_U16SYS  ...
#define AUDIO_S16SYS  ...
#define MIX_CHANNELS ...

SDL_RWops * SDL_RWFromFile(const char *file, const char *mode);
SDL_RWops * SDL_RWFromFP(FILE *fp, int autoclose);
SDL_RWops * SDL_AllocRW(void);
int SDL_RWclose(struct SDL_RWops* context);
size_t SDL_RWwrite(struct SDL_RWops* context, const void* ptr, size_t size, size_t num);

int Mix_PlayChannelTimed(int channel, Mix_Chunk *chunk, int loops, int ticks);
int Mix_FadeInChannelTimed(int channel, Mix_Chunk *chunk, int loops, int ms, int ticks);
void Mix_ChannelFinished(void (*channel_finished)(int channel));
int Mix_Volume(int channel, int volume);
int Mix_VolumeMusic(int volume);
int Mix_VolumeChunk(Mix_Chunk *chunk, int volume);
int Mix_QuerySpec(int *frequency, uint16_t *format,int *channels);
int Mix_OpenAudio(int frequency, uint16_t format, int channels, int chunksize);
void Mix_CloseAudio(void);
Mix_Chunk * Mix_LoadWAV_RW(SDL_RWops *src, int freesrc);
void Mix_FreeChunk(Mix_Chunk *chunk);
int Mix_AllocateChannels(int numchans);
int Mix_FadeOutChannel(int channel, int ms);
int Mix_ReserveChannels(int num);
int Mix_HaltMusic(void);
void Mix_PauseMusic(void);
int Mix_PausedMusic(void);
void Mix_ResumeMusic(void);
int Mix_FadeInMusicPos(Mix_Music *music, int loops, int ms, double position);
int Mix_PlayMusic(Mix_Music *music, int loops);
int Mix_FadeOutMusic(int ms);
Mix_Music * Mix_LoadMUS(const char *file);
Mix_Music * Mix_LoadMUS_RW(SDL_RWops *src);
void Mix_FreeMusic(Mix_Music *music);
int Mix_PlayingMusic(void);
int Mix_Playing(int channel);
int Mix_GroupAvailable(int tag);
int Mix_GroupOldest(int tag);
int Mix_GroupChannel(int which, int tag);
int Mix_GroupCount(int tag);
int Mix_FadeOutGroup(int tag, int ms);
void Mix_Pause(int channel);
void Mix_Resume(int channel);
int Mix_SetMusicPosition(double position);
void Mix_RewindMusic(void);
int Mix_HaltChannel(int channel);
int Mix_SetPanning(int channel, Uint8 left, Uint8 right);
void Mix_HookMusicFinished(void (*music_finished)(void));
void Mix_SetPostMix(void (*mix_func)(void *udata, uint8_t *stream, int len),
                    void *arg);

int pygame_Blit (SDL_Surface * src, SDL_Rect * srcrect,
    SDL_Surface * dst, SDL_Rect * dstrect, int the_args);
int surface_fill_blend (SDL_Surface *surface, SDL_Rect *rect, Uint32 color, int blendargs);
void scale2x(SDL_Surface *src, SDL_Surface *dst);
static void rotate90(SDL_Surface *src, SDL_Surface *dst, int angle);
static void rotate(SDL_Surface *src, SDL_Surface *dst, Uint32 bgcolor,
    double sangle, double cangle);
static void stretch (SDL_Surface *src, SDL_Surface *dst);
static void scalesmooth(SDL_Surface *src, SDL_Surface *dst);
SDL_Surface* rotozoomSurface (SDL_Surface *src, double angle, double zoom,
    int smooth);
""")

sdl = ffi.set_source(
    "pygame._sdl_c",
    libraries=['SDL', 'SDL_image', 'SDL_ttf', 'SDL_mixer'],
    include_dirs=['/usr/include/SDL', '/usr/local/include/SDL'],
    source="""
    #include <stdlib.h>
    #include <SDL.h>
    #include <SDL_image.h>
    #include <SDL_ttf.h>
    #include <SDL_mixer.h>

    Uint8 _pygame_SDL_BUTTON(Uint8 X) {
        return SDL_BUTTON(X);
    }

    /*******************************************************/
    /* tga code by Mattias Engdegard, in the public domain */
    /*******************************************************/
    struct TGAheader
    {
        Uint8 infolen;                /* length of info field */
        Uint8 has_cmap;                /* 1 if image has colormap, 0 otherwise */
        Uint8 type;

        Uint8 cmap_start[2];        /* index of first colormap entry */
        Uint8 cmap_len[2];                /* number of entries in colormap */
        Uint8 cmap_bits;                /* bits per colormap entry */

        Uint8 yorigin[2];                /* image origin (ignored here) */
        Uint8 xorigin[2];
        Uint8 width[2];                /* image size */
        Uint8 height[2];
        Uint8 pixel_bits;                /* bits/pixel */
        Uint8 flags;
    };

    enum tga_type
    {
        TGA_TYPE_INDEXED = 1,
        TGA_TYPE_RGB = 2,
        TGA_TYPE_BW = 3,
        TGA_TYPE_RLE = 8                /* additive */
    };

    #define TGA_INTERLEAVE_MASK        0xc0
    #define TGA_INTERLEAVE_NONE        0x00
    #define TGA_INTERLEAVE_2WAY        0x40
    #define TGA_INTERLEAVE_4WAY        0x80

    #define TGA_ORIGIN_MASK                0x30
    #define TGA_ORIGIN_LEFT                0x00
    #define TGA_ORIGIN_RIGHT        0x10
    #define TGA_ORIGIN_LOWER        0x00
    #define TGA_ORIGIN_UPPER        0x20

    /* read/write unaligned little-endian 16-bit ints */
    #define LE16(p) ((p)[0] + ((p)[1] << 8))
    #define SETLE16(p, v) ((p)[0] = (v), (p)[1] = (v) >> 8)

    #ifndef MIN
    #define MIN(a, b) ((a) < (b) ? (a) : (b))
    #endif

    #define TGA_RLE_MAX 128                /* max length of a TGA RLE chunk */
    /* return the number of bytes in the resulting buffer after RLE-encoding
       a line of TGA data */
    static int
    rle_line (Uint8 *src, Uint8 *dst, int w, int bpp)
    {
        int x = 0;
        int out = 0;
        int raw = 0;
        while (x < w)
        {
            Uint32 pix;
            int x0 = x;
            memcpy (&pix, src + x * bpp, bpp);
            x++;
            while (x < w && memcmp (&pix, src + x * bpp, bpp) == 0
                   && x - x0 < TGA_RLE_MAX)
                x++;
            /* use a repetition chunk iff the repeated pixels would consume
               two bytes or more */
            if ((x - x0 - 1) * bpp >= 2 || x == w)
            {
                /* output previous raw chunks */
                while (raw < x0)
                {
                    int n = MIN (TGA_RLE_MAX, x0 - raw);
                    dst[out++] = n - 1;
                    memcpy (dst + out, src + raw * bpp, n * bpp);
                    out += n * bpp;
                    raw += n;
                }

                if (x - x0 > 0)
                {
                    /* output new repetition chunk */
                    dst[out++] = 0x7f + x - x0;
                    memcpy (dst + out, &pix, bpp);
                    out += bpp;
                }
                raw = x;
            }
        }
        return out;
    }

    /*
     * Save a surface to an output stream in TGA format.
     * 8bpp surfaces are saved as indexed images with 24bpp palette, or with
     *     32bpp palette if colourkeying is used.
     * 15, 16, 24 and 32bpp surfaces are saved as 24bpp RGB images,
     * or as 32bpp RGBA images if alpha channel is used.
     *
     * RLE compression is not used in the output file.
     *
     * Returns -1 upon error, 0 if success
     */
    static int
    _pygame_SaveTGA_RW (SDL_Surface *surface, SDL_RWops *out, int rle)
    {
        SDL_Surface *linebuf = NULL;
        int alpha = 0;
        int ckey = -1;
        struct TGAheader h;
        int srcbpp;
        unsigned surf_flags;
        unsigned surf_alpha;
        Uint32 rmask, gmask, bmask, amask;
        SDL_Rect r;
        int bpp;
        Uint8 *rlebuf = NULL;

        h.infolen = 0;
        SETLE16 (h.cmap_start, 0);

        srcbpp = surface->format->BitsPerPixel;
        if (srcbpp < 8)
        {
            SDL_SetError ("cannot save <8bpp images as TGA");
            return -1;
        }

        if (srcbpp == 8)
        {
            h.has_cmap = 1;
            h.type = TGA_TYPE_INDEXED;
            if (surface->flags & SDL_SRCCOLORKEY)
            {
                ckey = surface->format->colorkey;
                h.cmap_bits = 32;
            }
            else
                h.cmap_bits = 24;
            SETLE16 (h.cmap_len, surface->format->palette->ncolors);
            h.pixel_bits = 8;
            rmask = gmask = bmask = amask = 0;
        }
        else
        {
            h.has_cmap = 0;
            h.type = TGA_TYPE_RGB;
            h.cmap_bits = 0;
            SETLE16 (h.cmap_len, 0);
            if (surface->format->Amask)
            {
                alpha = 1;
                h.pixel_bits = 32;
            }
            else
                h.pixel_bits = 24;
            if (SDL_BYTEORDER == SDL_BIG_ENDIAN)
            {
                int s = alpha ? 0 : 8;
                amask = 0x000000ff >> s;
                rmask = 0x0000ff00 >> s;
                gmask = 0x00ff0000 >> s;
                bmask = 0xff000000 >> s;
            }
            else
            {
                amask = alpha ? 0xff000000 : 0;
                rmask = 0x00ff0000;
                gmask = 0x0000ff00;
                bmask = 0x000000ff;
            }
        }
        bpp = h.pixel_bits >> 3;
        if (rle)
            h.type += TGA_TYPE_RLE;

        SETLE16 (h.yorigin, 0);
        SETLE16 (h.xorigin, 0);
        SETLE16 (h.width, surface->w);
        SETLE16 (h.height, surface->h);
        h.flags = TGA_ORIGIN_UPPER | (alpha ? 8 : 0);

        if (!SDL_RWwrite (out, &h, sizeof (h), 1))
            return -1;

        if (h.has_cmap)
        {
            int i;
            SDL_Palette *pal = surface->format->palette;
            Uint8 entry[4];
            for (i = 0; i < pal->ncolors; i++)
            {
                entry[0] = pal->colors[i].b;
                entry[1] = pal->colors[i].g;
                entry[2] = pal->colors[i].r;
                entry[3] = (i == ckey) ? 0 : 0xff;
                if (!SDL_RWwrite (out, entry, h.cmap_bits >> 3, 1))
                    return -1;
            }
        }

        linebuf = SDL_CreateRGBSurface (SDL_SWSURFACE, surface->w, 1, h.pixel_bits,
                                        rmask, gmask, bmask, amask);
        if (!linebuf)
            return -1;
        if (h.has_cmap)
            SDL_SetColors (linebuf, surface->format->palette->colors, 0,
                           surface->format->palette->ncolors);
        if (rle)
        {
            rlebuf = malloc (bpp * surface->w + 1 + surface->w / TGA_RLE_MAX);
            if (!rlebuf)
            {
                SDL_SetError ("out of memory");
                goto error;
            }
        }

        /* Temporarily remove colourkey and alpha from surface so copies are
           opaque */
        surf_flags = surface->flags & (SDL_SRCALPHA | SDL_SRCCOLORKEY);
        surf_alpha = surface->format->alpha;
        if (surf_flags & SDL_SRCALPHA)
            SDL_SetAlpha (surface, 0, 255);
        if (surf_flags & SDL_SRCCOLORKEY)
            SDL_SetColorKey (surface, 0, surface->format->colorkey);

        r.x = 0;
        r.w = surface->w;
        r.h = 1;
        for (r.y = 0; r.y < surface->h; r.y++)
        {
            int n;
            void *buf;
            if (SDL_BlitSurface (surface, &r, linebuf, NULL) < 0)
                break;
            if (rle)
            {
                buf = rlebuf;
                n = rle_line (linebuf->pixels, rlebuf, surface->w, bpp);
            }
            else
            {
                buf = linebuf->pixels;
                n = surface->w * bpp;
            }
            if (!SDL_RWwrite (out, buf, n, 1))
                break;
        }

        /* restore flags */
        if (surf_flags & SDL_SRCALPHA)
            SDL_SetAlpha (surface, SDL_SRCALPHA, (Uint8)surf_alpha);
        if (surf_flags & SDL_SRCCOLORKEY)
            SDL_SetColorKey (surface, SDL_SRCCOLORKEY, surface->format->colorkey);

    error:
        free (rlebuf);
        SDL_FreeSurface (linebuf);
        return 0;
    }

    %(surface_h)s

    %(alphablit)s

    %(surface_fill)s

    %(scale2x)s

    %(rotate)s

    %(stretch)s

    %(smoothscale)s

    %(rotozoom)s
    """ % {
        'surface_h': _get_c_lib('surface.h'),
        'alphablit': _get_c_lib('alphablit.c'),
        'surface_fill': _get_c_lib('surface_fill.c'),
        'scale2x': _get_c_lib('scale2x.c'),
        'rotate': _get_c_lib('rotate.c'),
        'stretch': _get_c_lib('stretch.c'),
        'smoothscale': _get_c_lib('smoothscale.c'),
        'rotozoom': _get_c_lib('rotozoom.c'),
    }
)


if __name__ == "__main__":
    ffi.compile()
