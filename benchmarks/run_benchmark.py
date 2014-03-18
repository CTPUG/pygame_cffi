import math
import sys
import time
from threading import Thread, Event

import pygame


DEFAULT_SAMPLING_INTERVAL = 1.0
DEFAULT_MAX_RUNTIME = 30


class Timer(Thread):
    def __init__(self, stop_flag, interval, callback, max_runtime, args):
        self.stop_flag = stop_flag
        self.interval = interval
        self.callback = callback
        self.max_runtime = max_runtime
        self.args = args
        super(Timer, self).__init__()

    def run(self):
        start = time.time()
        while not self.stop_flag.wait(self.interval):
            self.callback(*self.args)
            if time.time() - start >= self.max_runtime:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                break


class Stats(object):
    def __init__(self):
        self.n = 0
        self.mean = 0.0
        self.m2 = 0.0
        self.min = float('inf')
        self.max = 0.0

    def add_sample(self, value):
        # online algorithm to compute running variance
        self.n += 1
        delta = value - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (value - self.mean)

        if value < self.min:
            self.min = value
        if value > self.max:
            self.max = value

    @property
    def variance(self):
        return self.m2 / (self.n - 1)

    def __str__(self):
        return '%s,%s,%s,%s' % (self.mean, self.min, self.max,
                                math.sqrt(self.variance))


def sample_fps(clock, stats):
    stats.add_sample(clock.get_fps())


def run(module, sampling_interval, max_runtime, args=()):
    clock = pygame.time.Clock()
    stop_flag = Event()
    stats = Stats()
    timer = Timer(stop_flag, sampling_interval, sample_fps,
                  max_runtime, (clock, stats))
    timer.start()
    module.main(clock, *args)
    stop_flag.set()
    sys.stdout.write('%s\n' % stats)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise RuntimeError("No benchmark module argument supplied.\n"
                           "Usage: python %s <bench_module> [options] [<bench_arg>, ...]"
                           % __file__)

    sampling_interval = DEFAULT_SAMPLING_INTERVAL
    max_runtime = DEFAULT_MAX_RUNTIME
    non_option_args = []
    i = 1  # skip script argument
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '-i':
            i += 1
            sampling_interval = float(sys.argv[i])
        elif arg == '-r':
            i += 1
            max_runtime = float(sys.argv[i])
        else:
            try:
                non_option_args.append(float(arg))
            except ValueError:
                non_option_args.append(arg)
        i += 1

    module = __import__(non_option_args[0])
    run(module, sampling_interval, max_runtime, args=non_option_args[1:])
