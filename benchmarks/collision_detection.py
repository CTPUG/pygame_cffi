import os
import random
import time

import pygame

from base import Benchmark


IMAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                          '../examples/data/player1.gif'))
WIDTH = 800
HEIGHT = 600


class Sprite(pygame.sprite.Sprite):

    def __init__(self, img, mask, pos):
        super(Sprite, self).__init__()
        self.image = img
        self.mask = mask
        self.x = pos[0]
        self.y = pos[1]
        self.rect = pygame.Rect(self.x, self.y, img.get_width(), img.get_height())


def collide_sprites(sprite1, sprite2):
    # first check if rects overlap
    if sprite1 is sprite2 or (not sprite1.rect.colliderect(sprite2.rect)):
        return False

    # if they overlap, do more accurate bitmask check
    offset_x = sprite2.x - sprite1.x
    offset_y = sprite2.y - sprite1.y
    if offset_y < 0:
        offset_y = -offset_y
        if sprite2.rect.bottom > sprite1.rect.bottom:
            range_y = sprite1.rect.h
        else:
            range_y = sprite2.rect.h - offset_y

        if offset_x < 0:
            offset_x = -offset_x
            for i in range(range_y):
                if (sprite2.mask[i + offset_y] & (sprite1.mask[i] >> offset_x)) > 0:
                    return True
        else:
            for i in range(range_y):
                if (sprite2.mask[i + offset_y] & (sprite1.mask[i] << offset_x)) > 0:
                    return True
    else:
        if sprite2.rect.bottom > sprite1.rect.bottom:
            range_y = sprite1.rect.h - offset_y
        else:
            range_y = sprite2.rect.h

        if offset_x < 0:
            offset_x = -offset_x
            for i in range(range_y):
                if ((sprite2.mask[i] << offset_x) & sprite1.mask[i + offset_y]) > 0:
                    return True
        else:
            for i in range(range_y):
                if ((sprite2.mask[i] >> offset_x) & sprite1.mask[i + offset_y]) > 0:
                    return True
    return False


def compute_bitmask(surf):
    colorkey = surf.get_colorkey()
    bitmask = [0 for y in xrange(surf.get_height())]
    for i in xrange(surf.get_height()):
        for j in xrange(surf.get_width()):
            col = surf.get_at((j, i))
            if colorkey:
                if col != colorkey:
                    bitmask[i] += 2**j
            elif col.a >= 1:
                bitmask[i] += 2**j
    return bitmask


class CollisionDetectionBenchmark(Benchmark):

    def __init__(self, num_sprites=10):
        self.num_sprites = num_sprites

    def setUp(self):
        sprite_img = pygame.image.load(IMAGE_PATH)
        sprite_bitmask = compute_bitmask(sprite_img)
        self.sprite_group = pygame.sprite.Group()
        for i in range(self.num_sprites):
            sprite = Sprite(sprite_img, sprite_bitmask,
                            (random.randrange(WIDTH - sprite_img.get_width()),
                             random.randrange(HEIGHT - sprite_img.get_height())))
            sprite.add(self.sprite_group)

        pygame.font.init()
        font = pygame.font.Font(None, 16)
        self.surf1 = font.render('sprite1', True, (255, 255, 255), (0, 0, 0))
        self.surf2 = font.render('sprite2', True, (255, 255, 255), (0, 0, 0))

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def tearDown(self):
        pygame.quit()

    def main(self, clock):
        draw = False
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                    draw = not draw
                    if not draw:
                        # clear the screen so that toggling is obvious
                        self.screen.fill((0, 0, 0))
                        pygame.display.flip()


            # n-squared collision - very inefficient but likely to be used nonetheless 
            colliding = pygame.sprite.groupcollide(self.sprite_group, self.sprite_group,
                                                   False, False, collide_sprites)

            if draw:
                self.sprite_group.draw(self.screen)
                for sprite, sprites in colliding.iteritems():
                    if len(sprites) > 0:
                        pygame.draw.rect(self.screen, (255, 0, 0), sprite.rect, 1)
                        self.screen.blit(self.surf1, sprite.rect.topleft)
                        for s in sprites:
                            pygame.draw.rect(self.screen, (255, 0, 0), s.rect, 1)
                            self.screen.blit(self.surf2, s.rect.topleft)
                pygame.display.flip()

            # avoid the frame time being too short
            time.sleep(0.0001)
            clock.tick()


benchmark_class = CollisionDetectionBenchmark
