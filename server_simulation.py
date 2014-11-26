from models import *
import pygame, itertools
from messages import *
from metadata import PlayerEntry
from collisions import StateHistory

class ServerSimulation():
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

    def __init__(self):
        self.alive = True

        self.clock = pygame.time.Clock()
        self.timestamp = pygame.time.get_ticks()
        self.lastMob = 0

        self.world = {}
        self.world[Player.TYPE] = {}
        self.world[Bullet.TYPE] = {}
        self.world[Mob.TYPE] = {}
        self.solidWorld = {}
        self.allObjects = {}
        self.respawnQueue = {}
        self.removed = []
        self.history = StateHistory(self.FRAMES_PER_SECOND)

        self.playerEntries = {}

        self.verbose = False

    def addObject(self, obj):
        self.world[obj.type][obj.id] = obj
        self.allObjects[obj.id] = obj
        if obj.solid:
            self.solidWorld[obj.id] = obj

    def removeObject(self, obj):
        self.removed += [obj]
        del self.world[obj.type][obj.id]
        if obj.id in self.allObjects:
            del self.allObjects[obj.id]
        if obj.id in self.solidWorld:
            del self.solidWorld[obj.id]

    def getRandomPos(self):
        return \
            (random.random()*(self.BOUNDS[1]-self.BOUNDS[0]) + self.BOUNDS[0],
             random.random()*(self.BOUNDS[3] - self.BOUNDS[2]) + self.BOUNDS[2])

    def placeRandom(self, obj):
        obj.move(self.timestamp, position=self.getRandomPos())
        while len(self.history.collisions(obj, self.timestamp, True)) != 0:
            obj.move(position=self.getRandomPos())

    def addPlayer(self, msg):
        player = Player((0,0), 0,
                self.BOUNDS, self.history)
        self.placeRandom(player)
        self.addObject(player)
        self.playerEntries[player.id] = PlayerEntry(player.id, msg.name)
        return player.id

    def spawnMob(self):
        if self.timestamp > self.lastMob + self.MOB_RESPAWN_PERIOD and\
            len(self.world[Mob.TYPE]) < self.MAX_MOBS:
            mob = Mob((0,0), 0, self.BOUNDS, self.history)
            self.placeRandom(mob)
            self.addObject(mob)
            self.lastMob = self.timestamp

    def receiveInput(self, id, msg):
        player = self.world[Player.TYPE][id]
        player.addInput(msg)

        old_bullets = []
        lastT = player.lastTimestamp
        print 'Begin', lastT
        for t in self.history.getTimestamps(player.lastTimestamp):
            bullets = player.step(timestamp=t)
            print t
            new_bullets = []

            for bullet in bullets:
                self.addObject(bullet)

            for bullet in old_bullets + bullets:
                bullet.move(t, (t - lastT)*self.TIME_SCALE)
                cols = self.history.collisions(bullet, t, True)
                if (len(cols) > 0) and (bullet.owner != player.id):
                    if cols[0].type == Player.TYPE:
                        self.hitPlayer(cols[0], bullet)
                    else:
                        self.hitMob(cols[0], bullet)
                    if not cols[0].alive:
                        self.history.deleteState(cols[0], t)
                else:
                    new_bullets += [bullet]
                    self.history.updateState(bullet, t)

            old_bullets = new_bullets
            lastT = t

            cols = self.history.collisions(player, t)
            for c in cols:
                if c.type == Bullet.TYPE:
                    self.hitPlayer(player, c)
                    self.history.deleteState(c, t)
                    if not player.alive:
                        self.history.deleteState(player)

            self.history.updateState(player, t)

    def hitPlayer(self, player, bullet):
        bullet.alive = False
        self.removeObject(bullet)
        if player.hit(Bullet.DAMAGE):
            if bullet.owner in self.playerEntries:
                self.playerEntries[bullet.owner].score += self.PLAYER_COST

            self.playerEntries[player.id].deaths += 1
            self.respawnQueue[player.id] = (player, self.timestamp + self.PLAYER_RESPAWN_PERIOD)
            del self.solidWorld[player.id]
            del self.allObjects[player.id]

    def hitMob(self, mob, bullet):
        bullet.alive = False
        self.removeObject(bullet)
        if mob.hit(Bullet.DAMAGE):

            if bullet.owner in self.playerEntries:
                self.playerEntries[bullet.owner].score += self.MOB_COST

            self.removeObject(mob)

    def updateLatency(self, id, lag):
        self.playerEntries[id].latency = lag

    def removePlayer(self, id):
        self.removeObject(self.world[Player.TYPE][id])
        del self.playerEntries[id]

    def simulate(self):
        while self.alive:
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

            #for player in self.world[Player.TYPE].values():
            #    bullets = player.step(timestamp=self.timestamp)
            #    for bullet in bullets:
            #        self.addObject(bullet)

            for mob in self.world[Mob.TYPE].values():
                bullet = mob.step(self.world[Player.TYPE],
                                  delta*self.TIME_SCALE,
                                  self.timestamp)
                if bullet is not None:
                    self.addObject(bullet)

            for bullet in self.world[Bullet.TYPE].values():
                bullet.move(self.timestamp, delta*self.TIME_SCALE)
                if (bullet.x < self.BOUNDS[0]) or \
                    (bullet.x > self.BOUNDS[1]) or \
                    (bullet.y < self.BOUNDS[2]) or \
                    (bullet.y > self.BOUNDS[3]) or\
                        not bullet.alive:
                        self.removeObject(bullet)

            self.history.storeState(self.allObjects, self.timestamp)

            for player in self.world[Player.TYPE].values():
                if not player.alive:
                    continue
                for bullet in self.history.collisions(
                        player, self.timestamp):
                    if bullet.type == Bullet.TYPE:
                        self.hitPlayer(player, bullet)
                        if not player.alive:
                            break

            for mob in self.world[Mob.TYPE].values():
                for bullet in self.history.collisions(mob, self.timestamp):
                    if bullet.type == Bullet.TYPE:
                        self.hitMob(mob, bullet)
                        if not mob.alive:
                            break

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

    def getMeta(self):
        meta = ListMessage()
        meta.timestamp = self.timestamp
        for entry in self.playerEntries:
            meta.add(MetaMessage(self.playerEntries[entry]))
        return meta

