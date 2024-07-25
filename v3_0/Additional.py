# --- Imports
import pygame as pg
import Params as P


# --- Defs
def setText(text, pos, color=P.colors['text'], size=40):
    font = pg.font.SysFont(None, size)
    showText = font.render(str(text), True, color)
    P.screen.blit(showText, (pos[0], pos[1]))


# --- Classes
class Orb:
    def __init__(self, _pos):
        self.pos = _pos

    def drop(self):
        if self.pos[1] < P.HEIGHT:
            self.pos[1] += 2
            pg.draw.circle(P.screen, P.colors['orb'], self.pos, 10)
            return 0
        return 1