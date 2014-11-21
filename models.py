import math, pygame, random, struct
from messages import InputMessage
from game_object import GameObject



class Bullet(GameObject):
    SIZE = 5
    TYPE = 0
    DAMAGE = 1
    speed = 400

    def __init__(self, position, angle, owner=None, objId=None):
        GameObject.__init__(self, position, angle, self.SIZE, self.TYPE, objId, solid=False)
        if owner is not None:
            self.owner = owner.id

    def move(self, delta):
        GameObject.move(self, scale=delta*self.speed, angle=self.angle)

    @classmethod
    def fromState(cls, state):
        obj = Bullet((0, 0), 0, None, objId=state[1])
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
                if real:
                    if self.currentMsg.isSet(InputMessage.FIRE):
                        bullet = self.shoot(self.lastTimestamp)
                        if bullet is not None:
                            result += [bullet]

                self.move(self.speedx, self.speedy, delta*0.001)
                if self.lastTimestamp < timestamp:
                    if len(self.msgs) == 0:
                        self.currentMsg = None
                    else:
                        self.currentMsg = self.msgs[0][1]
                        del self.msgs[0]
                else:
                    break
            return result
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
        pygame.sprite.Sprite.__init__(self)
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