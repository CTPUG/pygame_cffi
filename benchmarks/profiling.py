import os
import time


class StopProfiling(Exception):
    pass


class Profile(object):

    class NoopTimer(object):
        def __enter__(self):
            pass
        def __exit__(self, *args):
            pass

    class Timer(object):
        def __init__(self, profile, identifier):
            self.profile = profile
            self.identifier = identifier

        def __enter__(self):
            self._start = time.time()

        def __exit__(self, *args):
            elapsed = time.time() - self._start
            self.profile.segments.setdefault(self.identifier, (0.0, 0.0))
            total, n = self.profile.segments[self.identifier]
            self.profile.segments[self.identifier] = (
                total + elapsed,
                n + 1.0,

            )

    def __init__(self, delay=-1, period=10):
        self.segments = {}
        self.delay = delay
        self.created = time.time()
        self.period = period
        if delay != -1:
            self.period += delay

    def time(self, name):
        diff = time.time() - self.created
        if diff > self.period:
            raise StopProfiling
        elif diff > self.delay:
            return Profile.Timer(self, name)
        else:
            return Profile.NoopTimer()

    def __str__(self):
        s = ''
        max_key_len = 0
        for key in self.segments.keys():
            if len(key) > max_key_len:
                max_key_len = len(key)
        for key in sorted(self.segments.keys()):
            val = self.segments[key]
            total = val[0]
            n = val[1]
            average = val[0] / val[1]
            spaces = ' ' * (max_key_len - len(key)) 
            s += '%s:%s\t%.5f\t%d\t%.8f\n' % (key, spaces, total, n, average)
        return s


if __name__ == '__main__':
    profile = Profile()
    with profile.time('test'):
        time.sleep(1)
    print profile