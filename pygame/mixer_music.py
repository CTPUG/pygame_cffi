""" pygame module for controlling streamed audio """

from pygame._sdl import sdl
from pygame._error import SDLError

current_music = None


def _check_init():
    # Duplicated logic to avoid circular imports
    if not sdl.SDL_WasInit(sdl.SDL_INIT_AUDIO):
        raise SDLError("mixer system not initialized")


def load(obj):
    """load(filename): return None
       load(object): return None

       Load a music file for playback"""
    _check_init()
    global current_music
    if isinstance(obj, basestring):
        new_music = sdl.Mix_LoadMUS(obj)
    else:
        raise NotImplementedError("Fix me")
    if not new_music:
        raise SDLError.from_sdl_error()

    # Cleanup
    if current_music:
        sdl.Mix_FreeMusic(current_music)

    current_music = new_music


def pause():
    """pause(): return None
       temporarily stop music playback"""
    sdl.Mix_PauseMusic()


def play(loops=0, start=0.0):
    """play(loops=0, start=0.0): return None
       Start the playback of the music stream"""
    # FIXME: Handle endevent positing and so forth
    global current_music
    _check_init()

    if not current_music:
        raise SDLError("music not loaded")
    # FIXME: Get helper values for get_pos
    volume = sdl.Mix_VolumeMusic(-1)
    val = sdl.Mix_FadeInMusicPos(current_music, loops, 0, start)
    sdl.Mix_VolumeMusic(volume)
    if val == -1:
        raise SDLError.from_sdl_error()


def set_volume(value):
    """set_volume(value): return None
       set the music volume"""
    sdl.Mix_VolumeMusic(int(volume * 128))


def stop():
    """stop(): return None
       stop the music playback"""
    sdl.Mix_HaltMusic()
    # FIXME: Handle music queue stuff when that's implemented


def unpause():
    """unpause(): return None
       resume paused music"""
    sdl.Mix_ResumeMusic()


def get_busy():
    """get_busy(): return bool

       check if the music stream is playing"""
    _check_init()
    return sdl.Mix_PlayingMusic() != 0
