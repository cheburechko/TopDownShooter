__author__ = 'thepunchy'

from game_object import GameObject
import struct

class Bullet(GameObject):
    SIZE = 5
    TYPE = 0
    DAMAGE = 1
    speed = 400
    STATE_FMT = "Ifff"
    STATE_SIZE = 17

    def __init__(self, position, angle, owner=None, objId=None):
        GameObject.__init__(self, position, angle, self.SIZE, self.TYPE, objId, solid=False)
        if owner is not None:
            self.owner = owner.id

    def move(self, delta):
        GameObject.move(self, scale=delta*self.speed, angle=self.angle)

    def getState(self):
        state = chr(self.type) + struct.pack(self.STATE_FMT, self.id,
                self.pos.x, self.pos.y, self.angle)
        return state

    def setState(self, state):
        self.pos.x = state[2]
        self.pos.y = state[3]
        self.angle = state[4]

    @classmethod
    def fromState(cls, state):
        obj = Bullet((0, 0), 0, None, objId=state[1])
        obj.setState(state)
        return obj