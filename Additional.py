# --- Imports
import cv2
import pygame as pg

import Params as P


# --- Defs
# <<< Frames
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


def convertForPygame(cvFrame):

    if len(cvFrame.shape) < 3:
        cvFrame = cv2.cvtColor(cvFrame, cv2.COLOR_GRAY2RGB)

    cvImage = cvFrame[:, :].tobytes()
    cvShape = cvFrame.shape[1::-1]

    image = pg.image.frombuffer(cvImage, cvShape, 'BGR')

    return image

# --- Links
'''
PyGame Image Convert: https://pg1.readthedocs.io/en/latest/ref/image.html#pygame.image.frombuffer
'''