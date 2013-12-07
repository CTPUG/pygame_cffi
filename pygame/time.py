""" pygame module for monitoring time
"""


class Clock(object):
    """ Clock() -> Clock
    create an object to help track time
    """

    def __init__(self):
        pass

    def tick(self, framerate=0):
        """ tick(framerate=0) -> milliseconds
        update the clock
        """
        #{ "tick", clock_tick, METH_VARARGS, DOC_CLOCKTICK },

    def get_fps(self):
        """ get_fps() -> float
        compute the clock framerate
        """
        #{ "get_fps", (PyCFunction) clock_get_fps,

    def get_time(self):
        """ get_time() -> milliseconds
        time used in the previous tick
        """
        #{ "get_time", (PyCFunction) clock_get_time, METH_NOARGS,
        #DOC_CLOCKGETTIME },

    def get_rawtime(self):
        """ get_rawtime() -> milliseconds
        actual time used in the previous tick
        """
        #{ "get_rawtime", (PyCFunction) clock_get_rawtime, METH_NOARGS,
        #DOC_CLOCKGETRAWTIME },

    def tick_busy_loop(self):
        """ tick_busy_loop(framerate=0) -> milliseconds
        update the clock
        """
        #{ "tick_busy_loop", clock_tick_busy_loop, METH_VARARGS,
        #DOC_CLOCKTICKBUSYLOOP },


def get_ticks():
    """ get_ticks() -> milliseconds
    get the time in milliseconds
    """


def set_timer(eventid, milliseconds):
    """set_timer(eventid, milliseconds) -> None
    repeatedly create an event on the event queue"
    """


def wait(milliseconds):
    """ wait(milliseconds) -> time
    pause the program for an amount of time
    """


def delay(milliseconds):
    """ delay(milliseconds) -> time
    pause the program for an amount of time
    """
