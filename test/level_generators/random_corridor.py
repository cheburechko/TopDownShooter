__author__ = 'thepunchy'

from level_generators.RandomWalkCorridorGenerator import RandomWalkCorridorGenerator
from geometry_shortcut import *
import registry, pygame
from pygame.locals import *
from graphics.Camera import Camera
from level_generators.GenerationDebugger import GenerationDebugger

SCREEN_AREA = (800, 600)
BACKGROUND = (0, 128, 0)
COLOR = (0, 0, 0)

c1 = Circle((400, 100), 0, 75)
c2 = Circle((400, 500), 0, 75)
c3 = Circle((200, 300), 0, 75)
c4 = Circle((600, 300), 0, 75)
rooms = [c1, c2, c3, c4]

gen = RandomWalkCorridorGenerator()
gen.max_deviation = 30

screen = pygame.display.set_mode(SCREEN_AREA, DOUBLEBUF)
screen.fill(BACKGROUND)
camera = Camera(screen.get_rect(), 0, 1)

debug = GenerationDebugger(screen, BACKGROUND, camera, COLOR)

w = gen.generate_corridor(c1, c2, rooms, debug)

for shape in rooms + [w]:
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
            w = gen.generate_corridor(c1, c2, rooms, debug)
            for shape in rooms + [w]:
                shape.draw(screen, camera, COLOR)
            pygame.display.flip()

    pygame.time.wait(100)