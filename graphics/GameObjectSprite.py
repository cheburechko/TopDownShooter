__author__ = 'thepunchy'

import math
import pygame

class GameObjectSprite(pygame.sprite.Sprite):

    def __init__(self, entity, image):
        pygame.sprite.Sprite.__init__(self)
        self.entity = entity
        self.entity.sprite = self
        self.src_image = image
        self.image = image
        self.image = image.get_rect()

    def update(self):
        self.image = pygame.transform.rotate(self.src_image, -self.entity.angle / math.pi * 180 - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.entity.x, self.entity.y)
