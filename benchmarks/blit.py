import random

import pygame


width = 800
height = 600


def main(clock, num_surfaces=100, surf_width=10, surf_height=10):
    blit_surf = pygame.Surface((int(surf_width), int(surf_height)))
    blit_surf.fill((255, 0, 0))
    # all surfaces are inside screen boundary
    surf_positions = [(random.randrange(width - int(surf_width)),
                       random.randrange(height - int(surf_height)))
                      for i in xrange(int(num_surfaces))]

    pygame.init()
    screen = pygame.display.set_mode((width, height))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for pos in surf_positions:
            screen.blit(blit_surf, pos)

        pygame.display.flip()
        clock.tick()

    pygame.quit()