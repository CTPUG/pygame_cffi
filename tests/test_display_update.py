# Do partial updates of a window with in and out
# of bounds rectangles.

import pygame
from pygame.rect import Rect
import time

pygame.display.init()
video = pygame.display.set_mode((800, 600))

blue = pygame.Color(0, 0, 255, 255)

blit_surface = pygame.surface.Surface((800, 600))
blit_surface.fill(blue)
video.blit(blit_surface, (0, 0))

rect1 = Rect(-5, -5, 200, 100)
rect2 = (300, 200, 100, 100)
rect3 = (750, 550, 100, 100)
for rect in (rect1, rect2, rect3):
    pygame.display.update(rect)
    time.sleep(0.5)

pygame.display.update((rect1, rect2, (-5, -5, 1, 1), None, rect3))
time.sleep(0.5)
pygame.display.update()
