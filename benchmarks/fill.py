import random

import pygame


width = 800
height = 600


def main(clock, num_rects=100, rect_width=10, rect_height=10):
    # all rects are inside screen boundary
    rects = [pygame.Rect(random.randrange(width - int(rect_width)),
                         random.randrange(height - int(rect_height)),
                         rect_width, rect_height)
             for i in xrange(int(num_rects))]

    pygame.init()
    screen = pygame.display.set_mode((width, height))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for rect in rects:
            screen.fill((0, 255, 0), rect)

        pygame.display.flip()
        clock.tick()

    pygame.quit()
