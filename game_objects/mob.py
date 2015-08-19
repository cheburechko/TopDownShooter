from game_object import GameObject
from bullet import Bullet
import math, random, struct
from libs.Vec2D import Vec2d
from geometry_shortcut import Circle

class Mob(GameObject):
    SIZE = 25
    SPEED = 50
    TYPE = 2
    HEALTH = 3
    FIRE_PERIOD = 1000
    FIRE_DIST = 1
    STATE_FMT = "ffII"
    STATE_SIZE = 16

    def __init__(self, position, angle, solids, objId=None):
        GameObject.__init__(self, Circle(position, angle, self.SIZE), self.TYPE, objId,
                            solids=solids)
        self.health = self.HEALTH
        self.next_shot = 0
        self.target = None

    def getState(self):
        t = self.target
        if t is None:
            t = 2**32 - 1
        state = struct.pack(self.STATE_FMT,
                self.pos.x, self.pos.y, t, self.health)
        return state

    def setState(self, data):
        state = struct.unpack(self.STATE_FMT, data)
        self.pos.x = state[0]
        self.pos.y = state[1]
        self.target = state[2]
        if self.target == 2**32 - 1:
            self.target = None
        self.health = state[3]

    @classmethod
    def get_state_size(cls, data):
        return cls.STATE_SIZE

    @classmethod
    def fromState(cls, state, id):
        obj = Mob((0, 0), 0, None, id)
        obj.setState(state)
        return obj

    def step(self, players, delta, timestamp):
        if len(players) == 0:
            return None

        if self.target is None:
            self.target = players.keys()[int(random.random() * len(players.keys()))]
        if self.target not in players or players[self.target].health <= 0:
            self.target = None
            return None

        self.rotate(vector=players[self.target].pos)
        self.move(angle=self.angle, scale=self.SPEED*delta)

        if self.next_shot < timestamp:
            self.next_shot = timestamp + self.FIRE_PERIOD
            dist = self.shape.radius + self.FIRE_DIST + Bullet.SIZE
            bullet = Bullet(self.pos + Vec2d.shift(self.angle, dist),
                            self.angle, owner=self)
            return bullet

        return None


    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return True
        return False