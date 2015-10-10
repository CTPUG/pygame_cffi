# Display a window for 2 seconds
# Fill a rectangle with blue and blit it to the screen

import pygame
import time

pygame.display.init()
video = pygame.display.set_mode((800, 600))

blue = pygame.Color(0, 0, 255, 255)

blit_surface = pygame.surface.Surface((200, 200))
blit_surface.fill(blue)
video.blit(blit_surface, (300, 200))
pygame.display.flip()

time.sleep(2)
