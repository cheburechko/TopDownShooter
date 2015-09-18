__author__ = 'thepunchy'

from pygame.locals import *
import pygame

class GenerationDebugger(object):
    def __init__(self, screen=None, background=None, camera=None, color=None):
        self.screen = screen
        self.camera = camera
        self.background = (255, 255, 255)
        self.color= (0, 0, 0)
        if background is not None:
            self.background = background
        if color is not None:
            self.color = color

    def ready(self):
        return self.screen is not None and self.camera is not None

    def debug_output(self, shapes, message=""):
        if self.ready():
            self.screen.fill(self.background)
            for shape in shapes:
                shape.draw(self.screen, self.camera, self.color)
            pygame.display.flip()
            print message
            run = True
            while run:
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONDOWN:
                        run = False
