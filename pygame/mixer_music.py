""" pygame module for controlling streamed audio """

from pygame._sdl import ffi, sdl
from pygame._error import SDLError

_current_music = None
_endmusic_event = None


def check_mixer():
    """Helper function to check if sound was initialised"""
    # Defined here so we don't need circular imports between
    # mixer and this
    if not sdl.SDL_WasInit(sdl.SDL_INIT_AUDIO):
        raise SDLError("mixer system not initialized")


def load(obj):
    """load(filename): return None
       load(object): return None

       Load a music file for playback"""
    check_mixer()
    global _current_music
    if isinstance(obj, basestring):
        new_music = sdl.Mix_LoadMUS(obj)
    else:
        raise NotImplementedError("Fix me")
    if not new_music:
        raise SDLError.from_sdl_error()

    # Cleanup
    if _current_music:
        sdl.Mix_FreeMusic(_current_music)

    _current_music = new_music


def pause():
    """pause(): return None
       temporarily stop music playback"""
    check_mixer()
    sdl.Mix_PauseMusic()


def play(loops=0, start=0.0):
    """play(loops=0, start=0.0): return None
       Start the playback of the music stream"""
    # FIXME: Handle endevent positing and so forth
    global _current_music
    check_mixer()

    if not _current_music:
        raise SDLError("music not loaded")
    sdl.Mix_HookMusicFinished(_endmusic_callback)
    # FIXME: Get helper values for get_pos
    volume = sdl.Mix_VolumeMusic(-1)
    val = sdl.Mix_FadeInMusicPos(_current_music, loops, 0, start)
    sdl.Mix_VolumeMusic(volume)
    if val == -1:
        raise SDLError.from_sdl_error()


def set_volume(volume):
    """set_volume(value): return None
       set the music volume"""
    check_mixer()
    sdl.Mix_VolumeMusic(int(volume * 128))


def get_volume():
    """music.get_volume(): return value
    get the music volume"""
    check_mixer()
    volume = sdl.Mix_VolumeMusic(-1)
    return volume / 128.0


def stop():
    """stop(): return None
       stop the music playback"""
    check_mixer()
    sdl.Mix_HaltMusic()
    # FIXME: Handle music queue stuff when that's implemented


def unpause():
    """unpause(): return None
       resume paused music"""
    check_mixer()
    sdl.Mix_ResumeMusic()


def get_busy():
    """get_busy(): return bool

       check if the music stream is playing"""
    check_mixer()
    return sdl.Mix_PlayingMusic() != 0


def set_endevent(end_event=None):
    global _endmusic_event
    _endmusic_event = end_event


@ffi.callback("void (*)(void)")
def _endmusic_callback():
    if _endmusic_event is not None:
        import pygame.event
        pygame.event.post(pygame.event.Event(_endmusic_event))
