# --- Imports
import cv2
from os import listdir
from pathlib import Path
import numpy as np

import Params as P
import Additional as A
import Modes as M


# --- Defs
def logging():
    path = str(Path().absolute())
    files = [f for f in listdir(path+"\\save") if f.count(".")]

    i = 0
    fps = A.FPS("LOG", P.fpsColor['green'])
    while i < len(files):
        file = files[i]
        name = file[0: file.find('.')]

        out = cv2.VideoWriter(path+"\\log\\"+name+".avi", cv2.VideoWriter_fourcc(*'FMP4'), P.FPS, P.cameraSize[-1::-1])

        video = cv2.VideoCapture(path + "\\save\\" + file)
        fps.reset()
        while True:
            ret, frame = video.read()
            if not ret: break

            fps.get()

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame, _ = M.process(gray)
            if np.sum(A.getMask(frame)) > 0:
                out.write( cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR) )

        out.release()
        i += 1

    print(f"\n\n\033[{P.fpsColor['info']}mAll videos have been shown\033[0m")

