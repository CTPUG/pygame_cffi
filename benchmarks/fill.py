import random

import pygame

from base import Benchmark


width = 800
height = 600


class FillBenchmark(Benchmark):

    def __init__(self, num_rects=100, rect_width=10, rect_height=10,
                 use_hw_surface=False):
        self.num_rects = int(num_rects)
        self.rect_dimensions = (int(rect_width), int(rect_height))
        self.use_hw_surface = bool(use_hw_surface)

    def setUp(self):
        # all rects are inside screen boundary
        self.rects = [pygame.Rect(random.randrange(width - self.rect_dimensions[0]),
                                  random.randrange(height - self.rect_dimensions[1]),
                                  *self.rect_dimensions)
                      for i in xrange(self.num_rects)]

        pygame.init()
        if not self.use_hw_surface:
            self.screen = pygame.display.set_mode((width, height))
        else:
            self.screen = pygame.display.set_mode((width, height),
                                                  pygame.FULLSCREEN|
                                                  pygame.HWSURFACE)

    def tearDown(self):
        pygame.quit()

    def main(self, clock):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            for rect in self.rects:
                self.screen.fill((0, 255, 0), rect)

            pygame.display.flip()
            clock.tick()


benchmark_class = FillBenchmark
