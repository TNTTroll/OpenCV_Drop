# --- Imports
import cv2

from Params import *


# --- Defs
# <<< Frames
def putText(frame, text, pos, color=(10, 10, 10), fontScale=1):
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (pos[0], pos[1])
    thickness = 2
    outline = [(255 - x) for x in color]

    cv2.putText(frame, str(text), org, font,
                fontScale, outline, thickness + 2, cv2.LINE_AA)
    cv2.putText(frame, str(text), org, font,
                fontScale, color, thickness, cv2.LINE_AA)