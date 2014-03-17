import glob
import math
import os
import sys
import time
from threading import Thread, Event

import pygame


MAX_RUNTIME = 30


class Timer(Thread):
    def __init__(self, stop_flag, interval, callback, args):
        self.stop_flag = stop_flag
        self.interval = interval
        self.callback = callback
        self.args = args
        super(Timer, self).__init__()

    def run(self):
        start = time.time()
        while not self.stop_flag.wait(self.interval):
            self.callback(*self.args)
            if time.time() - start >= MAX_RUNTIME:
                pygame.event.post(pygame.event.Event(pygame.QUIT))


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


def run(module, sampling_interval=1.0):
    clock = pygame.time.Clock()
    stop_flag = Event()
    stats = Stats()
    timer = Timer(stop_flag, sampling_interval, sample_fps, (clock, stats))
    timer.start()
    module.main(clock)
    stop_flag.set()
    sys.stdout.write('%s\n' % stats)


if __name__ == '__main__':
    modules = [__import__(m.strip()) for m in sys.argv[1:]]
    if len(modules) == 0:
        directory, filename = os.path.split(os.path.abspath(__file__))
        for path in glob.iglob(os.path.join(directory, '*.py')):
            module = os.path.basename(path)
            if module != filename:
                modules.append(__import__(module[:-3]))
    
    for module in modules:
        run(module)
