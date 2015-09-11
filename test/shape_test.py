__author__ = 'thepunchy'

import registry
from geometry_shortcut import *
import pygame
from graphics.Camera import Camera
from pygame.locals import *
from libs.Vec2D import Vec2d
from geometry.merger import WireframeMerger

c1 = Circle((0,0), 0, 5)
c2 = Circle((4, 4), 0, 2)
c3 = Circle((9, 2), 0, 1)

s1 = Segment((4, 7), end=(7, 4))
s2 = Segment((4, 4), end=(7, 7))
s3 = Segment((0, 0), end=(5, 0))
s4 = Segment((2, 0), end=(3, 4))
s5 = Segment((0, 0), end=(0, 2))

print s1.intersect(s2)
print s2.intersect(s1)

w1 = Wireframe((3, 1.5), 0, [(-3, -3.5), (3, -3.5), (3, 3.5), (-3, 3.5)])
w2 = Wireframe((9, 2), -90, [(-2, 2), (2, 2), (0, -4)])

w4 = Wireframe((0, 0), 0, [(-1, -1), (-1, 1), (1, 1), (1, -1)])
pts = [(0, 0.5), (0, -0.5), (2, -0.5), (2, 0.5)]
w5 = Wireframe((0, 0), 0, pts)
print list(reversed(pts))
w6 = Wireframe((0, 0), 0, list(reversed(pts))[1:])
w7 = WireframeMerger().merge_exterior(w4, w5)
w7.pos += Vec2d(3, 0)
w8 = WireframeMerger().merge_exterior(w4, w6)
w8.pos += Vec2d(-3, 0)
w9 = WireframeMerger().merge_exterior(w5, w6)
w9.pos += Vec2d(0, -3)

shapes = [c1, c2, c3, s1, s2, s3, s4, s5, w1, w2, w4, w5, w6, w7, w8, w9]
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
print not s3.hit_test(s4)
print not s4.hit_test(s3)
print w1.encloses_point(s3.pos)
print w1.encloses_point(s3.end)
print w1.encloses_point(s5.pos)
print w1.encloses_point(s5.end)


run = True
while run:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            run = False
            break
    pygame.time.wait(100)
