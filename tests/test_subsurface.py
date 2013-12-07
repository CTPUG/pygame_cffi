# Simple pygame subsurface tests

import sys, pygame, os

pygame.display.init()

size = width, height = 640, 480
speed = [2, 2]
black = pygame.Color(0, 0, 0, 255)
red = pygame.Color(255, 0, 0, 255)
green = pygame.Color(0, 255, 0, 255)
blue = pygame.Color(0, 0, 255, 255)

screen = pygame.display.set_mode(size)

box = pygame.surface.Surface((300, 300))
box.fill(blue)
boxrect = box.get_rect()
clock = pygame.time.Clock()

change = box.subsurface((25, 25, 100, 100))
change2 = box.subsurface((150, 150, 125, 125))

seq = [red]*10 + [green]*10 + [blue]*10
index = 0

# Hack'ish resource loading fakery
ball = pygame.image.load(os.path.join(os.path.dirname(__file__), "ball.gif"))
ballrect = ball.get_rect()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.constants.QUIT:
            sys.exit()

    boxrect = boxrect.move(speed)
    if boxrect.left < 0 or boxrect.right > width:
        speed[0] = -speed[0]
    if boxrect.top < 0 or boxrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(box, boxrect)
    pygame.display.flip()
    clock.tick(40)
    change.fill(seq[index])
    if index > 15:
        change2.blit(ball, ballrect)
    else:
        change2.fill(blue)
    index += 1
    if index >= len(seq):
        index = 0
