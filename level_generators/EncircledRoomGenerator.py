__author__ = 'thepunchy'

from geometry_shortcut import *
from libs.Vec2D import Vec2d
import random

class EncircledRoomGenerator(object):
    def __init__(self):
        self.minVertices = 4
        self.maxVertices = 10

    def generate(self, circle):
        correct = False
        while not correct:
            vertexNumber = random.randint(self.minVertices, self.maxVertices)
            arrow = Vec2d(0, circle.radius)
            angles = []
            for i in range(vertexNumber):
                angles += [random.uniform(0, 360)]
            angles.sort()

            points = []
            for angle in angles:
                points += [arrow.rotated(angle)]
            room = Wireframe(circle.pos, 0, points)
            correct = room.encloses_point(circle.pos)

        return room