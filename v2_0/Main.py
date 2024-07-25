# --- Imports
import numpy
import cv2
import gc
from threading import Thread, Lock, Semaphore
from queue import Queue
from time import time
from copy import deepcopy

from v2_0.IMVApi_2 import *


# --- Variables
startTime = time()
countFrames = 0

FOURCC = cv2.VideoWriter_fourcc(*'FMP4')
FPS = 30.0
RESOLUTION = (1920, 1200)

colors = {"white": "1",
          "green": "1;32",
          "red": "1;31",
          "gray": "1;37",
          "blue": "1;34",
          "purple": "1;35"}

# <<< GRAB THREAD
saveImages1 = numpy.zeros((300, 1200, 1920), numpy.uint8)
saveImages2 = numpy.zeros((300, 1200, 1920), numpy.uint8)

isGoing = True
isFirstArr = isFilling = False
arrFill = 0

lock = Lock()
s = Semaphore(2)

# <<< TWO ARRAYS
staticPointer = 0
staticArr = numpy.zeros((100, 1200, 1920), numpy.uint8)
dynamicPointer = 0
dynamicArr = numpy.zeros((1000, 1200, 1920), numpy.uint8)

# <<< SAVE VIDEO WRITER
codecNames = ["DIVX", "XVID", "WMV1", "WMV2", "FMP4", "mp4v", "mpg1"]

# <<< QUEUE
q = Queue(maxsize=500)
going = True
inProgress = True
pointer = 0


# --- Class
class FPS:
    def __init__(self, _name, _color=colors['white']):
        self.startTime = time()
        self.frameCount = 0
        self.name = _name
        self.color = f"\033[{_color}m"

    def get(self):
        self.frameCount += 1
        deltaT = time() - self.startTime
        if (deltaT != 0):
            f = self.frameCount / deltaT
            print(f"{self.color}--- {self.name} ---\nTime {round(deltaT, 2)}, Frames {self.frameCount}\nFPS {round(f, 2)}\n\033[0m")

    def reset(self):
        self.startTime = time()
        self.frameCount = 0


# --- Main


'''
Links:
CODECS: https://ru.wikipedia.org/wiki/Windows_Media_Video
'''