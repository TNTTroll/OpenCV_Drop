# --- Imports
import cv2
import numpy as np
import pygame as pg
from os import mkdir, listdir
import time
import json
import yaml
import pandas as pd

import Params as P
from Text import Text
from Drop import Drop


# --- Defs
# <<< Text
def addText(text, pos, color=(240, 240, 240), size=40):
    P.texts.append( Text(P.textTimeShow, text, pos, color, size) )
def setText():
    i = 0
    while i < len(P.texts):
        text = P.texts[i].getInfo()
        if text == 0:
            P.texts.pop(i)
        else:
            putTextPy(text[0], text[1], text[2], text[3])
        i += 1
def putTextPy(text, pos, color=(240, 240, 240), size=40):
    font = pg.font.SysFont(None, size)
    showText = font.render(str(text), True, color)
    P.screen.blit(showText, (pos[0], pos[1]))
def putTextCv(frame, text, pos, color=(240, 240, 240), size=1):
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (pos[0], pos[1])
    thickness = 2
    outline = [(255 - x) for x in color]

    cv2.putText(frame, str(text), org, font,
                size, outline, thickness + 2, cv2.LINE_AA)
    cv2.putText(frame, str(text), org, font,
                size, color, thickness, cv2.LINE_AA)

# <<< Median
def getMedian(frame):
    if len(P.medianFrames) == P.medianLength: return  # No need to generate new median

    elif len(P.medianFrames) < P.medianLength-1:  # Fill array with new frames
        putTextPy(f"{int(len(P.medianFrames) / P.medianLength * 100)}%", (P.WIDTH * .9, P.HEIGHT // 2 + 65), size=30)

        try:
            if frame == None:
                return
        except(ValueError):
            P.medianFrames.append(frame)

    else:  # Generate new median
        median = np.median(P.medianFrames, axis=0).astype(dtype=np.uint8)
        cv2.imwrite(P.medianName, median)

        P.medianFrames.append(0)  # Make array's len = need len. Stop array filling

        addText("Saved", (P.WIDTH * .8, P.HEIGHT // 2 + 125), size=30)

# <<< Output frame
def convertForPygame(cvFrame):

    if len(cvFrame.shape) < 3:
        cvFrame = cv2.cvtColor(cvFrame, cv2.COLOR_GRAY2RGB)

    cvImage = cvFrame[:, :].tobytes()
    cvShape = cvFrame.shape[1::-1]

    image = pg.image.frombuffer(cvImage, cvShape, 'BGR')

    return image

# <<< Frame's processing
def setFrame(frame):
    copy = frame.copy()
    copy = copy[P.sets[6]:int(P.HEIGHT - P.sets[7] + 1), P.sets[8]:int(frame.shape[1] - P.sets[9] + 1)]

    if len(frame.shape) > 2:
        mask = cv2.inRange(copy, (P.sets[0], P.sets[1], P.sets[2]), (P.sets[3], P.sets[4], P.sets[5]))
    else:
        mask = cv2.inRange(copy, (P.sets[0]), (P.sets[1]))

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=np.ones((4, 4)), iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=np.ones((4, 4)), iterations=4)
    mask = cv2.morphologyEx(mask, cv2.MORPH_ERODE, kernel=np.ones((5, 5)))

    copy = cv2.bitwise_and(copy, copy, mask=mask)

    frame[P.sets[6]:int(P.HEIGHT - P.sets[7] + 1), P.sets[8]:int(frame.shape[1] - P.sets[9]) + 1] = copy

    frame, _ = getConnected(frame, mask)

    return frame

def getConnected(frame, mask):
    cv2.rectangle(frame, (P.sets[8], P.sets[6]),
                  (int(frame.shape[1] - P.sets[9]), int(frame.shape[0] - P.sets[7])),
                  (0, 255, 0), 3)

    output = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
    num_labels = output[0]
    stats = output[2]

    for i in range(1, num_labels):
        t = P.sets[6] + stats[i, cv2.CC_STAT_TOP]
        l = P.sets[8] + stats[i, cv2.CC_STAT_LEFT]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]

        if (w * h > P.sets[10] and t != 2147483647):
            cv2.rectangle(frame, (l, t), (w + l, h + t), (255, 0, 255), 1)

            if P.pxSizeFrame != 0:
                textWidth = f"{round((P.pxSizeFrame * w), 3)}mm"
                textHeight = f"{round((P.pxSizeFrame * h), 3)}mm"
            else:
                textWidth = f"{w}px"
                textHeight = f"{h}px"

            putTextCv(frame, textWidth, (l + w // 2, t + h - 5), size=.5)
            putTextCv(frame, textHeight, (l + 5, t + h // 2), size=.5)

    return frame, num_labels

def getObjects(frame, mask):
    cv2.rectangle(frame, (P.sets[8], P.sets[6]),
                  (int(frame.shape[1] - P.sets[9]), int(frame.shape[0] - P.sets[7])),
                  (0, 255, 0), 3)

    output = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
    num = output[0]
    stats = output[2]

    drops = []

    for i in range(1, num):
        t = P.sets[6] + stats[i, cv2.CC_STAT_TOP]
        l = P.sets[8] + stats[i, cv2.CC_STAT_LEFT]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        a = stats[i, cv2.CC_STAT_AREA]

        drops.append( Drop(a, w, h, l, t, P.frameCount) )

        if (w * h > P.sets[10] and t != 2147483647):
            cv2.rectangle(frame, (l, t), (w + l, h + t), (255, 0, 255), 1)

            if P.pxSizeFrame != 0:
                textWidth = f"{round((P.pxSizeFrame * w), 3)}mm"
                textHeight = f"{round((P.pxSizeFrame * h), 3)}mm"
            else:
                textWidth = f"{w}px"
                textHeight = f"{h}px"

            putTextCv(frame, textWidth, (l + w // 2, t + h - 5), size=.5)
            putTextCv(frame, textHeight, (l + 5, t + h // 2), size=.5)

    return frame, drops

def addDynamicFrame(frame):
    try:
        if frame == None or frame == 0: return
    except(ValueError):
        P.dynamicFrames.append(frame)
        if len(P.dynamicFrames) > P.dynamicLength:
            P.dynamicFrames.pop(0)

    median = np.median(P.dynamicFrames, axis=0).astype(dtype=np.uint8)
    return cv2.absdiff(frame, median)

# <<< Recording
def createFolder():
    P.threadCount += 1
    path = P.logFolder + str(P.threadCount).zfill(4)

    mkdir(path)
    if P.isImageSave:
        mkdir(path + "/images")

    P.lastPath = P.path
    P.path = "%s%s%s" % (P.logFolder + str(P.threadCount).zfill(4) + "/", time.strftime(P.timeFormat, time.gmtime()), P.fileType)
    P.out = cv2.VideoWriter(P.path, P.fourcc, P.FPS, (640, 480))

def recording(set):
    P.isRecording = set
    if set:
        print("\nStart a recording")
        P.out = cv2.VideoWriter(P.path, P.fourcc, P.FPS, (640, 480))

    else:
        print("\nStop a recording")
        P.out.release()

# <<< File manager
def YAMLtoJSON(folder, yamlName, jsonName):
    with open(folder + yamlName, 'r') as yaml_in, open(folder + jsonName, "w+") as json_out:
        yaml_object = yaml.safe_load(yaml_in)
        json.dump(yaml_object, json_out)

    if len([f for f in listdir(folder) if f == jsonName]) > 0:
        addText("YAML to JSON", (P.WIDTH*.68, P.HEIGHT*.05), color=P.GREEN, size=20)
        JSONtoPANDAS(folder, jsonName)
    else:
        addText("ERROR JSON", (P.WIDTH * .68, P.HEIGHT * .05), color=P.RED, size=20)

def JSONtoPANDAS(folder, jsonName):
    pandas_object = pd.io.json.read_json(folder + jsonName)
    print(pandas_object)

# <<< Reset
def resetAllParams():
    print("RESET ALL")

    P.dynamicFrames = []
    # TODO: Add here all necessaries params that need to clear


# --- Links
'''
PyGame Image Convert: https://pg1.readthedocs.io/en/latest/ref/image.html#pygame.image.frombuffer
'''