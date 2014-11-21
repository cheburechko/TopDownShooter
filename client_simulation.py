import pygame, sys, math, Queue, thread
from models import *
from pygame.locals import *
from messages import *
from udp import UDPClient
#import pygame.freetype as freetype
pygame.font.init()

class LocalSimulation():
    """
    This class is responsible for simulation of game
    and rendering stuff on screen
    """
    BACKGROUND = (0, 128, 0)
    TIME_SCALE = 0.001
    FRAMES_PER_SECOND = 60
    SCREEN_AREA = (1024, 768)

    def __init__(self, inputQ):

        self.inputQ = inputQ
        self.alive = True

        self.screen = pygame.display.set_mode(self.SCREEN_AREA, DOUBLEBUF)
        self.screen.fill(self.BACKGROUND)
        self.clock = pygame.time.Clock()
        self.timestamp = pygame.time.get_ticks()
        self.timestamp_offset = 0

        # Entities
        self.players = pygame.sprite.Group() 
        self.bullets = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.world = pygame.sprite.Group()
        self.solid_world = pygame.sprite.Group()

        # Fonts
        self.playerFont = pygame.font.SysFont("None", 24)
        self.chatFont = pygame.font.SysFont("None", 50)

        self.messages = []

    def drawBackground(self, surf, rect):
        surf.fill(self.BACKGROUND, rect)

    def removeObject(self, obj):
        if obj.type == Player.TYPE:
            self.players.remove(obj)
        elif obj.type == Bullet.TYPE:
            self.bullets.remove(obj)
        elif obj.type == Mob.TYPE:
            self.mobs.remove(obj)
        if obj.solid:
            self.solid_world.remove(obj)
    
        self.world.remove(obj)
    
    def addObject(self, obj):
        ID = obj.id
        if obj.type == Player.TYPE:
            self.players.add(obj)
        elif obj.type == Bullet.TYPE:
            self.bullets.add(obj)
        elif obj.type == Mob.TYPE:
            self.mobs.add(obj)
        if obj.solid:
            self.solid_world.add(obj)
    
        self.world.add(obj)

    def processInputForever(self):
        while self.alive:
            vert = horiz = 0
            msg = self.inputQ.get()
            if msg.type == Message.INPUT:
                self.player.addMessage(msg)
            elif msg.type == Message.CHAT:
                self.messages += [msg]
            elif mdg.type == Message.LIST:
                self.sync(msg)

    def setPlayer(self, player):
        self.player = player

                self.player.move(horiz, vert, msg.msecs*self.TIME_SCALE, self.solid_world)
        self.addObject(player)


    def renderForever(self):
        while self.alive:
            delta = self.clock.tick(self.FRAMES_PER_SECOND)
            t = pygame.time.get_ticks() + self.timestamp_offset

            for player in self.players:
                player.entity.

            for mob in self.mobs:
                mob.entity.step(self.players.sprites(), delta*self.TIME_SCALE, t)


            for bullet in self.bullets:
                bullet.move(delta*self.TIME_SCALE)
                if (bullet.x < 0) or (bullet.x > self.SCREEN_AREA[0]) or\
                    (bullet.y < 0) or (bullet.y > self.SCREEN_AREA[1]):
                        bullet.alive = False
                        self.removeObject(bullet)

            for player in self.players:
                for bullet in player.collisions(self.bullets):
                    bullet.alive = False
                    self.removeObject(bullet)
                    if (player.hit(Bullet.DAMAGE)):
                        player.respawn()
                        break

            for mob in self.mobs:
                for bullet in mob.collisions(self.bullets):
                    bullet.alive = False
                    self.removeObject(bullet)
                    if (mob.hit(Bullet.DAMAGE)):
                        self.removeObject(mob)

            self.world.clear(self.screen, self.drawBackground)
            self.world.update()
            self.world.draw(self.screen)

            pygame.display.flip()

class InputControl():

    FRAMES_PER_SECOND = 30

    def __init__(self, client, q):
        self.firing = False
        self.k_right = self.k_left = self.k_up = self.k_down = 0
        self.alive = True
        self.clock = pygame.time.Clock()
        self.client = client
        self.outputQ = q
        self.timestamp_offset = 0

    def processInputForever(self):

        while self.alive:
            delay = self.clock.tick(self.FRAMES_PER_SECOND)
            timestamp = pygame.time.get_ticks()

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
                        client.shutdown()
                        self.alive = False
                        break

            msg = InputMessage()
            if self.k_right: msg.setButton(InputMessage.RIGHT)
            if self.k_left: msg.setButton(InputMessage.LEFT)
            if self.k_up: msg.setButton(InputMessage.UP)
            if self.k_down: msg.setButton(InputMessage.DOWN)
            if self.firing: msg.setButton(InputMessage.FIRE)

            msg.setCursor(pygame.mouse.get_pos())
            msg.msecs = delay
            msg.timestamp = timestamp + self.timestamp_offset
            self.client.send(msg.toString())
            self.outputQ.put(msg)



# INITIALIZE
q = Queue.Queue()
sim = LocalSimulation(q)
client = UDPClient(('localhost', 7000), q)
ic = InputControl(client, q)

player = Player((100, 100), 0)
sim.setPlayer(player)

INITIAL_MOBS = 3
for i in range(INITIAL_MOBS):
    pos = (random.random()*sim.SCREEN_AREA[0], random.random()*sim.SCREEN_AREA[1])
    mob = Mob(pos, 0)
    sim.addObject(mob)
    if len(mob.collisions(sim.world)) > 0:
        mob.move(position=(random.random()*sim.SCREEN_AREA[0], random.random()*sim.SCREEN_AREA[1]))

thread.start_new_thread(sim.processInputForever, ())
thread.start_new_thread(client.receive, ())
thread.start_new_thread(client.keepAlive, ())
thread.start_new_thread(sim.renderForever, ())
ic.processInputForever()
