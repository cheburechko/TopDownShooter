from game_object import GameObject
from bullet import Bullet
import math, random, struct

class Mob(GameObject):
    SIZE = 25
    SPEED = 50
    TYPE = 2
    HEALTH = 3
    FIRE_PERIOD = 1000
    FIRE_DIST = 1
    STATE_FMT = "IffII"
    STATE_SIZE = 21

    def __init__(self, position, angle, area, solids, objId=None):
        GameObject.__init__(self, position, angle, self.SIZE, self.TYPE, objId,
                            area=area, solids=solids)
        self.health = self.HEALTH
        self.next_shot = 0
        self.target = None

    def getState(self):
        t = self.target
        if t is None:
            t = 2**32 - 1
        state = chr(self.type) + struct.pack(self.STATE_FMT, self.id,
                self.x, self.y, t, self.health)
        return state

    def setState(self, state):
        self.x = state[2]
        self.y = state[3]
        self.target = state[4]
        if self.target == 2**32 - 1:
            self.target = None
        self.health = state[5]

    @classmethod
    def fromState(cls, state):
        obj = Mob((0, 0), 0, None, None, state[1])
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

        self.rotate(vector=(players[self.target].x, players[self.target].y))
        GameObject.move(self, angle=self.angle, scale=self.SPEED*delta)

        if self.next_shot < timestamp:
            self.next_shot = timestamp + self.FIRE_PERIOD
            dist = self.size + self.FIRE_DIST + Bullet.SIZE
            bullet = Bullet((self.x + math.cos(self.angle) * dist,
                             self.y + math.sin(self.angle) * dist),
                            self.angle, owner=self)
            return bullet

        return None


    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return True
        return False