from threading import Thread, Event
import time

import pygame

from base import Benchmark


class Poster(Thread):

    def __init__(self, stop_flag):
        super(Poster, self).__init__()
        self.stop_flag = stop_flag

    def run(self):
        while not self.stop_flag.is_set():
            event = pygame.event.Event(pygame.USEREVENT)
            try_post = True
            # The pygame.event.post raises an exception if the event
            # queue is full. So wait a little bit, and try again.
            while try_post:
                try:
                    pygame.event.post(event)
                    try_post = False
                except:
                    time.sleep(0.0001)
                    try_post = True


class EventBenchmark(Benchmark):

    def __init__(self):
        self.stop_flag = Event()
        self.poster = Poster(self.stop_flag)

    def setUp(self):
        pygame.init()

    def tearDown(self):
        pygame.quit()

    def main(self, clock):
        running = True
        self.poster.start()
        total = 0
        while running:
            for e in pygame.event.get():
                total += 1
                if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and
                                             e.key == pygame.K_ESCAPE):
                    self.stop_flag.set()
                    running = False
                    break

            time.sleep(0.00001)
            clock.tick()
        print total


benchmark_class = EventBenchmark
