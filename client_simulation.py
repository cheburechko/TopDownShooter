from models import *
from pygame.locals import *
from messages import *
import pygame
from threading import Lock
from gui import ScoreBoard

pygame.font.init()

class LocalSimulation():
    """
    This class is responsible for simulation of game
    and rendering stuff on screen
    """
    BACKGROUND = (0, 128, 0)
    NICK_COLOR = (0, 0, 0)
    NICK_OFFSET = 15;
    TIME_SCALE = 0.001
    FRAMES_PER_SECOND = 60
    SCREEN_AREA = (1024, 768)
    BOUNDS = (0, 1024, 0, 768)
    PLAYER_IMG = pygame.image.load("resources/Player.png")
    BULLET_IMG= pygame.image.load("resources/Bullet.png")
    MOB_IMG = pygame.image.load("resources/Mob.png")

    def __init__(self):

        self.alive = True

        self.screen = pygame.display.set_mode(self.SCREEN_AREA, DOUBLEBUF)
        self.screen.fill(self.BACKGROUND)
        self.clock = pygame.time.Clock()
        self.timestamp = pygame.time.get_ticks()
        self.timestamp_offset = 0

        # Entities
        self.players = {}
        self.bullets = {}
        self.mobs = {}
        self.world = {Player.TYPE: self.players, Bullet.TYPE: self.bullets,
                      Mob.TYPE: self.mobs}
        self.solid_world = {}
        self.sprites = pygame.sprite.Group()

        self.playerID = None
        self.playerEntries = {}
        self.playerNicks = {}

        self.scoreBoard = ScoreBoard(self.screen, self.playerEntries, self.drawBackground)
        self.showScore = False

        self.renderLock = Lock()

        # Fonts
        self.playerFont = pygame.font.SysFont("None", 24)
        self.chatFont = pygame.font.SysFont("None", 50)

        self.messages = []

    def drawBackground(self, surf, rect):
        surf.fill(self.BACKGROUND, rect)

    def removeObject(self, obj):
        ID = obj.id
        if obj.type == Player.TYPE:
            del self.players[ID]
            if ID in self.playerNicks:
                del self.playerNicks[ID]
            if ID in self.playerEntries:
                del self.playerEntries[ID]
        elif obj.type == Bullet.TYPE:
            del self.bullets[ID]
        elif obj.type == Mob.TYPE:
            del self.mobs[ID]
        if obj.solid:
            del self.solid_world[ID]
    
        self.sprites.remove(obj.sprite)
    
    def addObject(self, obj):
        ID = obj.id
        sprite = None
        if obj.type == Player.TYPE:
            self.players[ID] = obj
            sprite = GameObjectSprite(obj, self.PLAYER_IMG)
        elif obj.type == Bullet.TYPE:
            self.bullets[ID] = obj
            sprite = GameObjectSprite(obj, self.BULLET_IMG)
        elif obj.type == Mob.TYPE:
            self.mobs[ID] = obj
            sprite = GameObjectSprite(obj, self.MOB_IMG)
        if obj.solid:
            self.solid_world[ID] = obj
    
        self.sprites.add(sprite)

    def processInput(self, msg):
        if msg.type == Message.INPUT:
            if self.playerID is not None and self.playerID in self.players:
                self.players[self.playerID].addInput(msg)
        elif msg.type == Message.CHAT:
            self.messages += [msg]
        elif msg.type == Message.LIST:
            self.sync(msg)
        elif msg.type == Message.CONNECT:
            self.setPlayer(int(msg.name))

    def setPlayer(self, id):
        self.playerID = id

    def renderForever(self):
        fps = self.playerFont.render(str(self.clock.get_fps()), True, (0,0,0))
        r = fps.get_rect()
        r.topleft = (0, 0)
        while self.alive:

            self.drawBackground(self.screen, r)

            self.scoreBoard.clear()
            for id in self.playerNicks:
                self.drawBackground(self.screen, self.playerNicks[id][1])

            delta = self.clock.tick(self.FRAMES_PER_SECOND)
            self.timestamp = pygame.time.get_ticks() + self.timestamp_offset

            self.renderLock.acquire()

            for id in self.players:
                self.players[id].step(controlled=self.playerID==id,
                                      timestamp=self.timestamp, delta=delta, real=False)

            for id in self.mobs:
                self.mobs[id].step(self.players, delta*self.TIME_SCALE, self.timestamp)

            for id in self.bullets:
                self.bullets[id].move(delta*self.TIME_SCALE)

            self.sprites.clear(self.screen, self.drawBackground)
            self.sprites.update()
            self.sprites.draw(self.screen)


            for id in self.playerNicks:
                self.playerNicks[id][1].center = (self.players[id].x,
                                                  self.players[id].y+self.NICK_OFFSET)
                self.screen.blit(self.playerNicks[id][0], self.playerNicks[id][1].topleft)

            if self.showScore:
                self.scoreBoard.draw()

            self.screen.blit(fps, (0, 0))

            fps = self.playerFont.render(str(int(self.clock.get_fps())), True, (0,0,0))
            r = fps.get_rect()
            r.topleft = (0, 0)


            self.renderLock.release()

            pygame.display.flip()

    def sync(self, list):

        self.renderLock.acquire()
        for msg in list.msgs:
            if msg.type == Message.ENTITY:
                state = GameObject.unpackState(msg.state)
                if state[1] in self.world[state[0]]:
                    self.world[state[0]][state[1]].setState(state)
                else:
                    obj = GameObject.fromState(state)
                    if state[1] == Player.TYPE:
                        obj.lastTimestamp = list.timestamp
                    if state[1] != Bullet.TYPE:
                        obj.area = self.BOUNDS
                        obj.solids = self.solid_world

                    self.addObject(obj)
            elif msg.type == Message.REMOVE:
                if msg.id in self.world[msg.objType]:
                    self.removeObject(self.world[msg.objType][msg.id])
            elif msg.type == Message.META:
                if msg.entry.id not in self.playerNicks:
                    nick = self.playerFont.render(msg.entry.name, True, self.NICK_COLOR)
                    rect = nick.get_rect()
                    self.playerNicks[msg.entry.id] = (nick, rect)

                self.playerEntries[msg.entry.id] = msg.entry

        self.renderLock.release()



class InputControl():

    FRAMES_PER_SECOND = 20

    def __init__(self, client, sim):
        self.firing = False
        self.k_right = self.k_left = self.k_up = self.k_down = 0
        self.alive = True
        self.clock = pygame.time.Clock()
        self.client = client
        self.sim = sim

    def processInputForever(self):

        while self.alive:
            delay = self.clock.tick(self.FRAMES_PER_SECOND)
            timestamp = self.sim.timestamp

            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    self.firing = True
                elif event.type == MOUSEBUTTONUP:
                    self.firing = False
                elif event.type == KEYDOWN or event.type == KEYUP:
                    down = event.type == KEYDOWN
                    if event.key == K_d: self.k_right = down
                    elif event.key == K_a: self.k_left = down
                    elif event.key == K_w: self.k_up = down
                    elif event.key == K_s: self.k_down = down
                    elif event.key == K_ESCAPE: 
                        self.client.shutdown()
                        self.alive = False
                        break
                    elif event.key == K_TAB:
                        self.sim.showScore = down

            msg = InputMessage()
            if self.k_right: msg.setButton(InputMessage.RIGHT)
            if self.k_left: msg.setButton(InputMessage.LEFT)
            if self.k_up: msg.setButton(InputMessage.UP)
            if self.k_down: msg.setButton(InputMessage.DOWN)
            if self.firing: msg.setButton(InputMessage.FIRE)

            msg.setCursor(pygame.mouse.get_pos())
            msg.msecs = delay
            msg.timestamp = timestamp

            self.client.send(msg.toString())
            self.sim.processInput(msg)