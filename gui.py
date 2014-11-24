import pygame

pygame.font.init()


class ScoreBoard():

    ENTRY_HEIGHT = 50
    NAME_WIDTH = 600
    SCORE_WIDTH = 100
    DEATHS_WIDTH = 100
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
        self.title = self.font.render("Scoreboard", True, self.TEXT_COLOR)
        self.titleTopLeft = (
            (self.WINDOW_WIDTH - self.title.get_rect().width) / 2,
             self.TOP_OFFSET)

    def clear(self):
        if self.active:
            self.background(self.screen, self.boardRect)
            self.active = False

    def draw(self):
        self.active = True
        windowHeight = self.ENTRY_HEIGHT * (len(self.entries) + 1)
        self.boardRect = pygame.Rect(self.boardTopLeft, (self.WINDOW_WIDTH, windowHeight))
        self.screen.fill(self.BOARD_COLOR, self.boardRect)
        self.screen.blit(self.title, self.titleTopLeft)
        entries = self.entries.values()

        for i in range(len(self.entries)):
            text = self.font.render(entries[i].name, True, self.TEXT_COLOR)
            self.screen.blit(text,
                (self.boardTopLeft[0], self.boardTopLeft[1]+self.ENTRY_HEIGHT*(i+1)))

            text = self.font.render(str(entries[i].score), True, self.TEXT_COLOR)
            self.screen.blit(text,
                (self.boardTopLeft[0] + self.NAME_WIDTH,
                 self.boardTopLeft[1]+self.ENTRY_HEIGHT*(i+1)))

            text = self.font.render(str(entries[i].deaths), True, self.TEXT_COLOR)
            self.screen.blit(text,
                (self.boardTopLeft[0] + self.NAME_WIDTH + self.SCORE_WIDTH,
                 self.boardTopLeft[1]+self.ENTRY_HEIGHT*(i+1)))


