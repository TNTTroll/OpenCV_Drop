# --- Imports
import cv2
from threading import Thread, Semaphore
from copy import deepcopy
import numpy as np
from os import listdir
from pathlib import Path
from math import sqrt, pow, pi

import Params as P
import Settings as S
import Additional as A
import Logging as L


# --- Defs
# <<< RECORD
def startRecord(camera):
    S.updating(False)

    fps1 = A.FPS("SAVE", P.fpsColor['purple'])
    fps2 = A.FPS("NUMPY", P.fpsColor['gray'])
    fps3 = A.FPS("SHOW", P.fpsColor['blue'])

    def recording(s: Semaphore, q):
        fps1.reset()
        for i in range(P.queueLimit):
            frame = S.getImage(camera)
            with s: q.put(frame)
            fps1.get()
        return

    def numpying(s: Semaphore, q, arr):
        fps2.reset()
        for i in range(P.queueLimit):
            with s: byte = deepcopy(q.get())
            frame = np.array(bytearray(byte)).reshape(1200, 1920)
            arr[i] = frame
            fps2.get()
        return

    def showing(arr):
        print(f"\n\033[{P.fpsColor['info']}mPress Q to stop\033[0m")

        out = cv2.VideoWriter(f"save/{str(P.queueFileCounter).zfill(4)}.avi", cv2.VideoWriter_fourcc(*'FMP4'), 160.0, P.cameraSize)
        P.queueFileCounter += 1

        fps3.reset()
        for i in range(P.queueLimit):
            frame = arr[i]

            out.write( cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR) )
            fps3.get()

            cv2.imshow("RECORDED", frame)
            if cv2.waitKey(1) == ord('q'):
                out.release()
                return 1

        out.release()
        return 0

    s = Semaphore(2)
    while True:
        t1 = Thread(target=recording, args=(s, P.queue,), daemon=True)
        t2 = Thread(target=numpying, args=(s, P.queue, P.matrix,))

        t1.start()
        t2.start()
        t2.join()

        if showing(P.matrix): break

    cv2.destroyAllWindows()
    cv2.waitKey(10)
    S.updating(True)

def stopRecord(camera):
    S.closeCamera(camera)

    S.updating(True)

# <<< REPLAY
def replay():
    path = str(Path().absolute()) + "\\save"
    files = [f for f in listdir(path) if f.count(".")]

    fps = A.FPS("", P.fpsColor['green'])
    isRunning = True
    for file in files:

        name = file[0 : file.find('.')]
        fps.reset()
        fps.setName(name)
        if isRunning:
            video = cv2.VideoCapture(path + "/" + file)
            while isRunning:
                ret, frame = video.read()
                if not ret: break

                fps.get()

                cv2.imshow(f"Video: {name}", processReplay(frame))
                if cv2.waitKey(1) == ord("q"): isRunning = False

            cv2.destroyAllWindows()
            cv2.waitKey(10)

    print(f"\n\n\033[{P.fpsColor['info']}mAll videos have been shown\033[0m")

# <<< MEASURE
def measure(camera):
    S.updating(False)

    fps1 = A.FPS("SAVE", P.fpsColor['purple'])
    fps2 = A.FPS("NUMPY", P.fpsColor['gray'])
    fps3 = A.FPS("SHOW", P.fpsColor['blue'])

    def recording(s: Semaphore, q):
        fps1.reset()
        for i in range(P.queueLimit):
            frame = S.getImage(camera)
            with s: q.put(frame)
            fps1.get()
        return

    def numpying(s: Semaphore, q, arr):
        fps2.reset()
        for i in range(P.queueLimit):
            with s: byte = deepcopy(q.get())
            frame = np.array(bytearray(byte)).reshape(1200, 1920)
            arr[i] = frame
            fps2.get()
        return

    def showing(arr):
        print(f"\n\033[{P.fpsColor['info']}mPress Q to stop\033[0m")

        fps3.reset()
        for i in range(P.queueLimit):
            frame = arr[i]

            median = cv2.imread(P.medianName, 0)
            frame = cv2.absdiff(frame, median)

            thresh = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY)[1]

            mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel=np.ones((4, 4)), iterations=1)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=np.ones((4, 4)), iterations=1)

            if np.sum(mask) > 0:  # There are object on the scene
                show = processMeasure(frame)

                L.logging(frame, show)

                cv2.imshow("MEASURE", show)
                fps3.get()

            if cv2.waitKey(1) == ord("q"):
                return 1

        return 0

    s = Semaphore(2)
    while True:
        t1 = Thread(target=recording, args=(s, P.queue,), daemon=True)
        t2 = Thread(target=numpying, args=(s, P.queue, P.matrix,))

        t1.start()
        t2.start()
        t2.join()

        if showing(P.matrix): break

    cv2.destroyAllWindows()
    cv2.waitKey(10)
    S.updating(True)

# <<< MODES
def processMeasure(frame):
    c = frame.copy()
    if P.measureMode == 0:
        thresh = cv2.threshold(c, 127, 255, cv2.THRESH_BINARY)[1]

        mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel=np.ones((1, 1)), iterations=1)
        # mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=np.ones((4, 4)), iterations=1)
        # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=np.ones((4, 4)), iterations=1)

        output = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
        num_labels = output[0]
        stats = output[2]

        for i in range(num_labels):
            a = stats[i, cv2.CC_STAT_AREA]
            t = stats[i, cv2.CC_STAT_TOP]
            l = stats[i, cv2.CC_STAT_LEFT]
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]

            if w != frame.shape[1]:
                cv2.rectangle(c, (l, t), (l + w, t + h), (255, 0, 255), 1)
                A.setTextCv(c, a, (l+w, t))
        return c

    else:
        thresh = cv2.threshold(c, 127, 255, cv2.THRESH_BINARY_INV)[1]

        border = cv2.copyMakeBorder(thresh, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
        contours, hierarchy = cv2.findContours(border, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(-1, -1))

        radius = [0, 0]
        distances = []
        for i in range(len(contours[0])):
            for j in range(i + 1, len(contours[0])):
                p1 = contours[0][i][0]
                p2 = contours[0][j][0]
                dist = sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2))
                distances.append([dist, i, j])

        start = None
        distances.sort(reverse=True)
        for dist in distances:
            p1 = contours[0][dist[1]][0]
            p2 = contours[0][dist[2]][0]

            line = np.unique(np.round(np.linspace(p1, p2, num=1000)), axis=0).astype('uint8')
            if np.all(thresh[line[:, 1], line[:, 0]] == 255):
                cv2.line(c, p1, p2, (255, 0, 255), 1)
                start = dist[1]
                radius[0] = dist[0]
                break

        if start == None: return c

        orthogonal = []
        for i in range(len(contours[0])):
            try:
                p1 = contours[0][start + i][0]
                p2 = contours[0][start - i][0]
                dist = sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2))
                orthogonal.append([dist, i])
            except(IndexError):
                break

        orthogonal.sort(reverse=True)
        for dist in orthogonal:
            p1 = contours[0][start + dist[1]][0]
            p2 = contours[0][start - dist[1]][0]

            line = np.unique(np.round(np.linspace(p1, p2, num=1000)), axis=0).astype('uint8')
            if np.all(thresh[line[:, 1], line[:, 0]] == 255):
                cv2.line(c, p1, p2, (255, 0, 255), 1)
                radius[1] = dist[0]
                break

        square = pi * radius[0] * radius[1] / 4
        A.setTextCv(c, square, (50, 50))

        return c

def processReplay(frame):

    line = findPoints(frame)
    outline = findBorder(frame, line)

    return outline

def findPoints(frame):
    temp = frame.copy()

    gray = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)[1]

    border = cv2.copyMakeBorder(thresh, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    contours, hierarchy = cv2.findContours(border, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(-1, -1))

    distances = []
    for i in range(len(contours[0]) - 1):
        for j in range(i + 1, len(contours[0])):
            p1 = contours[0][i][0]
            p2 = contours[0][j][0]
            dist = sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2))

            distances.append([dist, i, j])

    distances.sort(reverse=True)
    for dist in distances:
        p1 = contours[0][dist[1]][0]
        p2 = contours[0][dist[2]][0]
        line = np.unique(np.round(np.linspace(p1, p2, num=1000)), axis=0).astype('uint8')
        if np.all(thresh[line[:, 1], line[:, 0]] == 255):
            cv2.line(temp, p1, p2, (255, 0, 255), 1)
            break

    return temp

def findBorder(frame, lines):
    c = lines.copy()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]

    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel=np.ones((1, 1)), iterations=1)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=np.ones((4, 4)), iterations=1)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=np.ones((4, 4)), iterations=1)

    output = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
    num_labels = output[0]
    stats = output[2]

    for i in range(num_labels):
        t = stats[i, cv2.CC_STAT_TOP]
        l = stats[i, cv2.CC_STAT_LEFT]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]

        if w != frame.shape[1]:
            cv2.rectangle(c, (l, t), (l + w, t + h), (255, 0, 255), 1)
            A.setTextCv(c, w, (int(l + w*.3), int(t + h)))
            A.setTextCv(c, h, (int(l + w), int(t + h * .5)))

    return c

# <<< CHESS
def modeChess(camera):
    nline = 4
    ncol = 5
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    while True:
        frame = np.array(bytearray( S.getImage(camera) )).reshape(1200, 1920)
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

        cv2.imshow("CHESS", frame)
        if cv2.waitKey(1) == ord('c'): break

    cv2.destroyAllWindows()
    cv2.waitKey(10)