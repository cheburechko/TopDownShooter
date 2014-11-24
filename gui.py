import pygame
from pygame.locals import *
pygame.font.init()


class ScoreBoard():

    ENTRY_HEIGHT = 50
    NAME_WIDTH = 500
    SCORE_WIDTH = 150
    DEATHS_WIDTH = 150
    WINDOW_WIDTH = NAME_WIDTH + SCORE_WIDTH + DEATHS_WIDTH
    TOP_OFFSET = 50
    BOARD_COLOR = (0, 0, 0)
    TEXT_COLOR = (255, 255, 255)

    def __init__(self, screen, entries, background):
        self.screen = screen
        self.entries = entries
        self.font = pygame.font.SysFont("None", self.ENTRY_HEIGHT)
        self.active = False

        screenRect = self.screen.get_rect()
        self.boardTopLeft = (
            (screenRect.width - self.WINDOW_WIDTH) / 2,
             self.TOP_OFFSET)
        self.background = background
        self.boardRect = pygame.Rect(0,0,0,0)

        self.titleName = self.font.render("Name", True, self.TEXT_COLOR)
        self.titleNameTopLeft = self.boardTopLeft
        self.titleScore = self.font.render("Score", True, self.TEXT_COLOR)
        self.titleScoreTopLeft = (
            self.titleNameTopLeft[0] + self.NAME_WIDTH, self.boardTopLeft[1]
        )
        self.titleDeaths = self.font.render("Deaths", True, self.TEXT_COLOR)
        self.titleDeathsTopLeft = (
            self.titleScoreTopLeft[0] + self.SCORE_WIDTH, self.boardTopLeft[1]
        )

    def clear(self):
        if self.active:
            self.background(self.screen, self.boardRect)
            self.active = False

    def draw(self):
        self.active = True
        windowHeight = self.ENTRY_HEIGHT * (len(self.entries) + 1)
        self.boardRect = pygame.Rect(self.boardTopLeft, (self.WINDOW_WIDTH, windowHeight))
        self.screen.fill(self.BOARD_COLOR, self.boardRect)
        self.screen.blit(self.titleName, self.titleNameTopLeft)
        self.screen.blit(self.titleScore, self.titleScoreTopLeft)
        self.screen.blit(self.titleDeaths, self.titleDeathsTopLeft)
        entries = self.entries.values()

        for i in range(len(self.entries)):
            text = self.font.render(entries[i].name, True, self.TEXT_COLOR)
            self.screen.blit(text,
                (self.boardTopLeft[0], self.boardTopLeft[1]+self.ENTRY_HEIGHT*(i+1)))

            text = self.font.render(str(entries[i].score), True, self.TEXT_COLOR)
            self.screen.blit(text,
                (self.titleScoreTopLeft[0],
                 self.boardTopLeft[1]+self.ENTRY_HEIGHT*(i+1)))

            text = self.font.render(str(entries[i].deaths), True, self.TEXT_COLOR)
            self.screen.blit(text,
                (self.titleDeathsTopLeft[0],
                 self.boardTopLeft[1]+self.ENTRY_HEIGHT*(i+1)))


class InputBox():

    BG_COLOR = (255, 255, 255)
    BORDER_COLOR = (0, 0, 0)
    BORDER_WIDTH = 1
    TEXT_COLOR = (0, 0, 0)

    def __init__(self, length, font, prompt, pos):
        self.length = length
        self.font = pygame.font.SysFont("None", font)
        char = self.font.render('_', True, self.TEXT_COLOR)
        self.chars = self.length / char.get_rect().width - len(prompt)
        self.promptImg = self.font.render(prompt, True, self.TEXT_COLOR)
        self.pos = pos
        self.rect = pygame.Rect(pos, (length, font))
        self.textPoint = (self.rect.left + self.promptImg.get_rect().width, self.rect.top)
        self.borderRect = pygame.Rect(
            pos[0] - self.BORDER_WIDTH,
            pos[1] - self.BORDER_WIDTH,
            length + self.BORDER_WIDTH*2,
            font   + self.BORDER_WIDTH*2)
        self.text = ''
        self.active = False

    def clear(self, screen, callback):
        if self.active:
            callback(screen, self.borderRect)

    def draw(self, screen):
        self.active = True
        screen.fill(self.BORDER_COLOR, self.borderRect)
        screen.fill(self.BG_COLOR, self.rect)
        screen.blit(self.promptImg, self.rect.topleft)
        text = self.text[-self.chars:]
        screen.blit(self.font.render(text, True, self.TEXT_COLOR), self.textPoint)

    def update(self, events):
        for event in events:
            if event.type != KEYDOWN:
                return None

            if event.key == K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == K_RETURN:
                text = self.text
                self.text = ''
                return text
            else:
                self.text += event.unicode
        #print self.text
        return None