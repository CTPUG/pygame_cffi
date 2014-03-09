""" pygame module for controlling streamed audio """

from pygame._sdl import ffi, sdl
from pygame._error import SDLError
from pygame import event
from pygame.rwobject import rwops_encode_file_path, rwops_from_file

_current_music = None
_queue_music = None
_endmusic_event = sdl.SDL_NOEVENT
_music_pos = 0
_music_pos_time = -1
_music_frequency = 0
_music_format = 0
_music_channels = 0


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
    global _current_music, _queue_music
    if isinstance(obj, basestring):
        filename = rwops_encode_file_path(obj)
        new_music = sdl.Mix_LoadMUS(filename)
    else:
        rwops = rwops_from_file(obj)
        new_music = sdl.Mix_LoadMUS_RW(rwops)
    if not new_music:
        raise SDLError.from_sdl_error()

    # Cleanup
    if _current_music:
        sdl.Mix_FreeMusic(_current_music)
    if _queue_music:
        sdl.Mix_FreeMusic(_queue_music)
        _queue_music = None

    _current_music = new_music


def pause():
    """pause(): return None
       temporarily stop music playback"""
    check_mixer()
    sdl.Mix_PauseMusic()


def unpause():
    """unpause(): return None
       resume paused music"""
    check_mixer()
    sdl.Mix_ResumeMusic()


def play(loops=0, startpos=0.0):
    """play(loops=0, start=0.0): return None
       Start the playback of the music stream"""
    global _current_music, _music_pos, _music_pos_time, \
           _music_frequency, _music_format, _music_channels
    check_mixer()

    if not _current_music:
        raise SDLError("music not loaded")

    sdl.Mix_HookMusicFinished(_endmusic_callback)
    sdl.Mix_SetPostMix(_mixmusic_callback, ffi.NULL)
    frequency, format, channels = (ffi.new('int*'), ffi.new('uint16_t*'),
                                   ffi.new('int*'))
    sdl.Mix_QuerySpec(frequency, format, channels)
    _music_pos = 0
    _music_pos_time = sdl.SDL_GetTicks()
    _music_frequency = frequency[0]
    _music_format = format[0]
    _music_channels = channels[0]
    volume = sdl.Mix_VolumeMusic(-1)
    val = sdl.Mix_FadeInMusicPos(_current_music, loops, 0, startpos)
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
    global _queue_music
    if _queue_music:
        sdl.Mix_FreeMusic(_queue_music)
        _queue_music = None


def get_busy():
    """get_busy(): return bool

       check if the music stream is playing"""
    check_mixer()
    return sdl.Mix_PlayingMusic() != 0


def set_endevent(end_event=None):
    global _endmusic_event
    _endmusic_event = end_event


def get_endevent():
    """ get_endevent() -> type
    get the event a channel sends when playback stops
    """
    return _endmusic_event


def rewind():
    """ rewind() -> None
    restart music
    """
    check_mixer()
    sdl.Mix_RewindMusic()


def fadeout(milliseconds):
    """ fadeout(time) -> None
    stop music playback after fading out
    """
    check_mixer()
    milliseconds = int(milliseconds)
    sdl.Mix_FadeOutMusic(milliseconds)
    global _queue_music
    if _queue_music:
        sdl.Mix_FreeMusic(_queue_music)
        _queue_music = None


def set_pos(pos):
    """ set_pos(pos) -> None
    set position to play from
    """
    check_mixer()
    pos = float(pos)
    if sdl.Mix_SetMusicPosition(pos) == -1:
        raise SDLError("set_pos unsupported for this codec")


def get_pos():
    """ get_pos() -> time
    get the music play time
    """
    check_mixer()
    if _music_pos_time < 0:
        return -1
    ticks = (1000 * _music_pos / (float(_music_channels) *
             _music_frequency * ((_music_format & 0xff) >> 3)))
    if not sdl.Mix_PausedMusic():
        ticks += sdl.SDL_GetTicks() - _music_pos_time
    return ticks


def queue(filename):
    """ queue(filename) -> None
    queue a music file to follow the current
    """
    check_mixer()
    global _queue_music
    try:
        filename = rwops_encode_file_path(filename)
        _queue_music = sdl.Mix_LoadMUS(filename)
    except SDLError:
        # try as file object
        rwops = rwops_from_file(filename)
        _queue_music = sdl.Mix_LoadMUS_RW(rwops)

    if not _queue_music:
        raise SDLError.from_sdl_error()


@ffi.callback("void (*)(void)")
def _endmusic_callback():
    global _current_music, _queue_music, _music_pos, _music_pos_time
    if _endmusic_event is not None and sdl.SDL_WasInit(sdl.SDL_INIT_AUDIO):
        event.post(event.Event(_endmusic_event))

    if _queue_music:
        if _current_music:
            sdl.Mix_FreeMusic(_current_music)
        _current_music = _queue_music
        _queue_music = None
        sdl.Mix_HookMusicFinished(_endmusic_callback)
        _music_pos = 0
        sdl.Mix_PlayMusic(_current_music, 0)
    else:
        _music_pos_time = -1
        sdl.Mix_SetPostMix(ffi.NULL, ffi.NULL)


@ffi.callback("void (*)(void *udata, uint8_t *stream, int len)")
def _mixmusic_callback(udata, stream, len):
    global _music_pos, _music_pos_time
    if not sdl.Mix_PausedMusic():
        _music_pos += len
        _music_pos_time = sdl.SDL_GetTicks()
