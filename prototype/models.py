import math, pygame, random

class GameObject(pygame.sprite.Sprite):
    ID = 0

    @classmethod
    def getID(cls):
        cls.ID += 1
        return cls.ID - 1

    def __init__(self, image, position, angle, size, objType, objId=None, solid=True):
        pygame.sprite.Sprite.__init__(self)
        self.x = position[0]
        self.y = position[1]
        self.angle = angle
        self.size = size
        self.solid = solid

        if objId is None:
            self.id = GameObject.getID()
        else:
            self.id = objId

        self.type = objType
        self.alive = True
        self.src_image = pygame.image.load(image)

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

    def move(self, vector=None, scale=None, angle=None, position=None, solidWorld=None):
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

        if self.solid and (solidWorld is not None):
            cols = self.collisions(solidWorld)
            if len(cols) > 0:
                self.x = oldPos[0]
                self.y = oldPos[1]

    def rotate(self, angle=None, vector=None):
        if vector is not None:
            self.angle = math.atan2(vector[1] - self.y, vector[0] - self.x)
        elif angle is not None:
            self.angle = angle

    def update(self):
        self.image = pygame.transform.rotate(self.src_image, -self.angle / math.pi * 180 - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

class Bullet(GameObject):
    SIZE = 5
    TYPE = 0
    DAMAGE = 1
    speed = 400

    def __init__(self, position, angle, objId=None):
        GameObject.__init__(self, 'Bullet.png', position, angle, self.SIZE, self.TYPE, objId, solid=False)

    def move(self, delta):
        GameObject.move(self, scale=delta*self.speed, angle=self.angle)

class Player(GameObject):
    SIZE = 10
    SPEED = 150
    TYPE = 1
    HEALTH = 5
    FIRE_PERIOD = 125
    FIRE_DIST = 1
    def __init__(self, position, angle, objId=None):
        GameObject.__init__(self, 'Player.png', position, angle, self.SIZE, self.TYPE, objId)
        self.health = self.HEALTH
        self.next_shot = 0
        self.respPos = position

    def move(self, dx, dy, delta, solidWorld):
        GameObject.move(self, vector=(dx, dy), scale=delta*self.SPEED, solidWorld=solidWorld)

    def shoot(self, timestamp):
        if self.next_shot < timestamp:
            dist = self.size + self.FIRE_DIST + Bullet.SIZE
            bullet = Bullet((self.x + math.cos(self.angle) * dist,\
                         self.y + math.sin(self.angle) * dist),\
                         self.angle)
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
    def __init__(self, position, angle, objId=None):
        GameObject.__init__(self, 'Mob.png', position, angle, self.SIZE, self.TYPE, objId)
        self.health = self.HEALTH
        self.next_shot = 0
        self.target = None
        print self.id

    def step(self, players, delta, timestamp, solidWorld):
        if len(players) == 0:
            return None

        if self.target is None:
            self.target = players[int(random.random() * len(players))]
        if not self.target.alive:
            self.target = None
            return None

        self.rotate(vector=(self.target.x, self.target.y))
        GameObject.move(self, angle=self.angle, scale=self.SPEED*delta, solidWorld=solidWorld)

        if self.next_shot < timestamp:
            self.next_shot = timestamp + self.FIRE_PERIOD
            dist = self.size + self.FIRE_DIST + Bullet.SIZE
            bullet = Bullet((self.x + math.cos(self.angle) * dist,\
                         self.y + math.sin(self.angle) * dist),\
                         self.angle)
            return bullet

        return None


    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return True
        return False
