# --- Imports
import cv2
from threading import Thread, Semaphore
from copy import deepcopy
import numpy as np
from os import listdir
from pathlib import Path

import Params as P
import Settings as S
import Additional as A


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
        print(f"\n\033[{P.fpsColor['info']}mPress Q to stop")

        out = cv2.VideoWriter(f"v3_0/save/{str(P.queueFileCounter).zfill(4)}.avi", cv2.VideoWriter_fourcc(*'FMP4'), 160.0, P.cameraSize)
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
    stopRecord(camera)

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

                cv2.imshow(f"Video: {name}", frame)
                if cv2.waitKey(1) == ord("q"): isRunning = False

            cv2.destroyAllWindows()
            cv2.waitKey(10)

    print(f"\n\n\033[{P.fpsColor['info']}mAll videos have been shown")