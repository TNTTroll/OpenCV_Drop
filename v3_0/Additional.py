# --- Imports
import cv2
import pygame as pg
from time import time
import requests
from bs4 import BeautifulSoup

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

def setTextCv(frame, text, pos, color=(240, 240, 240), size=1):
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (pos[0], pos[1])
    thickness = 2
    outline = [(255 - x) for x in color]

    cv2.putText(frame, str(text), org, font,
                size, outline, thickness + 2, cv2.LINE_AA)
    cv2.putText(frame, str(text), org, font,
                size, color, thickness, cv2.LINE_AA)

def getText():
    resp = requests.get("https://anekdoty.ru/")
    soup = BeautifulSoup(resp.text, "lxml")
    ds = soup.findAll('ul', class_='item-list')[0].next('p')[0].text
    return str(ds).replace("-", "\n-").replace(". ", "\n.")


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