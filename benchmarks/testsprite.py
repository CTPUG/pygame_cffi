#!/usr/bin/env python
# like the testsprite.c that comes with sdl, this pygame version shows 
#   lots of sprites moving around.


import pygame, sys, os
from pygame.locals import *
from random import randint
#import pygame.joystick
from pygame.compat import xrange_

##import FastRenderGroup as FRG
import pygame.sprite as FRG

from base import Benchmark


if "-psyco" in sys.argv:
    try:
        import psyco
        psyco.full()
    except Exception:
        print ("No psyco for you!  psyco failed to import and run.")

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, '../examples/data')






# use this to use update rects or not.
#  If the screen is mostly full, then update rects are not useful.
update_rects = True
use_static = False
use_FastRenderGroup = False
flags = 0
use_rle = True
screen_dims = [640, 480]
use_alpha = False


##class Thingy(pygame.sprite.Sprite):
##    images = None
##    def __init__(self):
##        pygame.sprite.Sprite.__init__(self)
##        self.image = Thingy.images[0]
##        self.rect = self.image.get_rect()
##        self.rect.x = randint(0, screen_dims[0])
##        self.rect.y = randint(0, screen_dims[1])
##        #self.vel = [randint(-10, 10), randint(-10, 10)]
##        self.vel = [randint(-1, 1), randint(-1, 1)]
##
##    def move(self):
##        for i in [0, 1]:
##            nv = self.rect[i] + self.vel[i]
##            if nv >= screen_dims[i] or nv < 0:
##                self.vel[i] = -self.vel[i]
##                nv = self.rect[i] + self.vel[i]
##            self.rect[i] = nv

class Thingy(FRG.DirtySprite):
    images = None
    def __init__(self):
##        pygame.sprite.Sprite.__init__(self)
        FRG.DirtySprite.__init__(self)
        self.image = Thingy.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = randint(0, screen_dims[0])
        self.rect.y = randint(0, screen_dims[1])
        #self.vel = [randint(-10, 10), randint(-10, 10)]
        self.vel = [randint(-1, 1), randint(-1, 1)]
        self.dirty = 2

    def update(self):
        for i in [0, 1]:
            nv = self.rect[i] + self.vel[i]
            if nv >= screen_dims[i] or nv < 0:
                self.vel[i] = -self.vel[i]
                nv = self.rect[i] + self.vel[i]
            self.rect[i] = nv

class Static(FRG.DirtySprite):
    images = None
    def __init__(self):
        FRG.DirtySprite.__init__(self)
        self.image = Static.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = randint(0, 3*screen_dims[0]/4)
        self.rect.y = randint(0, 3*screen_dims[1]/4)


class TestspriteBenchmark(Benchmark):

    def setUp(self):
        pygame.display.init()


        self.screen = pygame.display.set_mode(screen_dims, flags)


        self.screen.fill([0,0,0])
        pygame.display.flip()
        sprite_surface = pygame.image.load(os.path.join(data_dir, "asprite.bmp"))
        sprite_surface2 = pygame.image.load(os.path.join(data_dir, "static.png"))

        if use_rle:
            sprite_surface.set_colorkey([0xFF, 0xFF, 0xFF], SRCCOLORKEY|RLEACCEL)
            sprite_surface2.set_colorkey([0xFF, 0xFF, 0xFF], SRCCOLORKEY|RLEACCEL)
        else:
            sprite_surface.set_colorkey([0xFF, 0xFF, 0xFF], SRCCOLORKEY)
            sprite_surface2.set_colorkey([0xFF, 0xFF, 0xFF], SRCCOLORKEY)

        if use_alpha:
            sprite_surface = sprite_surface.convert_alpha()
            sprite_surface2 = sprite_surface2.convert_alpha()
        else:
            sprite_surface = sprite_surface.convert()
            sprite_surface2 = sprite_surface2.convert()

        Thingy.images = [sprite_surface]
        if use_static:
            Static.images = [sprite_surface2]
        
        if len(sys.argv) > 1:
            try:
                numsprites = int(sys.argv[-1])
            except Exception:
                numsprites = 100
        else:
            numsprites = 100
        self.sprites = None
        if use_FastRenderGroup:
    ##        sprites = FRG.FastRenderGroup()
            self.sprites = FRG.LayeredDirty()
        else:
            if update_rects:
                self.sprites = pygame.sprite.RenderUpdates()
            else:
                self.sprites = pygame.sprite.Group()

        for i in xrange_(0, numsprites):
            if use_static and i%2==0:
                self.sprites.add(Static())
            self.sprites.add(Thingy())

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill([0,0,0])

    def tearDown(self):
        pygame.quit()

    def main(self, clock):

        done = False

        while not done:
            if not update_rects:
                self.screen.fill([0,0,0])

    ##        for sprite in sprites:
    ##            sprite.move()

            if update_rects:
                self.sprites.clear(self.screen, self.background)
            self.sprites.update()

            rects = self.sprites.draw(self.screen)
            if update_rects:
                pygame.display.update(rects)
            else:
                pygame.display.flip()


            for event in pygame.event.get():
                if event.type in [KEYDOWN, QUIT, JOYBUTTONDOWN]:
                    done = True

            clock.tick()


benchmark_class = TestspriteBenchmark
