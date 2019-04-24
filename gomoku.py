from __future__ import absolute_import, division, print_function
import pygame
from pygame.locals import *
from board import *


class Gomoku():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((530, 550))
        pygame.display.set_caption("Gomoku")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("ariel", 18)
        self.going = True
        self.board = Board()
        self.auto = False
        self.semiauto = True

    def loop(self):
        while self.going:
            self.update()
            self.draw()
            self.clock.tick(60)
        print("Game finished.")
        pygame.quit()

    def update(self):
        if self.auto:
            self.board.autoplay()
        for e in pygame.event.get():
            if e.type == QUIT:
                self.going = False
            if e.type == MOUSEBUTTONDOWN:
                self.auto = False
                if self.board.handle_key_event(e):
                    if self.semiauto:
                        self.board.semi_autoplay()
            if e.type == KEYDOWN:
                if e.key == K_RETURN:
                    self.auto = not self.auto
                if e.key == K_SPACE:
                    self.auto = False
                    self.board.restart()
                if e.key == K_m:
                    self.semiauto = not self.semiauto

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.board.draw(self.screen)
        if self.board.game_over:
            self.screen.blit(self.font.render(
                "{0} Won. Press Space to restart.".format("Black" if self.board.winner == 'b' else "White"), True,
                (0, 0, 0)), (10, 8))
        elif self.auto:
            self.screen.blit(self.font.render("AI vs AI autoplaying.", True, (0, 0, 0)), (10, 8))
        elif self.semiauto:
            self.screen.blit(self.font.render(
                "Click to put down a piece. Press Enter for autoplay. Press 'm' for manual play.".format(
                    "Black" if self.board.piece == 'b' else "White"), True, (0, 0, 0)), (10, 8))
        else:
            self.screen.blit(self.font.render(
                "Manual Play: {0}'s Turn. Click to put down a piece. Press 'm' to play against AI.".format(
                    "Black" if self.board.piece == 'b' else "White"), True, (0, 0, 0)), (10, 8))
        pygame.display.update()


if __name__ == '__main__':
    game = Gomoku()
    game.loop()
