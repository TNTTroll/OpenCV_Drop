# --- Imports
import cv2
from math import sqrt
import numpy as np

import Params as P
import Additional as A


screen = None

# --- Defs
def getFrame(frame, scr, sliders, mode):
    global screen
    screen = scr

    if P.isTextShown:
        A.putText(screen, f"< {mode[0]} >", (P.statOffsetX, P.statOffsetY))

        A.putText(screen, f"PX between dots: {round(P.cellPX, 3)}", (P.statOffsetX, P.statOffsetY * 2))
        A.putText(screen, f"PX Size (MM): {round(P.pxSizeframe, 4)}", (P.statOffsetX, P.statOffsetY * 3))

    if P.checkForFlip:
        frame = cv2.flip(frame, 1)

    if (mode[0] == "SETTINGS" or mode[1] == "SETTINGS"):
        return modeSettings(frame, sliders, mode)

    if (mode[0] == "CHECKBOARD"):
        return modeChessboard(frame, sliders, mode)

    if (mode[0] == "DETECTING"):
        return modeDetecting(frame)

    else:  # Default
        return frame


def setFrame(frame, way):
    frame = frame[P.sets[6]:(P.HEIGHT - P.sets[7] + 1), P.sets[8]:(P.WIDTH - P.sets[9] + 1)]

    if (way == "CUT"): return frame

    else:
        mask = cv2.inRange(frame, (P.sets[0], P.sets[1], P.sets[2]), (P.sets[3], P.sets[4], P.sets[5]))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=np.ones((4, 4)), iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=np.ones((4, 4)), iterations=4)

        frame = cv2.bitwise_and(frame, frame, mask=cv2.morphologyEx(mask, cv2.MORPH_ERODE, kernel=np.ones((5, 5))))

        output = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
        num_labels = output[0]
        stats = output[2]

        for i in range(1, num_labels):
            a = stats[i, cv2.CC_STAT_AREA]
            t = stats[i, cv2.CC_STAT_TOP]
            l = stats[i, cv2.CC_STAT_LEFT]
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]

            cv2.rectangle(frame, (l, t), (l + w, t + h), (255, 0, 255), 1)

            #A.putText(screen, P.pxSizeframe * w, (l, t))

        return frame


def modeSettings(frame, sliders, mode):

    if (mode[0] != mode[1]): # Toggle first frame
        if (mode[0] == "SETTINGS"):
            for x in range( len(sliders) ):
                sliders[x].set_current_value(P.sets[x])
                sliders[x].show()

        else:
            for slider in sliders: slider.hide()

    else:
        for x in range( len(P.sets) ):
            P.sets[x] = sliders[x].get_current_value()

        frame = setFrame(frame, "FULL")

    return frame


def modeChessboard(frame, sliders, mode):
    frame = setFrame(frame, "CUT")

    if (mode[0] != mode[1]):  # Toggle first frame
        if (mode[0] == "CHECKBOARD"):
            for x in range(2):
                sliders[x].set_current_value(P.checkField[x])
                sliders[x].show()

        else:
            for x in range(2): sliders[x].show()

    else:
        nline = sliders[0].get_current_value()
        ncol = sliders[1].get_current_value()

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

                cellPX = sqrt((distanceX * distanceX) + (distanceY * distanceY))

                cv2.line(frame, (int(putDots[0][0][0]), int(putDots[0][0][1])),
                                (int(putDots[1][0][0]), int(putDots[1][0][1])),
                                (255, 255, 255), 2)

                chessWidthPX = cellPX * (ncol + 1)

                P.pxSizeframe = P.realSize / chessWidthPX

    return frame


def modeDetecting(frame):
    return setFrame(frame, "FULL")