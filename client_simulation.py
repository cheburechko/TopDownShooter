from models import *
from pygame.locals import *
from messages_shortcut import *
import pygame
from threading import Lock
from gui.gui import ScoreBoard, InputBox, ChatMessages
from graphics.GameObjectSprite import GameObjectSprite
from graphics.Camera import Camera

pygame.font.init()

class LocalSimulation():
    """
    This class is responsible for simulation of game
    and rendering stuff on screen
    """
    BACKGROUND = (0, 128, 0)
    NICK_COLOR = (0, 0, 0)
    NICK_OFFSET = 30
    PLAYER_BAR_OFFSET = 20
    TIME_SCALE = 0.001
    FRAMES_PER_SECOND = 60
    SCREEN_AREA = (1024, 768)
    BOUNDS = (0, 1024, 0, 768)

    PLAYER_IMG = pygame.image.load("resources/Player.png")
    BULLET_IMG= pygame.image.load("resources/Bullet.png")
    MOB_IMG = pygame.image.load("resources/Mob.png")

    BAR_HEIGHT = 5
    MOB_BAR_LENGTH = 50
    PLAYER_BAR_LENGTH = 30
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)

    def __init__(self):

        self.alive = True

        self.screen = pygame.display.set_mode(self.SCREEN_AREA, DOUBLEBUF)
        self.screen.fill(self.BACKGROUND)
        self.camera = Camera(self.screen.get_rect(), 0., 1.)
        self.clock = pygame.time.Clock()
        self.timestamp = pygame.time.get_ticks()
        self.timestamp_offset = 0
        self.lastUpdate = 0

        # Entities
        self.players = {}
        self.bullets = {}
        self.mobs = {}
        self.world = {Player.TYPE: self.players, Bullet.TYPE: self.bullets,
                      Mob.TYPE: self.mobs}
        self.solid_world = {}
        self.sprites = pygame.sprite.Group()
        self.playerID = None

        #Metadata
        self.playerEntries = {}

        #GUI
        self.playerNicks = {}
        self.scoreBoard = ScoreBoard(self.screen, self.playerEntries, self.drawBackground)
        self.showScore = False
        self.healthBars = {}
        self.mobBars = []
        self.playerBars = []
        self.textInput = InputBox(800, 20, 'Say: ', (100, 600))
        self.chat = ChatMessages(800, 20, 5, (100, 620))
        self.showInput = False

        #Prerender health bars
        bar = pygame.Surface((self.MOB_BAR_LENGTH, self.BAR_HEIGHT))
        bar.fill(self.RED)
        for i in range(Mob.HEALTH):
            b = bar.copy()
            b.fill(self.GREEN, pygame.Rect(0, 0,
                                           self.MOB_BAR_LENGTH * (i+1) / Mob.HEALTH ,
                                           self.BAR_HEIGHT))
            self.mobBars += [b]

        bar = pygame.Surface((self.PLAYER_BAR_LENGTH, self.BAR_HEIGHT))
        bar.fill(self.RED)
        for i in range(Player.HEALTH+1):
            b = bar.copy()
            b.fill(self.GREEN, pygame.Rect(
                0, 0,
                self.PLAYER_BAR_LENGTH * i / Player.HEALTH,
                self.BAR_HEIGHT))
            self.playerBars += [b]

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
            if ID in self.healthBars:
                self.drawBackground(self.screen, self.healthBars[ID])
                del self.healthBars[ID]
    
        self.sprites.remove(obj.sprite)
    
    def addObject(self, obj):
        ID = obj.id
        sprite = None
        if obj.type == Player.TYPE:
            self.players[ID] = obj
            sprite = GameObjectSprite(obj, self.PLAYER_IMG)
            self.healthBars[ID] = self.playerBars[0].get_rect()
        elif obj.type == Bullet.TYPE:
            self.bullets[ID] = obj
            sprite = GameObjectSprite(obj, self.BULLET_IMG)
        elif obj.type == Mob.TYPE:
            self.mobs[ID] = obj
            sprite = GameObjectSprite(obj, self.MOB_IMG)
            self.healthBars[ID] = self.mobBars[0].get_rect()
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
            delta = self.clock.tick(self.FRAMES_PER_SECOND)
            self.timestamp = pygame.time.get_ticks() + self.timestamp_offset
            # Clear

            # FPS
            self.drawBackground(self.screen, r)
            # Input
            self.textInput.clear(self.screen, self.drawBackground)
            # Scoreboard
            self.scoreBoard.clear()
            # Chat
            self.chat.clear(self.screen, self.drawBackground)
            # Player nicks
            for id in self.playerNicks:
                self.drawBackground(self.screen, self.playerNicks[id][1])
            # Bars
            for id in self.healthBars:
                self.drawBackground(self.screen, self.healthBars[id])
            #Sprites
            self.sprites.clear(self.screen, self.drawBackground)

            self.renderLock.acquire()
            # Extrapolation
            for id in self.players:
                self.players[id].step(controlled=self.playerID==id,
                                      timestamp=self.timestamp, delta=delta, real=False)

            for id in self.mobs:
                self.mobs[id].step(self.players, delta*self.TIME_SCALE, self.timestamp)

            for id in self.bullets:
                self.bullets[id].move(delta*self.TIME_SCALE)

            # Drawing
            if self.playerID in self.players:
                self.camera.move(self.players[self.playerID].pos)
            #Sprites
            self.sprites.update(self.camera)
            self.sprites.draw(self.screen)
            #Bars
            for id in self.mobs:
                if id in self.healthBars:
                    self.healthBars[id].center = self.camera.transform((self.mobs[id].pos.x,
                                                  self.mobs[id].pos.y + Mob.SIZE))
                    self.screen.blit(self.mobBars[self.mobs[id].health-1],
                                     self.healthBars[id].topleft)

            for id in self.players:
                if id in self.healthBars:
                    self.healthBars[id].center = self.camera.transform((self.players[id].pos.x,
                                                  self.players[id].pos.y + self.PLAYER_BAR_OFFSET))
                    self.screen.blit(self.playerBars[self.players[id].health],
                                     self.healthBars[id].topleft)

            # Nicks
            for id in self.playerNicks:
                self.playerNicks[id][1].center = self.camera.transform((self.players[id].pos.x,
                                                  self.players[id].pos.y+self.NICK_OFFSET))
                self.screen.blit(self.playerNicks[id][0], self.playerNicks[id][1].topleft)
            #Chat
            self.chat.draw(self.timestamp, self.messages, self.playerEntries, self.screen)
            self.messages = []
            #Scoreboard
            if self.showScore:
                self.scoreBoard.draw()
            # Input
            if self.showInput:
                self.textInput.draw(self.screen)
            #FPS
            self.screen.blit(fps, (0, 0))

            fps = self.playerFont.render(str(int(self.clock.get_fps())), True, (0,0,0))
            r = fps.get_rect()
            r.topleft = (0, 0)


            self.renderLock.release()

            pygame.display.flip()

    def sync(self, list):
        if list.timestamp < self.lastUpdate:
            return
        self.lastUpdate = list.timestamp

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

    FRAMES_PER_SECOND = 60

    def __init__(self, client, sim):
        self.firing = False
        self.k_right = self.k_left = self.k_up = self.k_down = 0
        self.alive = True
        self.clock = pygame.time.Clock()
        self.client = client
        self.sim = sim
        self.chatting = False

    def processInputForever(self):

        while self.alive:
            delay = self.clock.tick(self.FRAMES_PER_SECOND)
            timestamp = self.sim.timestamp

            if self.chatting:
                ans = self.sim.textInput.update(pygame.event.get())
                if ans is not None:
                    self.chatting = False
                    self.sim.showInput = False
                    msg = ChatMessage(msg=ans, id=self.sim.playerID)
                    msg.timestamp = timestamp
                    self.client.send(msg.toString())
            else:
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
                        elif event.key == K_RETURN:
                            self.chatting = down
                            self.sim.showInput = down

            msg = InputMessage()
            if self.k_right: msg.setButton(InputMessage.RIGHT)
            if self.k_left: msg.setButton(InputMessage.LEFT)
            if self.k_up: msg.setButton(InputMessage.UP)
            if self.k_down: msg.setButton(InputMessage.DOWN)
            if self.firing: msg.setButton(InputMessage.FIRE)

            msg.setCursor(self.sim.camera.reverse_transform(pygame.mouse.get_pos()))
            msg.msecs = delay
            msg.timestamp = timestamp

            self.client.send(msg.toString())
            self.sim.processInput(msg)