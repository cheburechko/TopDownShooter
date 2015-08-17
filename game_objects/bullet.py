__author__ = 'thepunchy'

from game_object import GameObject
import struct
from geometry_shortcut import Circle

class Bullet(GameObject):
    SIZE = 5
    TYPE = 0
    DAMAGE = 1
    speed = 400
    STATE_FMT = "fff"
    STATE_SIZE = 12

    def __init__(self, position, angle, owner=None, objId=None):
        GameObject.__init__(self, Circle(position, angle, self.SIZE), self.TYPE, objId, solid=False)
        if owner is not None:
            self.owner = owner.id

    def move(self, delta):
        GameObject.move(self, scale=delta*self.speed, angle=self.angle)

    def getState(self):
        state = struct.pack(self.STATE_FMT,
                self.pos.x, self.pos.y, self.angle)
        return state

    def setState(self, data):
        state = struct.unpack(self.STATE_FMT, data)
        self.pos.x = state[0]
        self.pos.y = state[1]
        self.angle = state[2]

    @classmethod
    def fromState(cls, state, id):
        obj = Bullet((0, 0), 0, None, objId=id)
        obj.setState(state)
        return obj

    @classmethod
    def get_state_size(cls, data):
        return cls.STATE_SIZE