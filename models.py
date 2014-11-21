import math, pygame, random, struct
from messages import InputMessage


class GameObject():

    ID = 0
    STATE_FMT = "Ifffff"
    STATE_SIZE = 25
    OBJECT_TYPES = {}

    @classmethod
    def getID(cls):
        cls.ID += 1
        return cls.ID - 1

    def __init__(self, position, angle, size, objType, objId=None, solid=True,
            area=None, solids=None):
        self.x = position[0]
        self.y = position[1]
        self.angle = angle
        self.size = size
        self.solid = solid
        self.speedx = 0
        self.speedy = 0

        # Movement limiters
        self.area = area
        self.solids = solids

        if objId is None:
            self.id = GameObject.getID()
        else:
            self.id = objId

        self.type = objType
        self.alive = True

    def hitTest(self, obj):
        if (self.x - obj.x) ** 2 + (self.y - obj.y) ** 2 < (self.size + obj.size) ** 2:
            return True
        return False

    def collisions(self, obj_list):
        ans = []
        for obj in obj_list:
            if (self.id != obj.id) and self.hitTest(obj):
                ans += [obj]
        return ans

    def move(self, vector=None, scale=None, angle=None, position=None):
        oldPos = (self.x, self.y)
        resultingScale = 1
        if scale is not None:
            resultingScale = scale

        if vector is not None:
            self.x += vector[0] * resultingScale
            self.y += vector[1] * resultingScale
        elif angle is not None:
            self.x += math.cos(angle) * resultingScale
            self.y += math.sin(angle) * resultingScale
        elif position is not None:
            self.x = position[0]
            self.y = position[1]

        if self.solid:
            if self.solids is not None:
                cols = self.collisions(self.solids)
                if len(cols) > 0:
                    self.x = oldPos[0]
                    self.y = oldPos[1]
            # Boundaries
            if self.area is not None:
                if self.x < self.area[0] or self.x > self.area[1]:
                    self.x = oldPos[0]
                if self.y < self.area[2] or self.y > self.area[3]:
                    self.y = oldPos[1]

    def rotate(self, angle=None, vector=None):
        if vector is not None:
            self.angle = math.atan2(vector[1] - self.y, vector[0] - self.x)
        elif angle is not None:
            self.angle = angle


    def getState(self):
        state = chr(self.type) + struct.pack(self.STATE_FMT, self.id,
                self.x, self.y, self.speedx, self.speedy, self.angle)
        return state

    @classmethod
    def unpackState(cls, data):
        state = (ord(data[0]),) + struct.unpack(cls.STATE_FMT, data[1:])
        return state

    def setState(self, state):
        self.x = state[2]
        self.y = state[3]
        self.speedx = state[4]
        self.speedy = state[5]
        self.angle = state[6]

    @classmethod
    def fromState(cls, state):
        return cls.OBJECT_TYPES[state[0]].fromState(state)

    @classmethod
    def registerType(cls, type):
        cls.OBJECT_TYPES[type.TYPE] = type

class Bullet(GameObject):
    SIZE = 5
    TYPE = 0
    DAMAGE = 1
    speed = 400

    def __init__(self, position, angle, owner, objId=None):
        GameObject.__init__(self, position, angle, self.SIZE, self.TYPE, objId, solid=False)
        self.owner = owner.id

    def move(self, delta):
        GameObject.move(self, scale=delta*self.speed, angle=self.angle)

    @classmethod
    def fromState(cls, state):
        obj = Bullet((0, 0), 0, None, state[1])
        obj.setState(state)
        return obj

class Player(GameObject):
    SIZE = 10
    SPEED = 150
    TYPE = 1
    HEALTH = 5
    FIRE_PERIOD = 125
    FIRE_DIST = 1
    def __init__(self, position, angle, area, solids, objId=None):
        GameObject.__init__(self, position, angle, self.SIZE, self.TYPE, objId,
                area=area, solids=solids)

        self.health = self.HEALTH
        self.next_shot = 0
        self.respPos = position

        self.msgs = []
        self.currentMsg = None
        self.lastTimestamp = 0

    @classmethod
    def fromState(cls, state):
        obj = Player((0, 0), 0, None, None, state[1])
        obj.setState(state)
        return obj

    def addInput(self, msg):
        if self.currentMsg is not None:
            if msg.timestamp < self.currentMsg.timestamp:
                return

        self.msgs += [(msg.timestamp, msg)]
        self.msgs.sort(key=lambda x: x[0])

    def step(self, controlled=True, delta=0, timestamp=0, real=True):
        result = []
        if controlled:
            if self.currentMsg is None:
                if len(self.msgs) == 0:
                    return result
                self.currentMsg = self.msgs[0]
                del self.msgs[0]

            while self.currentMsg is not None:
                delta = timestamp - self.lastTimestamp
                if self.currentMsg.timestamp + self.currentMsg.msecs < timestamp:
                    delta = self.currentMsg.msecs - \
                            (self.lastTimestamp - self.currentMsg.timestamp)

                self.lastTimestamp += delta

                horiz = vert = 0
                if self.currentMsg.isSet(InputMessage.UP): 
                    vert -= 1
                if self.currentMsg.isSet(InputMessage.DOWN):
                    vert += 1
                if self.currentMsg.isSet(InputMessage.LEFT):
                    horiz -= 1
                if self.currentMsg.isSet(InputMessage.RIGHT):
                    horiz += 1

                self.rotate(vector=(self.currentMsg.cursorX, self.currentMsg.cursorY))
                if real:
                    if self.currentMsg.isSet(InputMessage.FIRE):
                        bullet = self.shoot(self.lastTimestamp)
                        if bullet is not None:
                            result += [bullet]

                self.move(horiz, vert, delta*0.001)
                if self.lastTimestamp < timestamp:
                    if len(self.msgs) == 0:
                        self.currentMsg = None
                    else:
                        self.currentMsg = self.msgs[0]
                        del self.msgs[0]
                else:
                    break
        else:
            self.move(self.speedx, self.speedy, delta)

    def move(self, dx, dy, delta):
        GameObject.move(self, vector=(dx, dy), scale=delta*self.SPEED)

    def shoot(self, timestamp):
        if self.next_shot < timestamp:
            dist = self.size + self.FIRE_DIST + Bullet.SIZE
            bullet = Bullet((self.x + math.cos(self.angle) * dist,
                             self.y + math.sin(self.angle) * dist),
                            self.angle, self)
            self.next_shot = timestamp + self.FIRE_PERIOD
            return bullet

        return None

    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return True
        return False

    def respawn(self):
        GameObject.move(self, position=self.respPos)
        self.health = self.HEALTH
        self.alive = True

class Mob(GameObject):
    SIZE = 25
    SPEED = 50
    TYPE = 2
    HEALTH = 3
    FIRE_PERIOD = 1000
    FIRE_DIST = 1
    def __init__(self, position, angle, area, solids, objId=None):
        GameObject.__init__(self, position, angle, self.SIZE, self.TYPE, objId,
                            area=area, solids=solids)
        self.health = self.HEALTH
        self.next_shot = 0
        self.target = None


    def fromState(cls, state):
        obj = Mob((0, 0), 0, None, None, state[1])
        obj.setState(state)
        return obj

    def step(self, players, delta, timestamp):
        if len(players) == 0:
            return None

        if self.target is None:
            self.target = players[int(random.random() * len(players))]
        if not self.target.alive:
            self.target = None
            return None

        self.rotate(vector=(self.target.x, self.target.y))
        GameObject.move(self, angle=self.angle, scale=self.SPEED*delta)

        if self.next_shot < timestamp:
            self.next_shot = timestamp + self.FIRE_PERIOD
            dist = self.size + self.FIRE_DIST + Bullet.SIZE
            bullet = Bullet((self.x + math.cos(self.angle) * dist,
                             self.y + math.sin(self.angle) * dist),
                            self.angle, self)
            return bullet

        return None


    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return True
        return False

class GameObjectSprite(pygame.sprite.Sprite):

    def __init__(self, entity, image):
        self.entity = entity
        self.entity.sprite = self
        self.src_image = image

    def update(self):
        self.image = pygame.transform.rotate(self.src_image, -self.entity.angle / math.pi * 180 - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.entity.x, self.entity.y)

GameObject.registerType(Mob)
GameObject.registerType(Player)
GameObject.registerType(Bullet)