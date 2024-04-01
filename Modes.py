# --- Imports
import cv2
from math import sqrt
import numpy as np

import Params as P
import Additional as A


# --- Defs
def getFrame(frame, mode):

    if P.checkForFlip:
        frame = cv2.flip(frame, 1)

    # For the first frame hide old things and show current
    if (mode[0] != mode[1]):
        setModeChoise(mode[1], False)
        setModeChoise(mode[0], True)

    try:
        frame = modeChoise(mode[0], frame)
        P.screen.blit(A.convertForPygame(frame), (0, 0))

        if P.isRecording:
            P.out.write(frame)

    except(cv2.error, TypeError, AttributeError):
        A.putTextPy("| NO SIGNAL |", (P.WIDTH // 4, P.HEIGHT // 2))

    if P.isTextShown:

        if not P.sliders[0].visible:
            setModeChoise(mode[0], True)

        if P.buttons[1].visible:
            P.buttons[1].hide()

        setTextMode(mode[0])

        A.putTextPy(f"< {mode[0]} >", (P.WIDTH * .75, P.HEIGHT-40))

        if P.pxSizeframe != 0:
            A.putTextPy(f"PX between dots: {round(P.cellPX, 3)}", (P.WIDTH * .75, P.HEIGHT - 150), size=30)
            A.putTextPy(f"PX Size (MM): {round(P.pxSizeframe, 4)}", (P.WIDTH * .75, P.HEIGHT - 120), size=30)

    else:
        if P.sliders[0].visible:
            setModeChoise(mode[0], False)

        if P.isRecording:
            A.putTextPy("Recording...", (P.WIDTH * .75, P.HEIGHT//2+60))

            if not P.buttons[2].visible:
                P.buttons[2].show()

            if P.buttons[1].visible:
                P.buttons[1].hide()

        else:
            if not P.buttons[1].visible:
                P.buttons[1].show()

            if P.buttons[2].visible:
                P.buttons[2].hide()


def setFrame(frame, way):
    if (way == "CUT"): return frame

    else:
        copy = frame.copy()
        copy = copy[P.sets[6]:int(P.HEIGHT - P.sets[7] + 1), P.sets[8]:int(frame.shape[1] - P.sets[9] + 1)]

        if P.isExternal == None:
            mask = cv2.inRange(copy, (P.sets[0], P.sets[1], P.sets[2]), (P.sets[3], P.sets[4], P.sets[5]))
        else:
            mask = cv2.inRange(copy, (P.sets[0]), (P.sets[1]))

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=np.ones((4, 4)), iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=np.ones((4, 4)), iterations=4)

        copy = cv2.bitwise_and(copy, copy, mask=cv2.morphologyEx(mask, cv2.MORPH_ERODE, kernel=np.ones((5, 5))))

        frame[P.sets[6]:int(P.HEIGHT - P.sets[7] + 1), P.sets[8]:int(frame.shape[1] - P.sets[9]) + 1] = copy

        cv2.rectangle(frame, (P.sets[8], P.sets[6]),
                      (int(frame.shape[1]-P.sets[9]), int(frame.shape[0]-P.sets[7])),
                      (0, 255, 0), 3)

        output = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
        num_labels = output[0]
        stats = output[2]

        for i in range(num_labels):
            t = P.sets[6]
            l = P.sets[8]
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]

            if (w*h < P.sets[10]):
                cv2.rectangle(frame, (l, t), (w + l, h + t), (255, 0, 255), 1)
                if P.pxSizeframe != 0: A.putTextCv(frame, round((P.pxSizeframe * h), 3), (l + w//2, t + h), size=.5)

        return frame

def setModeChoise(name, set):
    return globals()['setMode' + str(name[0] + name.lower()[1:])](set)

def modeChoise(name, frame):
    return globals()['mode' + str(name[0] + name.lower()[1:])](frame)

def setTextMode(name):
    return globals()['setText' + str(name[0] + name.lower()[1:])]()

# <<< Default mode
def setModeDefault(set):
    pass
def modeDefault(frame):
    return frame

def setTextDefault():
    pass

# <<< Settings mode
def setModeSettings(set):
    if set:
        for x in range(len(P.sliders)):
            P.sliders[x].set_current_value(P.sets[x])
            P.sliders[x].show()

        if P.isExternal:
            for x in range(2, 6):
                P.sliders[x].hide()

    else:
        for slider in P.sliders: slider.hide()

def modeSettings(frame):

    for x in range( len(P.sets) ):
        P.sets[x] = P.sliders[x].get_current_value()

    return setFrame(frame, "FULL")

def setTextSettings():
    for x in range(len(P.slidersSettingsNames)):
        A.putTextPy(P.slidersSettingsNames[x], (P.WIDTH - 280, 75 + (25 * x)), size=20)

# <<< Chess mode
def setModeChess(set):
    if set:
        for x in range(2):
            P.sliders[x].set_current_value(P.checkField[x])
            P.sliders[x].show()

    else:
        for x in range(2): P.sliders[x].hide()

def modeChess(frame):
    frame = setFrame(frame, "CUT")

    nline = P.sliders[0].get_current_value()
    ncol = P.sliders[1].get_current_value()

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    if P.isExternal == None:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ret, cornersChess = cv2.findChessboardCorners(frame, (nline, ncol), None)

    if ret:
        putDots = cv2.cornerSubPix(frame, cornersChess, (11, 11), (-1, -1), criteria)

        for coord in putDots:
            x, y = int(coord[0][0]), int(coord[0][1])

            cv2.circle(frame, (x, y), 1, (255, 255, 255), 2)

            distanceX = abs(putDots[0][0][0] - putDots[1][0][0])
            distanceY = abs(putDots[0][0][1] - putDots[1][0][1])

            P.cellPX = sqrt((distanceX * distanceX) + (distanceY * distanceY))

            cv2.line(frame, (int(putDots[0][0][0]), int(putDots[0][0][1])),
                            (int(putDots[1][0][0]), int(putDots[1][0][1])),
                            (255, 255, 255), 2)

            chessWidthPX = P.cellPX * (ncol + 1)

            P.pxSizeframe = P.realSize / chessWidthPX

    return frame

def setTextChess():
    for x in range(len(P.slidersCheckboardMode)):
        A.putTextPy(P.slidersCheckboardMode[x], (P.WIDTH - 305, 75 + (25 * x)), size=20)