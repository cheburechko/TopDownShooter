import pygame, sys, math
from models import *
from pygame.locals import *
#import pygame.freetype as freetype
pygame.font.init()

BACKGROUND = (0, 128, 0)
TIME_SCALE = 0.001
FRAMES_PER_SECOND = 60
SCREEN_AREA = (1024, 768)
INITIAL_MOBS = 3

screen = pygame.display.set_mode(SCREEN_AREA, DOUBLEBUF)
screen.fill(BACKGROUND)
clock = pygame.time.Clock()

players = pygame.sprite.Group() 
bullets = pygame.sprite.Group()
mobs = pygame.sprite.Group()
world = pygame.sprite.Group()
solid_world = pygame.sprite.Group()

font = pygame.font.SysFont("None", 24)
title= font.render("Title", True, (0,0,0))
chat_font = pygame.font.SysFont("None", 50))

def clear_callback(surf, rect):
    surf.fill(BACKGROUND, rect)

def removeObject(obj):
    if obj.type == Player.TYPE:
        players.remove(obj)
    elif obj.type == Bullet.TYPE:
        bullets.remove(obj)
    elif obj.type == Mob.TYPE:
        mobs.remove(obj)
    if obj.solid:
        solid_world.remove(obj)

    world.remove(obj)

def addObject(obj):
    ID = obj.id
    if obj.type == Player.TYPE:
        players.add(obj)
    elif obj.type == Bullet.TYPE:
        bullets.add(obj)
    elif obj.type == Mob.TYPE:
        mobs.add(obj)
    if obj.solid:
        solid_world.add(obj)

    world.add(obj)

# INITIALIZE
player = Player((100, 100), 0)
addObject(player)
firing = False
k_right = k_left = k_up = k_down = 0
timestamp = pygame.time.get_ticks()

for i in range(INITIAL_MOBS):
    pos = (random.random()*SCREEN_AREA[0], random.random()*SCREEN_AREA[1])
    mob = Mob(pos, 0)
    addObject(mob)
    if len(mob.collisions(world)) > 0:
        mob.move(position=(random.random()*SCREEN_AREA[0], random.random()*SCREEN_AREA[1]))

# SIMULATION
r = title.get_rect()
while True:
    screen.fill(BACKGROUND, r)

    delta = clock.tick(FRAMES_PER_SECOND)
    timestamp = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
           firing = True
        elif event.type == MOUSEBUTTONUP:
            firing = False
        elif event.type == KEYDOWN or event.type == KEYUP:
            down = event.type == KEYDOWN
            if event.key == K_d: k_right = down
            elif event.key == K_a: k_left = down
            elif event.key == K_w: k_up = down
            elif event.key == K_s: k_down = down
            elif event.key == K_ESCAPE: sys.exit(0)

    player.move(k_right - k_left, -k_up + k_down, delta * TIME_SCALE, solid_world)
    player.rotate(vector=pygame.mouse.get_pos())

    for mob in mobs:
        bullet = mob.step(players.sprites(), delta*TIME_SCALE, timestamp, solid_world)
        if bullet is not None:
            addObject(bullet)

    for bullet in bullets:
        bullet.move(delta*TIME_SCALE)
        if (bullet.x < 0) or (bullet.x > SCREEN_AREA[0]) or\
            (bullet.y < 0) or (bullet.y > SCREEN_AREA[1]):
                bullet.alive = False
                removeObject(bullet)

    for bullet in player.collisions(bullets):
        bullet.alive = False
        removeObject(bullet)
        if (player.hit(Bullet.DAMAGE)):
            player.respawn()
            break

    for mob in mobs:
        for bullet in mob.collisions(bullets):
            bullet.alive = False
            removeObject(bullet)
            if (mob.hit(Bullet.DAMAGE)):
                removeObject(mob)
                break

    if firing:
        bullet = player.shoot(timestamp)
        if bullet is not None:
            addObject(bullet)

    world.clear(screen, clear_callback)
    world.update()
    world.draw(screen)

    r.center = (player.x, player.y + 15)
    screen.blit(title, r.topleft)

    pygame.display.flip()
