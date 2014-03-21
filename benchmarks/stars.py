#!/usr/bin/env python

"""A simple starfield example. Note you can move the 'center' of
the starfield by leftclicking in the window. This example show
the basics of creating a window, simple pixel plotting, and input
event management"""


import random, math, pygame
from pygame.constants import KEYUP, K_ESCAPE, MOUSEBUTTONDOWN, QUIT

from base import Benchmark


#constants
WINSIZE = [640, 480]
WINCENTER = [320, 240]
NUMSTARS = 150


def init_star():
    "creates new star values"
    dir = random.randrange(100000)
    velmult = random.random()*.6+.4
    vel = [math.sin(dir) * velmult, math.cos(dir) * velmult]
    return vel, WINCENTER[:]


def initialize_stars():
    "creates a new starfield"
    stars = []
    for x in range(NUMSTARS):
        star = init_star()
        vel, pos = star
        steps = random.randint(0, WINCENTER[0])
        pos[0] = pos[0] + (vel[0] * steps)
        pos[1] = pos[1] + (vel[1] * steps)
        vel[0] = vel[0] * (steps * .09)
        vel[1] = vel[1] * (steps * .09)
        stars.append(star)
    move_stars(stars)
    return stars


def draw_stars(surface, stars, color):
    "used to draw (and clear) the stars"
    for vel, pos in stars:
        pos = (int(pos[0]), int(pos[1]))
        surface.set_at(pos, color)


def move_stars(stars):
    "animate the star values"
    for vel, pos in stars:
        pos[0] = pos[0] + vel[0]
        pos[1] = pos[1] + vel[1]
        if not 0 <= pos[0] <= WINSIZE[0] or not 0 <= pos[1] <= WINSIZE[1]:
            vel[:], pos[:] = init_star()
        else:
            vel[0] = vel[0] * 1.05
            vel[1] = vel[1] * 1.05


class StarsBenchmark(Benchmark):

    def setUp(self):
        "This is the starfield code"
        #create our starfield
        random.seed()
        self.stars = initialize_stars()
        #initialize and prepare screen
        pygame.display.init()
        self.screen = pygame.display.set_mode(WINSIZE)
        pygame.display.set_caption('pygame Stars Example')
        self.white = 255, 240, 200
        self.black = 20, 20, 40
        self.screen.fill(self.black)

    def tearDown(self):
        pygame.quit()

    def main(self, clock):
        #main game loop
        done = 0
        while not done:
            draw_stars(self.screen, self.stars, self.black)
            move_stars(self.stars)
            draw_stars(self.screen, self.stars, self.white)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                    done = 1
                    break
                elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                    WINCENTER[:] = list(e.pos)
            clock.tick()


benchmark_class = StarsBenchmark
