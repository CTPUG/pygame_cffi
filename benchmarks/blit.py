import random

import pygame

from base import Benchmark


width = 800
height = 600


class BlitBenchmark(Benchmark):

    def __init__(self, num_surfaces=100, surf_width=10, surf_height=10,
                 use_hw_surface=False):
        self.num_surfaces = int(num_surfaces)
        self.surf_dimensions = (int(surf_width), int(surf_height))
        self.use_hw_surface = bool(use_hw_surface)

    def setUp(self):
        self.blit_surf = pygame.Surface(self.surf_dimensions)
        self.blit_surf.fill((255, 0, 0))
        # all surfaces are inside screen boundary
        self.surf_positions = [(random.randrange(width - self.surf_dimensions[0]),
                               random.randrange(height - self.surf_dimensions[1]))
                               for i in xrange(self.num_surfaces)]

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

            for pos in self.surf_positions:
                self.screen.blit(self.blit_surf, pos)

            pygame.display.flip()
            clock.tick()


benchmark_class = BlitBenchmark
