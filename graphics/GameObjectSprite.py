__author__ = 'thepunchy'

import math
import pygame
from game_objects.mob import Mob
class GameObjectSprite(pygame.sprite.Sprite):

    def __init__(self, entity, image):
        pygame.sprite.Sprite.__init__(self)
        self.entity = entity
        self.entity.sprite = self
        self.src_image = image
        self.image = image
        self.rect = image.get_rect()

    def update(self, camera):
        self.image = pygame.transform.rotozoom(self.src_image,
                                               (-camera.angle-self.entity.angle)-90,
                                               camera.scale)
        self.rect = self.image.get_rect()
        self.rect.center = camera.transform(self.entity.pos)
