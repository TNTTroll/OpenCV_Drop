# --- Imports
import cv2

import Params as P


# --- Defs
def logging(frame, info):
    out = cv2.VideoWriter(f"save/{str(P.queueFileCounter).zfill(4)}.avi", cv2.VideoWriter_fourcc(*'FMP4'), 160.0,
                          P.cameraSize)
    P.queueFileCounter += 1

    out.write(cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR))

    out.release()