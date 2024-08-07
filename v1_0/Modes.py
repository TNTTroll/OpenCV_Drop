# --- Imports
import cv2
import time
import os
from math import sqrt
import numpy as np

import Params as P
import Additional as A
import Logging as L
from Drop import Drop


# --- Defs
def getFrame(frame, mode):

    if P.isFlip: frame = cv2.flip(frame, 1)

    # For the first frame hide old things and show current
    if (mode[0] != mode[1]):
        setModeChoise(mode[1], False)
        setModeChoise(mode[0], True)

    try:
        if P.isExternal == None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        frame = modeChoise(mode[0], frame)
        A.setText()
        P.screen.blit(A.convertForPygame(frame), (0, 0))

        if P.isRecording:
            P.out.write(cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR))

        if P.lastFrameMode > 0:
            A.putTextPy(f"Last: {P.lastFrameMode}", (P.WIDTH - 300, 20), size=30)

    except(cv2.error, TypeError, AttributeError):
        A.putTextPy("| NO SIGNAL |", (P.WIDTH // 4, P.HEIGHT // 2))

    if P.isReady:

        if not P.sliders[0].visible:
            setModeChoise(mode[0], True)

        if P.buttons[1].visible:
            P.buttons[1].hide()

            for i in range(3, 7):
                P.buttons[i].hide()

        setTextMode(mode[0])

        A.putTextPy(f"< {mode[0]} >", (P.WIDTH * .75, P.HEIGHT-40))

        if P.pxSizeFrame != 0:
            #A.putTextPy(f"PX between dots: {round(P.cellPX, 3)}", (P.WIDTH * .74, P.HEIGHT - 150), size=30)
            #A.putTextPy(f"PX Size frame: {round(P.pxSizeFrame, 4)}", (P.WIDTH * .74, P.HEIGHT - 120), size=30)
            #A.putTextPy(f"Cell size (MM): {round(P.pxSizeFrame * P.cellPX, 4)}", (P.WIDTH * .74, P.HEIGHT - 90), size=30)
            A.putTextPy(f"PX between dots: {P.cellPX}", (P.WIDTH * .65, P.HEIGHT - 150), size=30)
            A.putTextPy(f"PX Size frame: {P.pxSizeFrame}", (P.WIDTH * .65, P.HEIGHT - 120), size=30)
            A.putTextPy(f"Cell size (MM): {P.pxSizeFrame * P.cellPX}", (P.WIDTH * .65, P.HEIGHT - 90), size=30)

    else:  # "Tab" Mode
        if P.sliders[0].visible:
            setModeChoise(mode[0], False)

        A.putTextPy(P.calibrationText, (P.WIDTH * .76, P.HEIGHT // 2 - 125), size=20)
        if not P.buttons[4].visible:
            for i in range(4, 7):
                P.buttons[i].show()

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

def processVideo():
    video = cv2.VideoCapture(P.lastPath)
    folderPath = P.logFolder + str(P.threadCount-1).zfill(4) + "/"

    while True:
        ret, frame = video.read()
        if not ret: break

        if P.isExternal == None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(A.addDynamicFrame(frame), 0, 255, cv2.THRESH_BINARY)[1]

        mask = cv2.erode(thresh, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4)), iterations=P.sets[0])
        mask = cv2.dilate(mask, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4)), iterations=P.sets[1])
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4)),
                                iterations=P.sets[2])
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4)),
                                iterations=P.sets[3])

        diff = cv2.bitwise_and(frame, frame, mask=mask)
        connection, objects = A.getObjects(diff, mask)

        if len(objects) > 0:
            if len(P.mainDrops) - P.inactiveDrops < len(objects):
                P.mainDrops.append(Drop(objects[0].areaPX[0], objects[0].width[0], objects[0].height[0],
                                        objects[0].left[0], objects[0].top[0], P.frameCount))

            elif len(P.mainDrops) - P.inactiveDrops > len(objects):
                P.inactiveDrops += ( len(P.mainDrops) - P.inactiveDrops - len(objects) )

            for x in range(P.inactiveDrops, len(objects)):
                P.mainDrops[x].addParam(objects[x])

            L.frameLog(objects, folderPath)

        if P.objectMoveReset == 0:
            L.mainLog(P.moveFrame, 1)
            P.objectMoveReset = 1

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

    return A.setFrame(frame)
def setTextSettings():
    for x in range(len(P.slidersSettingsNames)):
        A.putTextPy(P.slidersSettingsNames[x], (P.WIDTH - 280, 75 + (25 * x)), size=20)

# <<< Chess mode
def setModeChess(set):
    if set:
        for x in range(2):
            P.sliders[x].set_current_value(P.chessField[x])
            P.sliders[x].show()

    else:
        for x in range(2): P.sliders[x].hide()
def modeChess(frame):
    nline = P.sliders[0].get_current_value()
    ncol = P.sliders[1].get_current_value()

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

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

            P.pxSizeFrame = P.realSize / chessWidthPX
            P.chessPhoto = cornersChess

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

    median = cv2.imread(P.medianName, 0)
    frame = cv2.absdiff(frame, median)

    thresh = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY)[1]

    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel=np.ones((4, 4)), iterations=4)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=np.ones((4, 4)), iterations=1)

    frame = cv2.bitwise_and(frame, frame, mask=mask)

    frame, _ = A.getConnected(frame, mask)

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

    frame = A.addDynamicFrame(frame)

    thresh = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY)[1]

    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel=np.ones((4, 4)), iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=np.ones((4, 4)), iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=np.ones((4, 4)), iterations=7)

    frame = cv2.bitwise_and(frame, frame, mask=mask)

    frame, num = A.getConnected(frame, mask)

    A.putTextPy(f"Objects: {num}", (P.WIDTH * .75, P.HEIGHT // 2 - 40), size=30)

    if num > 1:

        P.timeFramesCount += 1
        if P.timeStart != 0:
            A.putTextPy(f"Capturing: {round((time.time() - P.timeStart), 2)}s", (P.WIDTH * .75, P.HEIGHT // 2 - 80), size=30)

        if not P.isRecDynamic:
            P.timeStart = time.time()
            P.isRecDynamic = True

            P.path = "%s%s%s" % (P.folder, time.strftime(P.timeFormat, time.gmtime()), P.fileType)
            #A.recording(True)
    else:
        if P.timeStart != 0:

            if P.timeFramesCount > 1:
                #A.recording(False)

                if time.time() - P.timeStart < P.timeGap:
                    #os.remove(P.path)
                    A.addText(f"Deleted. {round((time.time() - P.timeStart), 2)}s", (P.WIDTH * .75, P.HEIGHT // 2), size=30)

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
            P.sliders[x].set_current_value([0, 0, 7, 7][x])
            P.sliders[x].show()

        P.sliders[-1].set_current_value([0][-1])
        P.sliders[-1].show()

        A.createFolder()

        P.calibreId = -1

    else:
        for slider in P.sliders: slider.hide()
        P.sliders[-1].hide()
        L.saveFrames(P.out, "EXIT")
        P.mainDrops = []
def modeWindow(frame):
    for x in range(len(P.sets)):
        P.sets[x] = P.sliders[x].get_current_value()

    thresh = cv2.threshold(A.addDynamicFrame(frame), 0, 255, cv2.THRESH_BINARY)[1]

    mask = cv2.erode(thresh, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4)), iterations=P.sets[0])
    mask = cv2.dilate(mask, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4)), iterations=P.sets[1])
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4)), iterations=P.sets[2])
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4)), iterations=P.sets[3])

    diff = cv2.bitwise_and(frame, frame, mask=mask)

    connection, objects = A.getObjects(diff, mask)

    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    if len(objects) > 0:  # There are object on the scene
        if not P.isCayotPause:
            P.writeStaticToMove += (str(P.currentFrame) + "|")
            P.isCayotPause = True

        P.moveArray[P.moveFrame][0] = frame
        P.moveArray[P.moveFrame][1] = diff
        P.moveFrame += 1
        if P.moveFrame == P.arrLength - 1:
            P.out = L.saveFrames(P.out, "MODE")

        if P.objectMoveReset == 1:
            P.windowMax = 0

        P.objectMoveReset = 0
        P.windowMax = max(P.windowMax, len(objects)-1)
        P.windowBuffer = [connection] + P.lastFrames[0:-1]

        P.staticFrames = P.cayotTime

        while len(P.mainDrops) - P.inactiveDrops < len(objects):
            P.mainDrops.append( Drop(objects[0].areaPX[0], objects[0].width[0], objects[0].height[0],
                                     objects[0].left[0], objects[0].top[0], P.frameCount) )

        if len(P.mainDrops) - P.inactiveDrops > len(objects):
            P.inactiveDrops += ( len(P.mainDrops) - P.inactiveDrops - len(objects) )

        for x in range(P.inactiveDrops, len(objects)):
            P.mainDrops[x].addParam(objects[x])

    else:  # Static scene
        if P.isCayotPause:
            P.writeStaticToMove += (str(P.moveFrame) + "&")
            P.isCayotPause = False

        P.staticArray[P.currentFrame] = frame
        P.currentFrame += 1
        if P.currentFrame >= P.arrLength - 1: P.currentFrame = 0

        if P.moveFrame != 0:
            if P.staticFrames == 0:
                P.out = L.saveFrames(P.out, "MODE")
                P.staticFrames = P.cayotTime
            else:
                P.staticFrames -= 1

            A.putTextPy(f"Cayot time: {P.staticFrames}", (P.WIDTH * .75, P.HEIGHT // 2), size=30)

    A.putTextPy(f"Objects: {len(objects)}", (P.WIDTH * .75, P.HEIGHT // 2 - 40), size=30)
    A.putTextPy(f"Max: {P.windowMax}", (P.WIDTH * .75, P.HEIGHT // 2 - 20), size=30)

    A.putTextCv(frame, f"A: {P.currentFrame}", (50, 50))
    A.putTextCv(frame, f"B: {P.moveFrame}", (50, 100))

    folderPath = P.logFolder + str(P.threadCount).zfill(4) + "/"
    if 0 < len(objects): L.frameLog(objects, folderPath)

    return connection #frame
def setTextWindow():
    for x in range(len(P.slidersWindowMode)):
        A.putTextPy(f"{P.slidersWindowMode[x]}: {P.sets[x]}", (P.WIDTH - 300, 75 + (25 * x)), size=20)
    A.putTextPy(P.slidersSettingsNames[-1], (P.WIDTH - 305, 325), size=20)

# <<< Post mode
def setModePost(set):
    if set:
        for x in range(len(P.slidersWindowMode)):
            P.sliders[x].set_current_value([0, 0, 7, 7][x])
            P.sliders[x].show()

        P.sliders[-1].set_current_value([0][-1])
        P.sliders[-1].show()

        A.createFolder()

        P.calibreId = -1

    else:
        for slider in P.sliders: slider.hide()
        P.sliders[-1].hide()
        L.saveFrames(P.out, "EXIT")
        P.mainDrops = []
def modePost(frame):
    for x in range(len(P.sets)):
        P.sets[x] = P.sliders[x].get_current_value()

    thresh = cv2.threshold(A.addDynamicFrame(frame), 0, 255, cv2.THRESH_BINARY)[1]

    mask = cv2.erode(thresh, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4)), iterations=P.sets[0])
    mask = cv2.dilate(mask, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4)), iterations=P.sets[1])
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4)), iterations=P.sets[2])
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4)), iterations=P.sets[3])

    diff = cv2.bitwise_and(frame, frame, mask=mask)
    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    if np.sum(mask) > 0:  # There are object on the scene
        if not P.isCayotPause:
            P.writeStaticToMove += (str(P.currentFrame) + "|")
            P.isCayotPause = True

        P.moveArray[P.moveFrame][0] = frame
        P.moveArray[P.moveFrame][1] = diff
        P.moveFrame += 1
        if P.moveFrame == P.arrLength - 1:
            P.out = L.saveFrames(P.out, "MODE")
            processVideo()

        P.objectMoveReset = 0
        P.staticFrames = P.cayotTime

    else:  # Static scene
        if P.isCayotPause:
            P.writeStaticToMove += (str(P.moveFrame) + "&")
            P.isCayotPause = False

        P.staticArray[P.currentFrame] = frame
        P.currentFrame += 1
        if P.currentFrame >= P.arrLength - 1: P.currentFrame = 0

        if P.moveFrame != 0:
            if P.staticFrames == 0:
                P.out = L.saveFrames(P.out, "MODE")
                processVideo()
                P.staticFrames = P.cayotTime

            else:
                P.staticFrames -= 1

            A.putTextPy(f"Cayot time: {P.staticFrames}", (P.WIDTH * .75, P.HEIGHT // 2), size=30)

    A.putTextCv(frame, f"A: {P.currentFrame}", (50, 50))
    A.putTextCv(frame, f"B: {P.moveFrame}", (50, 100))

    return frame
def setTextPost():
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