# --- Imports
import cv2
import numpy as np
import pygame as pg

import Params as P


# --- Defs
# <<< Text
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
        putTextPy(f"{int(len(P.medianFrames) / P.medianLength * 100)}%", (P.WIDTH * .8, P.HEIGHT // 2 + 125), size=30)

        try:
            if frame == None:
                return
        except(ValueError):
            P.medianFrames.append(frame)

    else:  # Generate new median
        median = np.median(P.medianFrames, axis=0).astype(dtype=np.uint8)
        cv2.imwrite(P.medianName, median)

        P.medianFrames.append(0)  # Make array's len = need len. Stop array filling

        putTextPy("Saved", (P.WIDTH * .8, P.HEIGHT // 2 + 125), size=30)

# <<< Output frame
def convertForPygame(cvFrame):

    if len(cvFrame.shape) < 3:
        cvFrame = cv2.cvtColor(cvFrame, cv2.COLOR_GRAY2RGB)

    cvImage = cvFrame[:, :].tobytes()
    cvShape = cvFrame.shape[1::-1]

    image = pg.image.frombuffer(cvImage, cvShape, 'BGR')

    return image

# <<< Recording
def recording(set):
    P.isRecording = set
    if set:
        print("\nStart a recording")
        P.out = cv2.VideoWriter(P.path, P.fourcc, P.FPS, (640, 480))

    else:
        print("\nStop a recording")
        P.out.release()

# <<< Reset
def resetAllParams():
    print("RESET ALL")

    P.dynamicFrames = []
    # TODO: Add here all necessaries params that need to clear

# --- Links
'''
PyGame Image Convert: https://pg1.readthedocs.io/en/latest/ref/image.html#pygame.image.frombuffer
'''