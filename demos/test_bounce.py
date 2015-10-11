import sys, pygame

pygame.display.init()

size = width, height = 320, 240
speed = [2, 2]
black = pygame.Color(0, 0, 0, 255)

screen = pygame.display.set_mode(size)

try:
    ball = pygame.image.load("ball.gif")
except pygame._error.SDLError as e:
    print('Failed to load ball image: %s' % (e,))
    print('Are you in the correct directory?')
    ball = pygame.surface.Surface((100, 100))
    ball.fill(pygame.Color(0, 0, 255, 255))
ballrect = ball.get_rect()
clock = pygame.time.Clock()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.constants.QUIT:
            sys.exit()

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()
    clock.tick(40)
