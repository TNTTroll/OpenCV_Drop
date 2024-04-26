# --- Imports
import cv2
import time
import os
from math import sqrt
import numpy as np

import Params as P
import Additional as A


# --- Defs
def getFrame(frame, mode):

    if P.isFlip: frame = cv2.flip(frame, 1)

    # For the first frame hide old things and show current
    if (mode[0] != mode[1]):
        setModeChoise(mode[1], False)
        setModeChoise(mode[0], True)

    try:
        frame = modeChoise(mode[0], frame)
        P.screen.blit(A.convertForPygame(frame), (0, 0))

        if P.isRecording:
            P.out.write(cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR))

        if P.lastFrameMode > 0:
            A.putTextPy(f"Last: {P.lastFrameMode}", (P.WIDTH - 300, 20), size=30)

    except(cv2.error, TypeError, AttributeError):
        A.putTextPy("| NO SIGNAL |", (P.WIDTH // 4, P.HEIGHT // 2))

    if P.isTextShown:

        if not P.sliders[0].visible:
            setModeChoise(mode[0], True)

        if P.buttons[1].visible:
            P.buttons[1].hide()

        if P.buttons[3].visible:
            P.buttons[3].hide()

        setTextMode(mode[0])

        A.putTextPy(f"< {mode[0]} >", (P.WIDTH * .75, P.HEIGHT-40))

        if P.pxSizeframe != 0:
            A.putTextPy(f"PX between dots: {round(P.cellPX, 3)}", (P.WIDTH * .75, P.HEIGHT - 150), size=30)
            A.putTextPy(f"PX Size (MM): {round(P.pxSizeframe, 4)}", (P.WIDTH * .75, P.HEIGHT - 120), size=30)

    else:
        if P.sliders[0].visible:
            setModeChoise(mode[0], False)

        if P.isRecording:
            A.putTextPy("Recording...", (P.WIDTH * .75, P.HEIGHT//3-60))

            if not P.buttons[2].visible:
                P.buttons[2].show()

            if P.buttons[1].visible:
                P.buttons[1].hide()

        else:
            if not P.buttons[1].visible:
                P.buttons[1].show()

            if P.buttons[2].visible:
                P.buttons[2].hide()

        if not P.buttons[3].visible:
            P.buttons[3].show()

    if P.lastFrameMode > 0:
        try:
            if P.lastFrames[-1] == None or P.lastFrames[-1] == 0:
                pass
        except(ValueError):
            for i in range(P.lastFrameMode):
                P.lastFrames[i] = cv2.resize(P.lastFrames[i], (320, 240), interpolation=cv2.INTER_LINEAR)

            if P.lastFrameMode == 1:
                layers = P.lastFrames[0]
            elif P.lastFrameMode == 2:
                layers = np.hstack((P.lastFrames[1], P.lastFrames[0]))
            elif P.lastFrameMode == 3:
                layers = np.hstack((P.lastFrames[2], P.lastFrames[1], P.lastFrames[0]))
            elif P.lastFrameMode == 4:
                layers = np.vstack((np.hstack((P.lastFrames[3], P.lastFrames[2])),
                                    np.hstack((P.lastFrames[1], P.lastFrames[0]))))

            cv2.imshow(P.lastFrameName, layers)


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

            if P.pxSizeframe != 0:
                textWidth = f"{round((P.pxSizeframe * w), 3)}mm"
                textHeight = f"{round((P.pxSizeframe * h), 3)}mm"
            else:
                textWidth = f"{w}px"
                textHeight = f"{h}px"

            A.putTextCv(frame, textWidth, (l + w // 2, t + h - 5), size=.5)
            A.putTextCv(frame, textHeight, (l + 5, t + h // 2), size=.5)

    return frame, num_labels

def setModeChoise(name, set):
    if not set: cv2.destroyAllWindows()
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

    return setFrame(frame)
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

# <<< Different mode
def setModeDifferent(set):
    if set:
        for x in range(2):
            P.sliders[x].set_current_value(P.sets[x])
            P.sliders[x].show()

        P.sliders[-1].set_current_value(P.sets[-1])
        P.sliders[-1].show()

    else:
        for x in range(2): P.sliders[x].hide()
        P.sliders[-1].hide()
def modeDifferent(frame):
    for x in range(len(P.sets)):
        P.sets[x] = P.sliders[x].get_current_value()

    if P.isExternal == None:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    median = cv2.imread(P.medianName, 0)
    frame = cv2.absdiff(frame, median)

    thresh = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY)[1]

    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel=np.ones((4, 4)), iterations=4)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=np.ones((4, 4)), iterations=1)

    frame = cv2.bitwise_and(frame, frame, mask=mask)

    frame, _ = getConnected(frame, mask)

    return frame
def setTextDifferent():
    for x in range(len(P.slidersMovementMode)):
        A.putTextPy(P.slidersMovementMode[x], (P.WIDTH - 305, 75 + (25 * x)), size=20)

    A.putTextPy(P.slidersSettingsNames[-1], (P.WIDTH - 305, 325), size=20)

# <<< Movement mode
def setModeMovement(set):
    if set:
        for x in range(2):
            P.sliders[x].set_current_value(P.sets[x])
            P.sliders[x].show()

        P.sliders[-1].set_current_value(P.sets[-1])
        P.sliders[-1].show()

    else:
        for x in range(2): P.sliders[x].hide()
        P.sliders[-1].hide()
def modeMovement(frame):
    for x in range(len(P.sets)):
        P.sets[x] = P.sliders[x].get_current_value()

    if P.isExternal == None:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Add new frame to array
    try:
        if frame == None: return
    except(ValueError):
        P.dynamicFrames.append(frame)
        if (len(P.dynamicFrames) > P.dynamicLength):
            P.dynamicFrames.pop(0)

    median = np.median(P.dynamicFrames, axis=0).astype(dtype=np.uint8)
    frame = cv2.absdiff(frame, median)

    thresh = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY)[1]

    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel=np.ones((4, 4)), iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=np.ones((4, 4)), iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=np.ones((4, 4)), iterations=7)

    frame = cv2.bitwise_and(frame, frame, mask=mask)

    frame, num = getConnected(frame, mask)

    A.putTextPy(f"Objects: {num}", (P.WIDTH * .75, P.HEIGHT // 2 - 40), size=30)

    if num > 1:

        P.timeFramesCount += 1
        if P.timeStart != 0:
            A.putTextPy(f"Capturing: {round((time.time() - P.timeStart), 2)}s", (P.WIDTH * .75, P.HEIGHT // 2 - 80), size=30)

        if not P.isRecDynamic:
            P.timeStart = time.time()
            P.isRecDynamic = True

            P.path = "%s%s.avi"%(P.folder, time.strftime(P.timeFormat, time.gmtime()))
            A.recording(True)
    else:
        if P.timeStart != 0:

            if P.timeFramesCount > 1:
                A.recording(False)

                if time.time() - P.timeStart < P.timeGap:
                    os.remove(P.path)
                    A.putTextPy(f"Deleted. {round((time.time() - P.timeStart), 2)}s", (P.WIDTH * .75, P.HEIGHT // 2), size=30)

            P.timeFramesCount = 0
            P.isRecDynamic = False
            P.timeStart = 0

    return frame
def setTextMovement():
    for x in range(len(P.slidersMovementMode)):
        A.putTextPy(P.slidersMovementMode[x], (P.WIDTH - 305, 75 + (25 * x)), size=20)

    A.putTextPy(P.slidersSettingsNames[-1], (P.WIDTH - 305, 325), size=20)

# <<< Window mode
def setModeWindow(set):
    if set:
        for x in range(len(P.slidersWindowMode)):
            P.sliders[x].set_current_value(P.sets[x])
            P.sliders[x].show()

        P.sliders[-1].set_current_value(P.sets[-1])
        P.sliders[-1].show()

        P.path = "%s%s.avi" % (P.folder, time.strftime(P.timeFormat, time.gmtime()))
        P.windowOut = cv2.VideoWriter(P.path, P.fourcc, P.FPS, (640, 480))

    else:
        for slider in P.sliders: slider.hide()
        P.sliders[-1].hide()
        P.windowOut.release()
def modeWindow(frame):
    def saveFrames():
        if P.moveFrame > 5:  # TODO: Change for drop (less frames needed to be)
            for i in range(len(P.windowStaticArray) - 1):
                try:
                    if P.windowStaticArray[P.currentFrame % 50] != 0: pass
                except(ValueError):
                    P.windowOut.write(P.windowStaticArray[P.currentFrame % 50])

                P.currentFrame += 1

            for i in range(P.moveFrame):
                P.windowOut.write(P.windowMoveArray[i])

            P.windowOut.release()
            P.path = "%s%s.avi" % (P.folder, time.strftime(P.timeFormat, time.gmtime()))
            P.windowOut = cv2.VideoWriter(P.path, P.fourcc, P.FPS, (640, 480))

        P.currentFrame %= 50
        P.moveFrame = 0

    for x in range(len(P.sets)):
        P.sets[x] = P.sliders[x].get_current_value()

    if P.isExternal == None:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Add new frame to array
    try:
        if frame == None or frame == 0: return
    except(ValueError):
        P.dynamicFrames.append(frame)
        if len(P.dynamicFrames) > P.dynamicLength:
            P.dynamicFrames.pop(0)

    median = np.median(P.dynamicFrames, axis=0).astype(dtype=np.uint8)
    diff = cv2.absdiff(frame, median)

    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY)[1]

    mask = cv2.erode(thresh, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4)), iterations=P.sets[0])
    mask = cv2.dilate(mask, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4)), iterations=P.sets[1])
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4)), iterations=P.sets[2])
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4)), iterations=P.sets[3])

    diff = cv2.bitwise_and(frame, frame, mask=mask)

    connection, num = getConnected(diff, mask)

    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    if num > 1:  # There are object on the scene
        P.windowMoveArray[P.moveFrame] = frame
        P.moveFrame += 1
        if P.moveFrame == len(P.windowMoveArray) - 1:
            saveFrames()

        if P.windowReset == 1:
            P.windowMax = 0

        P.windowMax = max(P.windowMax, num-1)
        P.windowReset = 0

        P.windowBuffer = [connection] + P.lastFrames[0:-1]

    else:  # Static scene
        P.windowStaticArray[P.currentFrame] = frame
        P.currentFrame += 1
        if P.currentFrame >= len(P.windowStaticArray) - 1: P.currentFrame = 0

        if P.moveFrame != 0:
            saveFrames()

        if P.windowReset == 0:
            P.lastFrames = P.windowBuffer

        P.windowReset = 1

    A.putTextPy(f"Objects: {num - 1}", (P.WIDTH * .75, P.HEIGHT // 2 - 40), size=30)
    A.putTextPy(f"Max: {P.windowMax}", (P.WIDTH * .75, P.HEIGHT // 2 - 20), size=30)

    A.putTextCv(frame, f"A: {P.currentFrame}", (50, 50))
    A.putTextCv(frame, f"B: {P.moveFrame}", (50, 100))

    return connection
def setTextWindow():
    for x in range(len(P.slidersWindowMode)):
        A.putTextPy(f"{P.slidersWindowMode[x]}: {P.sets[x]}", (P.WIDTH - 300, 75 + (25 * x)), size=20)
    A.putTextPy(P.slidersSettingsNames[-1], (P.WIDTH - 305, 325), size=20)

# <<< Playground mode
def setModePlay(set):
    pass
def modePlay(frame):
    return frame
def setTextPlay():
    pass