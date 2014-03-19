import os
import random

import pygame


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
        self.rect = pygame.Rect(self.x, self.y, img.get_w(), img.get_h())


def collide_sprites(sprite1, sprite2):
    # first check if rects overlap
    if sprite1 is sprite2 or (not sprite1.rect.colliderect(sprite2.rect)):
        return False

    # if they overlap, do more accurate bitmask check
    offset_x = sprite2.x - sprite1.x
    offset_y = sprite2.y - sprite1.y
    if offset_y < 0:
        offset_y = -offset_y
        range_y = min(sprite2.rect.h - offset_y, sprite1.rect.h)
        if offset_x < 0:
            offset_x = -offset_x
            for i in range(range_y):
                if (sprite2.mask[i + offset_y] << offset_x) & sprite1.mask[i] > 0:
                    return True
        else:
            for i in range(range_y):
               if sprite2.mask[i + offset_y] & (sprite1.mask[i] << offset_x) > 0:
                    return True
    else:
        range_y = min(sprite2.rect.h, sprite1.rect.h - offset_y)
        if offset_x < 0:
            offset_x = -offset_x
            for i in range(range_y):
                if (sprite2.mask[i] << offset_x) & sprite1.mask[i + offset_y] > 0:
                    return True
        else:
            for i in range(range_y):
               if sprite2.mask[i] & (sprite1.mask[i + offset_y] << offset_x) > 0:
                    return True


def compute_bitmask(surf):
    colorkey = surf.get_colorkey()
    bitmask = [0 for y in xrange(surf.get_h())]
    for i in xrange(surf.get_h()):
        for j in xrange(surf.get_w()):
            col = surf.get_at((j, i))
            if colorkey:
                if col != colorkey:
                    bitmask[i] += 2^j
            elif col.a >= 1:
                bitmask[i] += 2^j
    return bitmask


def main(clock, num_sprites=10):
    pygame.init()
    num_sprites = int(num_sprites)
    sprite_img = pygame.image.load(IMAGE_PATH)
    sprite_bitmask = compute_bitmask(sprite_img)
    sprite_group = pygame.sprite.Group()
    draw = False
    for i in range(num_sprites):
        sprite = Sprite(sprite_img, sprite_bitmask,
                        (random.randrange(WIDTH - sprite_img.get_w()),
                         random.randrange(HEIGHT - sprite_img.get_h())))
        sprite.add(sprite_group)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.Font(None, 16)
    surf1 = font.render('sprite1', True, (255, 255, 255), (0, 0, 0))
    surf2 = font.render('sprite2', True, (255, 255, 255), (0, 0, 0))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        colliding = pygame.sprite.groupcollide(sprite_group, sprite_group,
                                               False, False, collide_sprites)

        if draw:
            sprite_group.draw(screen)
            for sprite, sprites in colliding.iteritems():
                if len(sprites) > 0:
                    pygame.draw.rect(screen, (255, 0, 0), sprite.rect, 1)
                    screen.blit(surf1, sprite.rect.topleft)
                    for s in sprites:
                        pygame.draw.rect(screen, (255, 0, 0), s.rect, 1)
                        screen.blit(surf2, s.rect.topleft)
            pygame.display.flip()

        clock.tick()

    pygame.quit()
