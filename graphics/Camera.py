__author__ = 'thepunchy'

import math
from libs.Vec2D import Vec2d


class Camera:
    def __init__(self, viewport, angle, scale):
        self.viewport = viewport
        self.angle = angle
        self.scale = scale

    def move(self, pos):
        self.viewport.center = pos

    def rotate(self, angle):
        self.angle = angle

    def rescale(self, scale):
        self.scale = scale

    def transform(self, coords):
        new_point = (Vec2d(coords) - self.viewport.topleft) * self.scale
        return new_point.rotated(self.angle)

    def reverse_transform(self, coords):
        point = Vec2d(coords).rotated(-self.angle)
        return point / self.scale + self.viewport.topleft