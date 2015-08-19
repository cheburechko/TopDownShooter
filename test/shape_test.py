__author__ = 'thepunchy'

from geometry_shortcut import *
import pygame
from graphics.Camera import Camera
from pygame.locals import *
from libs.Vec2D import Vec2d

c1 = Circle((0,0), 0, 5)
c2 = Circle((4, 4), 0, 2)
c3 = Circle((9, 2), 0, 1)

s1 = Segment((4, 7), end=(7, 4.5))
s2 = Segment((4, 4), end=(7, 7))

w1 = Wireframe((3, 1.5), 0, [(-3, -3.5), (3, -3.5), (3, 3.5), (-3, 3.5)])
w2 = Wireframe((9, 2), -90, [(-2, 2), (2, 2), (0, -4)])

shapes = [c1, c2, c3, s1, s2, w1, w2]
SCREEN_AREA = (800, 600)
BACKGROUND = (0, 128, 0)
COLOR = (0, 0, 0)

screen = pygame.display.set_mode(SCREEN_AREA, DOUBLEBUF)
screen.fill(BACKGROUND)
camera = Camera(screen.get_rect(), 0, 30)
camera.move((0, 0))

for shape in shapes:
    shape.draw(screen, camera, COLOR)

pygame.display.flip()

print c1.hit_test(c2)
print not c1.hit_test(c3)
print not c2.hit_test(c3)
print s1.hit_test(s2)
print w1.hit_test(w2)
print w1.hit_test(c1)
print c1.hit_test(w1)
print w1.hit_test(c2)
print w1.hit_test(s2)
print not w1.hit_test(s1)
print not w2.hit_test(c3)



run = True
while run:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            run = False
            break
    pygame.time.wait(100)
