from models import *
import pygame, itertools, random
from messages_shortcut import *
from metadata import PlayerEntry
from geometry_shortcut import *
from libs.Vec2D import Vec2d
from level_generators.SparseLevelGenerator import SparseLevelGenerator

class ServerSimulation(object):
    """
    This class simulates all of the game events
    """

    FRAMES_PER_SECOND = 60
    SCREEN_AREA = (1024, 768)
    BOUNDS = (0, 1024, 0, 768)
    TIME_SCALE = 0.001
    MAX_MOBS = 0
    MOB_RESPAWN_PERIOD = 3000
    PLAYER_RESPAWN_PERIOD = 3000
    PLAYER_COST = 5
    MOB_COST = 1

    def __init__(self, level=None):
        self.alive = True

        self.clock = pygame.time.Clock()
        self.timestamp = pygame.time.get_ticks()
        self.lastMob = 0

        self.world = {}
        self.world[Player.TYPE] = {}
        self.world[Bullet.TYPE] = {}
        self.world[Mob.TYPE] = {}
        self.level = {}
        self.solidWorld = {}
        self.respawnQueue = {}
        self.removed = []
        self.playerAdded = False

        self.playerEntries = {}

        self.verbose = True
        
        self.levelGenerator = SparseLevelGenerator()
        self.levelGenerator.corridorGenerator.min_width = 55
        self.levelGenerator.corridorGenerator.max_width = 100
        self.levelGenerator.corridorGenerator.max_curvature = 1. / 200.
        self.levelGenerator.roomGenerator.minVertices = 4
        self.levelGenerator.roomGenerator.maxVertices = 10
        self.levelGenerator.minRoomSize = 100
        self.levelGenerator.roomNumber = 20
        self.levelGenerator.area = ((0, 0), (2000, 2000))

        self.generateLevel(level)


    def generateLevel(self, level=None):
        # level = Walls(Wireframe((0,0), 0,
        #                           [(0,0), (0,self.SCREEN_AREA[1]),
        #                            self.SCREEN_AREA, (self.SCREEN_AREA[0], 0)]))
        if level is None:
            level_shape = self.levelGenerator.generate()
            level = Walls(level_shape)
            self.level[level.id] = level
            self.solidWorld[level.id] = level.shape
        else:
            for msg in level.msgs:
                entity = GameObject.fromState(msg.state)
                self.level[entity.id] = entity
                self.solidWorld[entity.id] = entity.shape

    def addObject(self, obj):
        self.world[obj.type][obj.id] = obj
        if obj.solid:
            self.solidWorld[obj.id] = obj.shape

    def removeObject(self, obj):
        self.removed += [obj]
        del self.world[obj.type][obj.id]
        if obj.solid:
            del self.solidWorld[obj.id]

    def getRandomPos(self):
        while True:
            pos = (random.uniform(self.levelGenerator.area[0][0], self.levelGenerator.area[1][1]),
             (random.uniform(self.levelGenerator.area[0][1], self.levelGenerator.area[1][1])))
            for room in self.level:
                if self.level[room].shape.encloses_point(pos):
                    return pos

    def placeRandom(self, obj):
        while obj.move(position=self.getRandomPos()):
            pass

    def addPlayer(self, msg):
        player = Player((0,0), 0,
                self.solidWorld)
        self.placeRandom(player)
        self.addObject(player)
        self.playerEntries[player.id] = PlayerEntry(player.id, msg.name)
        return player.id

    def spawnMob(self):
        if self.timestamp > self.lastMob + self.MOB_RESPAWN_PERIOD and\
            len(self.world[Mob.TYPE]) < self.MAX_MOBS:
            mob = Mob((0,0), 0, self.solidWorld)
            self.placeRandom(mob)
            self.addObject(mob)
            self.lastMob = self.timestamp

    def receiveInput(self, id, msg):
        self.world[Player.TYPE][id].addInput(msg)

    def updateLatency(self, id, lag):
        self.playerEntries[id].latency = lag

    def removePlayer(self, id):
        self.removeObject(self.world[Player.TYPE][id])
        del self.playerEntries[id]

    def simulate(self):
        while self.alive:
            if self.verbose:
                print self.clock.get_fps()
            delta = self.clock.tick(self.FRAMES_PER_SECOND)
            self.timestamp = pygame.time.get_ticks()

            self.spawnMob()

            respawned = []
            for id in self.respawnQueue:
                player ,t = self.respawnQueue[id]
                if t <= self.timestamp:
                    player.respawn()
                    self.placeRandom(player)
                    respawned += [id]

            for id in respawned:
                del self.respawnQueue[id]

            for player in self.world[Player.TYPE].values():
                bullets = player.step(timestamp=self.timestamp)
                for bullet in bullets:
                    self.addObject(bullet)

            for mob in self.world[Mob.TYPE].values():
                bullet = mob.step(self.world[Player.TYPE],
                                  delta*self.TIME_SCALE,
                                  self.timestamp)
                if bullet is not None:
                    self.addObject(bullet)

            for bullet in self.world[Bullet.TYPE].values():
                bullet.move(delta*self.TIME_SCALE)

            for player in self.world[Player.TYPE].values():
                if not player.alive:
                    continue
                for bullet in player.collisions(
                        self.world[Bullet.TYPE].values()):
                    bullet.alive = False
                    self.removeObject(bullet)
                    if player.hit(Bullet.DAMAGE):

                        if bullet.owner in self.playerEntries:
                            self.playerEntries[bullet.owner].score += self.PLAYER_COST

                        self.playerEntries[player.id].deaths += 1
                        self.respawnQueue[player.id] = (player, self.timestamp + self.PLAYER_RESPAWN_PERIOD)

                        break

            for mob in self.world[Mob.TYPE].values():
                for bullet in mob.collisions(
                        self.world[Bullet.TYPE].values()):
                    bullet.alive = False
                    self.removeObject(bullet)
                    if mob.hit(Bullet.DAMAGE):

                        if bullet.owner in self.playerEntries:
                            self.playerEntries[bullet.owner].score += self.MOB_COST

                        self.removeObject(mob)
                        break

            for room in self.level.values():
                for bullet in room.collisions(self.world[Bullet.TYPE].values()):
                    bullet.alive = False
                    self.removeObject(bullet)


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

    def getLevelState(self):
        state = ListMessage()
        state.timestamp = self.timestamp
        for obj in self.level.values():
            state.add(EntityMessage(obj))
        return state

    def getMeta(self):
        meta = ListMessage()
        meta.timestamp = self.timestamp
        for entry in self.playerEntries:
            meta.add(MetaMessage(self.playerEntries[entry]))
        return meta

