# --- Imports
import cv2
from threading import Thread, Semaphore
from copy import deepcopy
import numpy as np
from os import listdir
from pathlib import Path
from math import sqrt, pow, pi, sin, cos

import Params as P
import Settings as S
import Additional as A


# --- Defs
# <<< RECORD
def startRecord(camera, cycle):
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
            frame = np.array(bytearray(byte)).reshape(P.cameraSize[-1::-1])
            arr[i] = frame
            fps2.get()
        return

    def showing(arr):
        print(f"\n\033[{P.fpsColor['info']}mPress Q to stop\033[0m")
        S.saving()

        out = cv2.VideoWriter(f"save/{str(P.queueFileCounter).zfill(4)}.avi", cv2.VideoWriter_fourcc(*'FMP4'), P.FPS, P.cameraSize[-1::-1])
        P.queueFileCounter += 1

        fps3.reset()
        for i in range(P.queueLimit):
            frame = np.rot90(arr[i])

            out.write( cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR) )
            fps3.get()

            #cv2.imshow("DO NOT CLOSE TILL THE END", frame)
            if cv2.waitKey(1) == ord('q'):
                out.release()
                return 1

        out.release()
        return 0

    s = Semaphore(2)
    i = 0
    while i <= cycle:
        t1 = Thread(target=recording, args=(s, P.queue,), daemon=True)
        t2 = Thread(target=numpying, args=(s, P.queue, P.matrix,))

        t1.start()
        t2.start()
        t2.join()

        if showing(P.matrix): break
        cv2.destroyAllWindows()

        i = i - 1 if i > 1 else 0
        if cycle == 0: break

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

    def getFrame(video):
        ret, frame = video.read()
        if not ret: return 1
        frame = cv2.resize(frame, (frame.shape[1] // 4, frame.shape[0] // 4))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame, mask = process(gray)

        A.setTextCv(frame, count, (50, 50))
        cv2.imshow(f"Video: {name}", frame)
        cv2.imshow(f"Mask: {name}", mask)
        return 0

    fps = A.FPS("", P.fpsColor['green'])
    watching = False
    i = 0
    while i < len(files):
        file = files[i]
        if watching: break
        name = file[0: file.find('.')]
        fps.reset()
        fps.setName(name)
        isRunning = True
        if isRunning:
            video = cv2.VideoCapture(path + "/" + file)
            count = 0
            going = True
            while isRunning:

                k = cv2.waitKey(1)
                if k == ord("q"):
                    watching = True
                    isRunning = False
                elif k == 32:
                    going = not going
                elif k == ord("a"):
                    count -= 1
                    video.set(cv2.CAP_PROP_POS_FRAMES, count)
                    if (getFrame(video)): break
                elif k == ord("d"):
                    count += 1
                    video.set(cv2.CAP_PROP_POS_FRAMES, count)
                    if (getFrame(video)): break
                elif k == ord("z"):
                    count -= 10
                    video.set(cv2.CAP_PROP_POS_FRAMES, count)
                    if (getFrame(video)): break
                elif k == ord("c"):
                    count += 10
                    video.set(cv2.CAP_PROP_POS_FRAMES, count)
                    if (getFrame(video)): break
                elif k == ord("m"):
                    video.set(cv2.CAP_PROP_POS_FRAMES, count)
                    P.measureMode = P.measureMode + 1 if P.measureMode < len(P.measurement) - 1 else 0
                    if (getFrame(video)): break
                elif k == ord("w"):
                    isRunning = False
                elif k == ord("s"):
                    isRunning = False
                    i -= 2

                if going:
                    count += 1
                    if (getFrame(video)): isRunning = False

            cv2.destroyAllWindows()
            cv2.waitKey(10)

        i += 1

    print(f"\n\n\033[{P.fpsColor['info']}mAll videos have been shown\033[0m")

# <<< MODES
def process(frame):
    c = frame.copy()
    filled = A.getMask(c)

    if P.measureMode == 0:
        thresh = cv2.threshold(c, P.maskLimit, 255, cv2.THRESH_BINARY)[1]
        mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel=np.ones((1, 1)), iterations=1)

        output = cv2.connectedComponentsWithStats(filled, 4, cv2.CV_32S)
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
                A.setTextCv(c, a, (l+w, t+h//2), size=.5)

        return c, np.hstack((cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY_INV)[1], filled))

    elif P.measureMode == 1:
        mask = cv2.threshold(c, P.maskLimit, 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.threshold(filled, P.maskLimit, 255, cv2.THRESH_BINARY_INV)[1]

        border = cv2.copyMakeBorder(thresh, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
        contours, hierarchy = cv2.findContours(border, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(-1, -1))

        for x in range(len(contours)):
            if len(contours[x]) >= 5:
                radius = [0, 0]
                distances = []
                for i in range(len(contours[x])-1):
                    for j in range(i + 1, len(contours[x])):
                        p1 = contours[x][i][0]
                        p2 = contours[x][j][0]
                        dist = sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2))
                        distances.append([dist, i, j])

                start = None
                distances.sort(reverse=True)
                for dist in distances:
                    p1 = contours[x][dist[1]][0]
                    p2 = contours[x][dist[2]][0]

                    #line = np.unique(np.round(np.linspace(p1, p2, num=1000)), axis=0).astype('uint8')
                    #if np.all(thresh[line[:, 1], line[:, 0]] == 255):
                    cv2.line(c, p1, p2, (255, 0, 255), 1)
                    start = dist[1]
                    radius[0] = dist[0]
                    break

                if start == None: continue

                orthogonal = []
                for i in range(len(contours[x])):
                    try:
                        p1 = contours[x][start + i][0]
                        p2 = contours[x][start - i][0]
                        dist = sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2))
                        orthogonal.append([dist, i])
                    except(IndexError):
                        break

                orthogonal.sort(reverse=True)
                for dist in orthogonal:
                    p1 = contours[x][start + dist[1]][0]
                    p2 = contours[x][start - dist[1]][0]

                    #line = np.unique(np.round(np.linspace(p1, p2, num=1000)), axis=0).astype('uint8')
                    #if np.all(thresh[line[:, 1], line[:, 0]] == 255):
                    cv2.line(c, p1, p2, (255, 0, 255), 1)
                    radius[1] = dist[0]
                    square = pi * radius[0] * radius[1] / 4
                    A.setTextCv(c, round(square, 2), (p1[0]+10, p1[1]), size=.5)
                    break

        return c, np.hstack((cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY_INV)[1], cv2.threshold(thresh, 127, 255, cv2.THRESH_BINARY_INV)[1]))

    elif P.measureMode == 2:
        mask = cv2.threshold(c, P.maskLimit, 255, cv2.THRESH_BINARY_INV)[1]

        thresh = cv2.threshold(filled, P.maskLimit, 255, cv2.THRESH_BINARY_INV)[1]

        border = cv2.copyMakeBorder(thresh, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
        contours, hierarchy = cv2.findContours(border, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(-1, -1))

        for i in range(len(contours)):
            if len(contours[i]) >= 5:
                h = cv2.fitEllipse(contours[i])
                cv2.ellipse(c, h, (0, 255, 0), 1)

                cx = int(h[0][0])
                cy = int(h[0][1])

                angle = (h[2] * pi) / 180
                a = h[1][0] / 2
                b = h[1][1] / 2

                dots = []
                for i in range(4):
                    alpha = angle + (pi / 2) * i
                    side = a if i % 2 == 0 else b
                    x = cx + int(side * cos(alpha))
                    y = cy + int(side * sin(alpha))
                    dots.append([x, y])

                cv2.line(c, dots[0], dots[2], (255, 0, 0), 1)
                cv2.line(c, dots[1], dots[3], (255, 0, 255), 1)

                volume = pi * a * b
                if P.pxSizeFrame != 0: volume *= P.pxSizeFrame
                A.setTextCv(c, round(volume, 2), (cx + 20, cy), size=.5)

        return c, np.hstack((mask, cv2.threshold(thresh, 127, 255, cv2.THRESH_BINARY_INV)[1]))

# <<< CHESS
def modeChess(camera):
    nline = 4
    ncol = 5
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    while True:
        frame = np.array(bytearray(S.getImage(camera))).reshape(P.cameraSize[-1::-1])
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

                print(f"\n\033[{P.fpsColor['info']}mPixel size: {round(P.pxSizeFrame, 5)}, Cell PX: {round(P.cellPX, 5)}\nReal chess: {P.pxSizeFrame * P.cellPX}\033[0m")

        frame = cv2.resize(frame, (frame.shape[1]//2, frame.shape[0]//2))
        cv2.imshow("CHESS", frame)
        if cv2.waitKey(1) == ord('q'): break

    cv2.destroyAllWindows()
    cv2.waitKey(10)

def videoPool(camera):
    rotate = True
    resize = False
    mask = False
    while True:
        frame = None
        if rotate:
            frame = np.array(bytearray(S.rotateImage(camera))).reshape(P.cameraSize)
        else:
            frame = np.array(bytearray(S.getImage(camera))).reshape(P.cameraSize[-1::-1])

        if resize:
            frame = cv2.resize(frame, (frame.shape[1] // 3, frame.shape[0] // 3))

        if mask:
            thresh = cv2.threshold(frame, P.maskLimit, 255, cv2.THRESH_BINARY)[1]
            maskShow = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel=np.ones((1, 1)), iterations=1)
            cv2.imshow(f"MASK", maskShow)

        cv2.imshow("VIEW", frame)

        k = cv2.waitKey(1)
        if k == ord("q"): break
        elif k == ord('m'):
            rotate = not rotate
        elif k == ord("n"):
            resize = not resize
        elif k == ord("b"):
            mask = not mask
            cv2.destroyAllWindows()

    cv2.destroyAllWindows()
    cv2.waitKey(10)