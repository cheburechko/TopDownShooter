__author__ = 'thepunchy'

from game_object import GameObject
import struct
from geometry_shortcut import Shape

class Walls(GameObject):

    TYPE = 4

    def __init__(self, shape, objId=None):
        GameObject.__init__(self, shape, self.TYPE, objId, solid=True)

    def getState(self):
        return self.shape.serialize()

    def setState(self, state):
        self.shape = Shape.deserialize(state)

    @classmethod
    def get_state_size(cls, data):
        return Shape.serialized_size(data)

    @classmethod
    def fromState(cls, state, id):
        obj = Walls(None, id)
        obj.setState(state)
        return obj
