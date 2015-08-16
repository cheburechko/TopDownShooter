import struct
import math

from messages_shortcut import InputMessage
from game_object import GameObject
from bullet import Bullet

class Player(GameObject):
    SIZE = 10
    SPEED = 150
    TYPE = 1
    HEALTH = 5
    FIRE_PERIOD = 125
    FIRE_DIST = 5
    STATE_FMT = "IfffffI"
    STATE_SIZE = 29

    def __init__(self, position, angle, area, solids, objId=None):
        GameObject.__init__(self, position, angle, self.SIZE, self.TYPE, objId,
                area=area, solids=solids)

        self.health = self.HEALTH
        self.next_shot = 0
        self.respPos = position

        self.msgs = []
        self.currentMsg = None
        self.lastTimestamp = 0

    def getState(self):
        state = chr(self.type) + struct.pack(self.STATE_FMT, self.id,
                self.x, self.y, self.speedx, self.speedy, self.angle, self.health)
        return state

    def setState(self, state):
        self.x = state[2]
        self.y = state[3]
        self.speedx = state[4]
        self.speedy = state[5]
        self.angle = state[6]
        self.health = state[7]

    @classmethod
    def fromState(cls, state):
        obj = Player((0, 0), 0, None, None, state[1])
        obj.setState(state)
        return obj

    def addInput(self, msg):
        if self.health <= 0:
            return

        if self.currentMsg is not None:
            if msg.timestamp < self.currentMsg.timestamp:
                return

        self.msgs += [(msg.timestamp, msg)]
        self.msgs.sort(key=lambda x: x[0])

    def step(self, controlled=True, delta=0, timestamp=0, real=True):
        if self.health <= 0:
            return []

        result = []
        if controlled:

            if self.currentMsg is None:
                if len(self.msgs) == 0:
                    return result
                self.currentMsg = self.msgs[0][1]
                del self.msgs[0]

            while self.currentMsg is not None:

                delta = timestamp - self.lastTimestamp
                if self.currentMsg.timestamp + self.currentMsg.msecs < timestamp:
                    delta = self.currentMsg.msecs - \
                            (self.lastTimestamp - self.currentMsg.timestamp)

                self.lastTimestamp += delta

                self.speedx = self.speedy = 0
                if self.currentMsg.isSet(InputMessage.UP):
                    self.speedy -= 1
                if self.currentMsg.isSet(InputMessage.DOWN):
                    self.speedy += 1
                if self.currentMsg.isSet(InputMessage.LEFT):
                    self.speedx -= 1
                if self.currentMsg.isSet(InputMessage.RIGHT):
                    self.speedx += 1

                self.rotate(vector=(self.currentMsg.cursorX, self.currentMsg.cursorY))
                self.move(vector=(self.speedx, self.speedy), scale=delta*0.001*self.SPEED)
                if real:
                    if self.currentMsg.isSet(InputMessage.FIRE):
                        bullet = self.shoot(self.lastTimestamp)
                        if bullet is not None:
                            result += [bullet]

                if self.lastTimestamp < timestamp:
                    if len(self.msgs) == 0:
                        self.currentMsg = None
                    else:
                        self.currentMsg = self.msgs[0][1]
                        del self.msgs[0]
                else:
                    break
        else:
            self.move(vector=(self.speedx, self.speedy), scale=delta*0.001*self.SPEED)
        #print self.x, self.y, self.speedx, self.speedy, self.SPEED*delta*0.001
        return result

    def shoot(self, timestamp):
        if self.next_shot < timestamp:
            dist = self.size + self.FIRE_DIST + Bullet.SIZE
            bullet = Bullet((self.x + math.cos(self.angle) * dist,
                             self.y + math.sin(self.angle) * dist),
                            self.angle, owner=self)
            self.next_shot = timestamp + self.FIRE_PERIOD
            return bullet

        return None

    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.msgs = []
            return True
        return False

    def respawn(self):
        #GameObject.move(self, position=self.respPos)
        self.health = self.HEALTH
        self.alive = True