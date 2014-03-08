""" pygame module for loading and playing sounds """

import math

from pygame._sdl import sdl, ffi
from pygame._error import SDLError
from pygame.base import register_quit
import pygame.mixer_music as music
from pygame.mixer_music import check_mixer


PYGAME_MIXER_DEFAULT_FREQUENCY = 22050
PYGAME_MIXER_DEFAULT_SIZE = -16
PYGAME_MIXER_DEFAULT_CHANNELS = 2
PYGAME_MIXER_DEFAULT_CHUNKSIZE = 4096

_request_frequency = PYGAME_MIXER_DEFAULT_FREQUENCY;
_request_size = PYGAME_MIXER_DEFAULT_SIZE;
_request_stereo = PYGAME_MIXER_DEFAULT_CHANNELS;
_request_chunksize = PYGAME_MIXER_DEFAULT_CHUNKSIZE;

_channeldata = None
_numchanneldata = 0
_current_music = None
_queue_music = None


class ChannelData(object):
    def __init__(self):
        self.sound = None
        self.queue = None
        self.endevent = 0


class Channel(object):
    """Channel(id): return Channel
       Create a Channel object for controlling playback"""

    def __init__(self, channel):
        # This is a null object for now, since most pygame sound
        # playback doesn't make use of the channel functionality.
        self._channel = channel

    def play(self, Sound, loops=0, maxtime=-1, fade_ms=0):
        """play Sound on this channel"""
        if fade_ms > 0:
            channel = sdl.Mix_FadeInChannelTimed(self._channel,
                                                 Sound._chunk, loops,
                                                 fade_ms, maxtime)
        else:
            channel = sdl.Mix_PlayChannelTimed(self._channel,
                                               Sound._chunk, loops,
                                               maxtime)
        if channel != -1:
            sdl.Mix_GroupChannel(self._channel, Sound._chunk_tag)

    def get_busy(self):
        check_mixer()
        return sdl.Mix_Playing(self._channel) != 0

    def stop(self):
        check_mixer()
        sdl.Mix_HaltChannel(self._channel)

    def pause(self):
        check_mixer()
        sdl.Mix_Pause(self._channel)

    def unpause(self):
        check_mixer()
        sdl.Mix_Resume(self._channel)

    def get_volume(self):
        check_mixer()
        volume = sdl.Mix_Volume(self._channel, -1)
        return volume / 128.0

    def set_volume(self, lvolume, rvolume=None):
        check_mixer()
        # This logic differs a bit from pygames because we can use a better
        # sentinal value
        if rvolume is None:
            # No Panning
            if sdl.Mix_SetPanning(self._channel, 255, 255) == 0:
                raise SDLError.from_sdl_error()
            volume = int(lvolume * 128)
        else:
            # Panning
            left = int(lvolume * 255)
            right = int(rvolume * 255)
            if sdl.Mix_SetPanning(self._channel, left, right) == 0:
                raise SDLError.from_sdl_error()
            volume = 128
        sdl.Mix_Volume(self._channel, volume)

    def fadeout(self, time):
        """ fadeout(time) -> None
        stop playback after fading channel out
        """

    def get_sound(self, ):
        """ get_sound() -> Sound
        get the currently playing Sound
        """

    def queue(self, sound):
        """ queue(Sound) -> None
        queue a Sound object to follow the current
        """

    def get_queue(self):
        """ get_queue() -> Sound
        return any Sound that is queued
        """

    def set_endevent(self):
        """ set_endevent() -> None
        have the channel send an event when playback stops
        """

    def get_endevent(self):
        """ get_endevent() -> type
        get the event a channel sends when playback stops
        """


class Sound(object):
    """Sound(filename): return Sound
       Sound(buffer): return Sound
       Sound(object): return Sound

       Create a new Sound object from a file or buffer object"""

    def __init__(self, obj):
        check_mixer()
        if isinstance(obj, basestring):
            RWops = sdl.SDL_RWFromFile(obj, "rb")
            if RWops == ffi.NULL:
                raise SDLError.from_sdl_error()
            self._chunk = sdl.Mix_LoadWAV_RW(RWops, 1)
            # pygame uses the pointer address as the tag to ensure
            # uniqueness, we use id for the same effect
            # Since we don't have the some automatic casting rules as
            # C, we explicitly cast to int here. This matches pygames
            # behaviour, so we're bug-compatible
            self._chunk_tag = ffi.cast("int", id(self._chunk))
            if self._chunk == ffi.NULL:
                raise SDLError.from_sdl_error()
        else:
            raise NotImplementedError("Implement loading from buffer & object")

    def play(self, loops=0, maxtime=-1, fade_ms=0):
        """play(loops=0, maxtime=-1, fade_ms=0): return Channel

           begin sound playback"""
        if fade_ms > 0:
            channel = sdl.Mix_FadeInChannelTimed(-1, self._chunk, loops,
                                                 fade_ms, maxtime)
        else:
            channel = sdl.Mix_PlayChannelTimed(-1, self._chunk, loops,
                                               maxtime)
        if channel < 0:
            # failure
            return None

        sdl.Mix_Volume(channel, 128)
        sdl.Mix_GroupChannel(channel, self._chunk_tag)
        return Channel(channel)

    def get_volume(self):
        """get_volume(): return value

           get the playback volume"""
        check_mixer()
        volume = sdl.Mix_VolumeChunk(self._chunk, -1)
        return volume / 128.0

    def set_volume(self, volume):
        """set_volume(value): return None

           set the playback volume for this Sound"""
        check_mixer()
        sdl.Mix_VolumeChunk(self._chunk, int(volume * 128))

    def fadeout(self, time):
        """ fadeout(time) -> None
        stop sound playback after fading out
        """

    def get_length(self):
        """ get_length() -> seconds
        get the length of the Sound
        """

    def get_raw(self):
        """ get_raw() -> bytes
        return a bytestring copy of the Sound samples.
        """


def get_init():
    """get_init(): return (frequency, format, channels)

       test if the mixer is initialized"""
    if not sdl.SDL_WasInit(sdl.SDL_INIT_AUDIO):
        return None

    freq = ffi.new("int *")
    audioformat = ffi.new("uint16_t *")
    chan = ffi.new("int *")
    if not sdl.Mix_QuerySpec(freq, audioformat, chan):
        return None
    return (int(freq[0]), int(audioformat[0]), int(chan[0]))


def pre_init(frequency=PYGAME_MIXER_DEFAULT_FREQUENCY,
             size=PYGAME_MIXER_DEFAULT_SIZE,
             channels=PYGAME_MIXER_DEFAULT_CHANNELS,
             chunksize=PYGAME_MIXER_DEFAULT_CHUNKSIZE):
    """ pre_init(frequency=22050, size=-16, channels=2, buffersize=4096) -> None
    preset the mixer init arguments
    """
    global _request_frequency, _request_size, _request_stereo, \
           _request_chunksize
    _request_frequency = frequency
    _request_size = size
    _request_stereo = channels
    _request_chunksize = chunksize


def init(frequency=None, size=None, channels=None, chunksize=None):
    """init(frequency=22050, size=-16, channels=2, buffer=4096): return None
    initialize the mixer module
    """
    if not autoinit():
        raise SDLError.from_sdl_error()


def autoinit(frequency=None, size=None, channels=None, chunksize=None):
    if not frequency:
        frequency = _request_frequency
    if not size:
        size = _request_size
    if not channels:
        channels = _request_stereo
    if not chunksize:
        chunksize = _request_chunksize

    if channels >= 2:
        channels = 2
    else:
        channels = 1

    # chunk must be a power of 2
    chunksize = int(math.log(chunksize, 2))
    chunksize = 2 ** chunksize
    if chunksize < buffer:
        chunksize *= 2

    # fmt is a bunch of flags
    if size == 8:
        fmt = sdl.AUDIO_U8
    elif size == -8:
        fmt = sdl.AUDIO_S8
    elif size == 16:
        fmt = sdl.AUDIO_U16SYS
    elif size == -16:
        fmt = sdl.AUDIO_S16SYS
    else:
        raise ValueError("unsupported size %d" % size)

    global _numchanneldata, _channeldata
    if not sdl.SDL_WasInit(sdl.SDL_INIT_AUDIO):
        register_quit(autoquit)
        # channel stuff
        if not _channeldata:
            _numchanneldata = sdl.MIX_CHANNELS
            _channeldata = [ChannelData() for i in range(_numchanneldata)]

        if sdl.SDL_InitSubSystem(sdl.SDL_INIT_AUDIO) == -1:
            return False

        if sdl.Mix_OpenAudio(frequency, fmt, channels, chunksize) == -1:
            sdl.SDL_QuitSubSystem(sdl.SDL_INIT_AUDIO)
            return False
        sdl.Mix_ChannelFinished(_endsound_callback)
        # TODO: reverse stereo for 8-bit below SDL 1.2.8
        sdl.Mix_VolumeMusic(127)
    return True


def autoquit():
    global _channeldata, _numchanneldata, _current_music, \
           _queue_music
    if sdl.SDL_WasInit(sdl.SDL_INIT_AUDIO):
        sdl.Mix_HaltMusic()
        # cleanup
        if _channeldata:
            # TODO: free channel SDL objects
            _channeldata = None
            _numchanneldata = 0
        if _current_music:
            sdl.Mix_FreeMusic(_current_music)
            _current_music = None
        if _queue_music:
            sdl.Mix_FreeMusic(_queue_music)
            _queue_music = None

        sdl.Mix_CloseAudio()
        sdl.SDL_QuitSubSystem(sdl.SDL_INIT_AUDIO)


def quit():
    """ quit() -> None
    uninitialize the mixer
    """
    autoquit()


def find_channel(force):
    """find_channel(force=False): return Channel

        find an unused channel"""
    check_mixer()

    chan = sdl.Mix_GroupAvailable(-1)
    if chan == -1:
        if not force:
            return None
        chan = sdl.Mix_GroupOldest(-1)
    return Channel(chan)


def get_busy():
    """get_busy(): return bool

       test if any sound is being mixed"""
    if not sdl.SDL_WasInit(sdl.SDL_INIT_AUDIO):
        return False
    return sdl.Mix_Playing(-1) != 0


def get_num_channels():
    """get the total number of playback channels"""
    check_mixer()
    return sdl.Mix_GroupCount(-1)


def set_num_channels(count):
    """ set_num_channels(count) -> None
    set the total number of playback channels
    """


def pause():
    """pause(): return None

       temporarily stop playback of all sound channels"""
    check_mixer()
    sdl.Mix_Pause(-1)


def stop():
    """stop(): return None

      stop playback of all sound channels"""
    check_mixer()
    sdl.Mix_HaltChannel(-1)


def unpause():
    """unpause(): return None

       resume paused playback of sound channels"""
    check_mixer()
    sdl.Mix_Resume(-1)


def fadeout(time):
    """ fadeout(time) -> None
    fade out the volume on all sounds before stopping
    """


def set_reserved(count):
    """ set_reserved(count) -> None
    reserve channels from being automatically used
    """


@ffi.callback("void (*)(int channel)")
def _endsound_callback(channel):
    pass  # TODO
