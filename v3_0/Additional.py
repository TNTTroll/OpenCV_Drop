# --- Imports
import pygame as pg
from time import time

import Params as P


# --- Defs
def addText(text, pos, color=P.colors['text'], size=40, duration=30):
    P.texts.append(
        Text(text, pos, color, size, duration)
    )

def setText():
    i = 0
    while i < len(P.texts):
        text = P.texts[i]

        font = pg.font.SysFont(None, text.size)
        showText = font.render(str(text.text), True, text.color)
        P.screen.blit(showText, text.pos)

        if text.duration > 0: text.duration -= 1
        if text.duration == 0: P.texts.pop(i)
        i += 1


# --- Classes
class Text:
    def __init__(self, _text, _pos, _color, _size, _duration):
        self.text = _text
        self.pos = _pos
        self.color = _color
        self.size = _size
        self.duration = _duration


class FPS:
    def __init__(self, _name, _color):
        self.startTime = time()
        self.frameCount = 0
        self.name = _name
        self.color = f"\033[{_color}m"

    def get(self):
        self.frameCount += 1
        deltaT = time() - self.startTime
        if deltaT != 0:
            f = self.frameCount / deltaT
            print(
                f"{self.color}--- {self.name} ---\nTime {round(deltaT, 2)}, "
                f"Frames {self.frameCount}\nFPS {round(f, 2)}\n\033[0m")

    def reset(self):
        self.startTime = time()
        self.frameCount = 0

    def setName(self, _name):
        self.name = _name


class Orb:
    def __init__(self, _pos):
        self.pos = _pos

    def drop(self):
        if self.pos[1] < P.HEIGHT:
            self.pos[1] += 2
            pg.draw.circle(P.screen, P.colors['orb'], self.pos, 10)
            return 0
        return 1