# --- Imports
import cv2
from math import sqrt

from Params import *
import Additional as A


# --- Defs
def getFrame(frame, statisticFrame, mode, isTextShown):
    global cellPX, pxSizeframe

    if (isTextShown):
        A.putText(frame, f"< {mode[0]} >", (10, 25))

    A.putText(statisticFrame, f"PX between dots: {round(cellPX, 3)}", (statOffsetX, statOffsetY * 1))
    A.putText(statisticFrame, f"PX Size (MM): {round(pxSizeframe, 4)}", (statOffsetX, statOffsetY * 2))

    if (mode[0] == "SETTINGS" or mode[1] == "SETTINGS"):
        return modeSettings(frame, mode)

    if (mode[0] == "CHECKBOARD"):
        frame, cellPX, pxSizeframe = modeChessboard(frame, statisticFrame)

        return frame

    if (mode[0] == "DETECTING"):
        frame = modeDetecting(frame)

        return frame

    else:  # Default
        return frame


def setFrame(frame, way):
    frame = frame[par06:(HEIGHT - par07 + 1), par08:(WIDTH - par09 + 1)]

    if (way == "CUT"):
        return frame

    else:
        mask = cv2.inRange(frame, (par00, par01, par02), (par03, par04, par05))
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

            A.putText(frame, pxSizeframe * w, (l, t))

        return frame


def modeSettings(frame, mode):
    global par00, par01, par02, par03, par04, par05, par06, par07, par08, par09

    if (mode[0] != mode[1]):
        if (mode[0] == "SETTINGS"):
            cv2.namedWindow(WINDOW_SET)

            cv2.createTrackbar('Par00', WINDOW_SET, par00, 255, change_value)
            cv2.createTrackbar('Par01', WINDOW_SET, par01, 255, change_value)
            cv2.createTrackbar('Par02', WINDOW_SET, par02, 255, change_value)
            cv2.createTrackbar('Par03', WINDOW_SET, par03, 255, change_value)
            cv2.createTrackbar('Par04', WINDOW_SET, par04, 255, change_value)
            cv2.createTrackbar('Par05', WINDOW_SET, par05, 255, change_value)
            cv2.createTrackbar('Par06', WINDOW_SET, par06, HEIGHT - 1, change_value)
            cv2.createTrackbar('Par07', WINDOW_SET, par07, HEIGHT - 1, change_value)
            cv2.createTrackbar('Par08', WINDOW_SET, par08, WIDTH - 1, change_value)
            cv2.createTrackbar('Par09', WINDOW_SET, par09, WIDTH - 1, change_value)

        else:
            cv2.destroyWindow(WINDOW_SET)

    else:
        settings = winSettings.copy()

        par00 = cv2.getTrackbarPos('Par00', WINDOW_SET)
        par01 = cv2.getTrackbarPos('Par01', WINDOW_SET)
        par02 = cv2.getTrackbarPos('Par02', WINDOW_SET)
        par03 = cv2.getTrackbarPos('Par03', WINDOW_SET)
        par04 = cv2.getTrackbarPos('Par04', WINDOW_SET)
        par05 = cv2.getTrackbarPos('Par05', WINDOW_SET)
        par06 = cv2.getTrackbarPos('Par06', WINDOW_SET)
        par07 = cv2.getTrackbarPos('Par07', WINDOW_SET)
        par08 = cv2.getTrackbarPos('Par08', WINDOW_SET)
        par09 = cv2.getTrackbarPos('Par09', WINDOW_SET)

        cv2.putText(settings, "PRESS 'S' to SAVE", (0, 10), cv2.FONT_HERSHEY_SIMPLEX, 1, BLACK, 2, cv2.LINE_AA)

        cv2.imshow(WINDOW_SET, settings)

        frame = setFrame(frame, "FULL")

    return frame


def modeChessboard(frame, statisticFrame):
    global cellPX, pxSizeframe

    frame = setFrame(frame, "CUT")

    nline = 4
    ncol = 5

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    if (isExternal == None):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ret, cornersChess = cv2.findChessboardCorners(frame, (nline, ncol), None)

    if (ret):
        putDots = cv2.cornerSubPix(frame, cornersChess, (11, 11), (-1, -1), criteria)

        for coord in putDots:
            x = int(coord[0][0])
            y = int(coord[0][1])

            cv2.circle(frame, (x, y), 1, (255, 255, 255), 2)

            distanceX = abs(putDots[0][0][0] - putDots[1][0][0])
            distanceY = abs(putDots[0][0][1] - putDots[1][0][1])

            cellPX = sqrt((distanceX * distanceX) + (distanceY * distanceY))

            cv2.line(frame, (int(putDots[0][0][0]), int(putDots[0][0][1])),
                     (int(putDots[1][0][0]), int(putDots[1][0][1])), (255, 255, 255), 2)

            chessWidthPX = cellPX * (ncol + 1)
            chessHeightPX = cellPX * (nline + 1)

            pxSizeframe = realSize / chessWidthPX

            stats = [cellPX, pxSizeframe]

    return frame, cellPX, pxSizeframe


def modeDetecting(frame):
    return setFrame(frame, "FULL")


def change_value(value): pass