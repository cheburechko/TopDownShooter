__author__ = 'thepunchy'

from game_object import GameObject
import struct
from geometry_shortcut import Shape

class Walls(GameObject):

    TYPE = 3

    def __init__(self, shape, objId=None):
        GameObject.__init__(self, shape, self.TYPE, objId, solid=True)

    def getState(self):
        return Shape.serialize(self.shape)

    def setState(self, state):
        shape = Shape.deserialize(state)
        if self.shape is None:
            self.shape = shape
        else:
            self.shape.pos = shape.pos
            self.shape.angle = shape.angle

    @classmethod
    def get_state_size(cls, data):
        return Shape.serialized_size(data)

    @classmethod
    def fromState(cls, state, id):
        obj = Walls(None, id)
        obj.setState(state)
        return obj
