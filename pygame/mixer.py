""" pygame module for loading and playing sounds """

import math

from pygame._sdl import sdl, ffi
from pygame._error import SDLError
from pygame.base import register_quit
import pygame.mixer_music as music
from pygame.mixer_music import check_mixer
from pygame.rwobject import (rwops_encode_file_path, rwops_from_file,
                             rwops_from_file_path)


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
        self.endevent = sdl.SDL_NOEVENT


class Channel(object):
    """Channel(id): return Channel
       Create a Channel object for controlling playback"""

    def __init__(self, channel):
        self.chan = int(channel)

    def __repr__(self):
        return '<Chan(%i)>' % self.chan

    def play(self, sound, loops=0, maxtime=-1, fade_ms=0):
        """play Sound on this channel"""
        # Note: channelnum will equal self.chan
        if fade_ms > 0:
            channelnum = sdl.Mix_FadeInChannelTimed(self.chan,
                                                    sound.chunk, loops,
                                                    fade_ms, maxtime)
        else:
            channelnum = sdl.Mix_PlayChannelTimed(self.chan,
                                                  sound.chunk, loops,
                                                  maxtime)
        if channelnum != -1:
            sdl.Mix_GroupChannel(channelnum, sound._chunk_tag)
        _channeldata[channelnum].sound = sound
        _channeldata[channelnum].queue = None

    def get_busy(self):
        check_mixer()
        return sdl.Mix_Playing(self.chan) != 0

    def stop(self):
        check_mixer()
        sdl.Mix_HaltChannel(self.chan)

    def pause(self):
        check_mixer()
        sdl.Mix_Pause(self.chan)

    def unpause(self):
        check_mixer()
        sdl.Mix_Resume(self.chan)

    def get_volume(self):
        check_mixer()
        volume = sdl.Mix_Volume(self.chan, -1)
        return volume / 128.0

    def set_volume(self, lvolume, rvolume=None):
        check_mixer()
        # This logic differs a bit from pygames because we can use a better
        # sentinal value
        if rvolume is None:
            # No Panning
            if sdl.Mix_SetPanning(self.chan, 255, 255) == 0:
                raise SDLError.from_sdl_error()
            volume = int(lvolume * 128)
        else:
            # Panning
            left = int(lvolume * 255)
            right = int(rvolume * 255)
            if sdl.Mix_SetPanning(self.chan, left, right) == 0:
                raise SDLError.from_sdl_error()
            volume = 128
        sdl.Mix_Volume(self.chan, volume)

    def fadeout(self, time):
        """ fadeout(time) -> None
        stop playback after fading channel out
        """
        check_mixer()
        sdl.Mix_FadeOutChannel(self.chan, time)

    def get_sound(self, ):
        """ get_sound() -> Sound
        get the currently playing Sound
        """
        return _channeldata[self.chan].sound

    def queue(self, sound):
        """ queue(Sound) -> None
        queue a Sound object to follow the current
        """
        # if nothing is playing
        if _channeldata[self.chan].sound is None:
            channelnum = sdl.Mix_PlayChannelTimed(self.chan, sound.chunk,
                                                  0, -1)
            if channelnum != -1:
                sdl.Mix_GroupChannel(channelnum, sound._chunk_tag)
            _channeldata[channelnum].sound = sound
        # sound is playing, queue new sound
        else:
            _channeldata[self.chan].queue = sound

    def get_queue(self):
        """ get_queue() -> Sound
        return any Sound that is queued
        """
        return _channeldata[self.chan].queue

    def set_endevent(self, event_id=sdl.SDL_NOEVENT):
        """ set_endevent() -> None
        have the channel send an event when playback stops
        """
        _channeldata[self.chan].endevent = event_id

    def get_endevent(self):
        """ get_endevent() -> type
        get the event a channel sends when playback stops
        """
        return _channeldata[self.chan].endevent


class Sound(object):
    """Sound(filename) -> Sound
    Sound(file=filename) -> Sound
    Sound(buffer) -> Sound
    Sound(buffer=buffer) -> Sound
    Sound(object) -> Sound
    Sound(file=object) -> Sound
    Sound(array=object) -> Sound
    Create a new Sound object from a file or buffer object
    """

    def __init__(self, obj=None, **kwargs):
        check_mixer()
        self.chunk = None

        # nasty mangling of parameters!
        # if 1 position arg: could be filename, file or buffer
        # if 1 keyword arg: could be filename, file, buffer or array where
        # filename and file use the same keyword 'file'
        if obj is not None:
            if kwargs:
                raise TypeError("Sound takes either 1 positional or "
                                "1 keyword argument")

            filename = None
            buff = None
            err = None
            if isinstance(obj, basestring):
                filename = obj
                if not isinstance(obj, unicode):
                    buff = obj
            elif isinstance(obj, file):
                rwops = rwops_from_file(obj)
                self.chunk = sdl.Mix_LoadWAV_RW(rwops, 1)
            else:
                buff = obj

            if filename is not None:
                try:
                    filename = rwops_encode_file_path(filename)
                    rwops = rwops_from_file_path(filename)
                    self.chunk = sdl.Mix_LoadWAV_RW(rwops, 1)
                except SDLError as e:
                    err = e

            if not self.chunk and buff is not None:
                raise NotImplementedError("Loading from buffer not "
                                          "implemented yet")
                # TODO: check if buff implements buffer interface.
                # If it does, load from buffer. If not, re-raise
                # error from filename if filename is not None.

        else:
            if len(kwargs) != 1:
                raise TypeError("Sound takes either 1 positional or "
                                "1 keyword argument")

            arg_name = kwargs.keys()[0]
            arg_value = kwargs[arg_name]
            if arg_name == 'file':
                if isinstance(arg_value, basestring):
                    filename = rwops_encode_file_path(arg_value)
                    rwops = rwops_from_file_path(filename, 'rb')
                else:
                    rwops = rwops_from_file(arg_value)
                self.chunk = sdl.Mix_LoadWAV_RW(rwops, 1)
            elif arg_name == 'buffer':
                if isinstance(arg_name, unicode):
                    raise TypeError("Unicode object not allowed as "
                                    "buffer object")
                raise NotImplementedError("Loading from buffer not "
                                          "implemented yet")
            elif arg_name == 'array':
                raise NotImplementedError("Loading from array not "
                                          "implemented yet")
            else:
                raise TypeError("Unrecognized keyword argument '%s'" % arg_name)

        # pygame uses the pointer address as the tag to ensure
        # uniqueness, we use id for the same effect
        # Since we don't have the some automatic casting rules as
        # C, we explicitly cast to int here. This matches pygames
        # behaviour, so we're bug-compatible
        self._chunk_tag = ffi.cast("int", id(self.chunk))
        if not self.chunk:
            raise SDLError.from_sdl_error()

    def __del__(self):
        if self.chunk:
            sdl.Mix_FreeChunk(self.chunk)

    def play(self, loops=0, maxtime=-1, fade_ms=0):
        """play(loops=0, maxtime=-1, fade_ms=0) -> Channel
        begin sound playback"""
        if fade_ms > 0:
            channelnum = sdl.Mix_FadeInChannelTimed(-1, self.chunk, loops,
                                                    fade_ms, maxtime)
        else:
            channelnum = sdl.Mix_PlayChannelTimed(-1, self.chunk, loops,
                                                  maxtime)
        if channelnum < 0:
            # failure
            return None

        _channeldata[channelnum].sound = self
        _channeldata[channelnum].queue = None
        sdl.Mix_Volume(channelnum, 128)
        sdl.Mix_GroupChannel(channelnum, self._chunk_tag)
        return Channel(channelnum)

    def stop(self):
        """stop() -> None
        stop sound playback
        """
        check_mixer()
        sdl.Mix_HaltGroup(self._chunk_tag)

    def get_volume(self):
        """get_volume(): return value

           get the playback volume"""
        check_mixer()
        volume = sdl.Mix_VolumeChunk(self.chunk, -1)
        return volume / 128.0

    def set_volume(self, volume):
        """set_volume(value): return None

           set the playback volume for this Sound"""
        check_mixer()
        sdl.Mix_VolumeChunk(self.chunk, int(volume * 128))

    def fadeout(self, time):
        """ fadeout(time) -> None
        stop sound playback after fading out
        """
        check_mixer()
        sdl.Mix_FadeOutGroup(self._chunk_tag, time)

    def get_num_channels(self):
        """ get_num_channels() -> count
        count how many times this Sound is playing
        """
        check_mixer()
        return sdl.Mix_GroupCount(self._chunk_tag)

    def get_length(self):
        """ get_length() -> seconds
        get the length of the Sound
        """
        check_mixer()
        frequency, format, channels = (ffi.new('int*'), ffi.new('uint16_t*'),
                                       ffi.new('int*'))
        sdl.Mix_QuerySpec(frequency, format, channels)
        if format == sdl.AUDIO_S8 or format == sdl.AUDIO_U8:
            mixerbytes = 1.0
        else:
            mixerbytes = 2.0
        numsamples = self.chunk.alen / mixerbytes / channels[0]
        return numsamples / frequency[0]

    def get_raw(self):
        """ get_raw() -> bytes
        return a bytestring copy of the Sound samples.
        """
        check_mixer()
        return ffi.buffer(ffi.cast('char*', self.chunk.abuf),
                          self.chunk.alen)[:]

    # TODO: array interface and buffer protocol implementation

    def __array_struct__(self, closure):
        raise NotImplementedError

    def __array_interface__(self, closure):
        raise NotImplementedError

    def _samples_address(self, closure):
        raise NotImplementedError


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
    if audioformat[0] & ~0xff:
        format_in_bits = -(audioformat[0] & 0xff)
    else:
        format_in_bits = audioformat[0] & 0xff
    return (int(freq[0]), format_in_bits, int(chan[0]))


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
    if not autoinit(frequency, size, channels, chunksize):
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


def find_channel(force=False):
    """find_channel(force=False): return Channel
    find an unused channel
    """
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
    check_mixer()
    global _numchanneldata, _channeldata
    if count > _numchanneldata:
        _channeldata.extend([ChannelData() for i in
                             range(count - _numchanneldata)])
        _numchanneldata = count
    sdl.Mix_AllocateChannels(count)


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
    check_mixer()
    sdl.Mix_FadeOutChannel(-1, time)


def set_reserved(count):
    """ set_reserved(count) -> None
    reserve channels from being automatically used
    """
    check_mixer()
    sdl.Mix_ReserveChannels(count)


@ffi.callback("void (*)(int channel)")
def _endsound_callback(channelnum):
    if not _channeldata:
        return

    data = _channeldata[channelnum]
    # post sound ending event
    if data.endevent != sdl.SDL_NOEVENT and sdl.SDL_WasInit(sdl.SDL_INIT_AUDIO):
        event = ffi.new('SDL_Event*')
        event.type = data.endevent
        if event.type >= sdl.SDL_USEREVENT and event.type < sdl.SDL_NUMEVENTS:
            event.user.code = channelnum
        sdl.SDL_PushEvent(event)

    if data.queue:
        sound_chunk = data.sound.chunk
        data.sound = data.queue
        data.queue = None
        channelnum = sdl.Mix_PlayChannelTimed(channelnum, sound_chunk, 0, -1)
        if channelnum != -1:
            sdl.Mix_GroupChannel(channelnum, data.sound._chunk_tag)
    else:
        data.sound = None
