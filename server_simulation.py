from models import *
import pygame, itertools
from messages import *
class ServerSimulation():
    """
    This class simulates all of the game events
    """

    FRAMES_PER_SECOND = 60
    SCREEN_AREA = (1024, 768)
    BOUNDS = (0, 1024, 0, 768)
    TIME_SCALE = 0.001

    def __init__(self):
        self.alive = True

        self.clock = pygame.time.Clock()
        self.timestamp = pygame.time.get_ticks()

        self.world = {}
        self.world[Player.TYPE] = {}
        self.world[Bullet.TYPE] = {}
        self.world[Mob.TYPE] = {}
        self.solidWorld = {}
        self.removed = []

    def addObject(self, obj):
        self.world[obj.type][obj.id] = obj
        self.solidWorld[obj.id] = obj

    def removeObject(self, obj):
        self.removed += [obj]
        del self.world[obj.type][obj.id]
        del self.solidWorld[obj.id]

    def getRandomPos(self):
        return \
            (random.random()*(self.BOUNDS[1]-self.BOUNDS[0]) + self.BOUNDS[0],
             random.random()*(self.BOUNDS[3] - self.BOUNDS[2]) + self.BOUNDS[2])

    def placeRandom(self, obj):
        w = self.solidWorld.values()
        while len(obj.collisions(w)) != 0:
            obj.move(position=self.getRandomPos())

    def addPlayer(self, msg):
        player = Player(self.getRandomPos(), 0,
                self.BOUNDS, self.solidWorld)
        self.placeRandom(player)
        self.addObject(player)
        return player.id

    def receiveInput(self, id, msg):
        self.world[Player.TYPE][id].addInput(msg)

    def removePlayer(self, id):
        self.removeObject(self.world[Player.TYPE][id])

    def simulate(self):
        while self.alive:
            delta = self.clock.tick(self.FRAMES_PER_SECOND)
            self.timestamp = pygame.time.get_ticks()

            for player in self.world[Player.TYPE].values():
                bullets = player.step(timestamp=self.timestamp)
                for bullet in bullets:
                    self.addObject(bullet)

            for mob in self.world[Mob.TYPE].values():
                bullet = mob.step(self.world[Player.TYPE].values(),
                                  delta*self.TIME_SCALE,
                                  self.timestamp)
                if bullet is not None:
                    self.addObject(bullet)

            for bullet in self.world[Bullet.TYPE].values():
                bullet.move(delta*self.TIME_SCALE)
                if (bullet.x < self.BOUNDS[0]) or \
                    (bullet.x > self.BOUNDS[1]) or \
                    (bullet.y < self.BOUNDS[2]) or \
                    (bullet.y > self.BOUNDS[3]):
                        bullet.alive = False
                        self.removeObject(bullet)

            for player in self.world[Player.TYPE].values():
                for bullet in player.collisions(
                        self.world[Bullet.TYPE].values()):
                    bullet.alive = False
                    self.removeObject(bullet)
                    if player.hit(Bullet.DAMAGE):
                        player.respawn()
                        self.placeRandom(player)
                        break

            for mob in self.world[Mob.TYPE].values():
                for bullet in mob.collisions(
                        self.world[Bullet.TYPE].values()):
                    bullet.alive = False
                    self.removeObject(bullet)
                    if (mob.hit(Bullet.DAMAGE)):
                        self.removeObject(mob)

    def getWorldState(self):
        state = ListMessage()
        state.timestamp = self.timestamp
        for obj in list(itertools.chain.from_iterable(
                [self.world[x].values() for x in self.world])):
            state.add(EntityMessage(obj))
        for obj in self.removed:
            state.add(RemoveMessage(obj.type, obj.id))
        self.removed = []
        return state

