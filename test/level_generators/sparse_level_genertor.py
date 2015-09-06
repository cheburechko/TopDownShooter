__author__ = 'thepunchy'

from level_generators.SparseLevelGenerator import SparseLevelGenerator
from libs.Vec2D import Vec2d
import registry, pygame
from pygame.locals import *
from graphics.Camera import Camera

SCREEN_AREA = (800, 600)
BACKGROUND = (0, 128, 0)
COLOR = (0, 0, 0)

gen = SparseLevelGenerator()
gen.area = (Vec2d(0, 0), Vec2d(SCREEN_AREA))

screen = pygame.display.set_mode(SCREEN_AREA, DOUBLEBUF)
screen.fill(BACKGROUND)
camera = Camera(screen.get_rect(), 0, 1)

gen.minRoomSize = 100
gen.roomNumber = 10

edges = gen.generate()
for shape in edges:
    shape.draw(screen, camera, COLOR)

pygame.display.flip()


run = True
while run:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            run = False
            break
        elif event.type == MOUSEBUTTONDOWN:
            screen.fill(BACKGROUND)
            shapes = gen.generate()
            for shape in shapes:
                shape.draw(screen, camera, COLOR)
            pygame.display.flip()
    pygame.time.wait(100)
