# --- Imports
# <<< isExternal
import cv2
import numpy as np
from pypylon import pylon

# <<< Modules
from Params import *
import Settings as S
import Modes as M
import Additional as A

# --- Variables
global par00, par01, par02, par03, par04, par05, par06, par07, par08, par09

checkForFlip = False
currentMode = lastMode = 0

# <<< Windows
main = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
main[:, :, :] = 0
stats = np.zeros((HEIGHT, 500, 3), np.uint8)
stats[:, :, :] = 200

# --- Using
S.setWindows()

isExternal = S.getCamBySerial()
if isExternal:
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(isExternal))
    camera.Open()

    camera.Width.SetValue(WIDTH)
    camera.Height.SetValue(HEIGHT)

    camera.StartGrabbing(1)

else:
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

# Start video capture
while True:

    frame = None
    statisticFrame = stats.copy()

    # <<< Get a frame from camera
    if isExternal:
        frame = S.getImageExternalCam(camera)
    else:
        frame = S.getImageInteranlCam(camera)

    if (checkForFlip):
        frame = cv2.flip(frame, 1)

    # <<< Check for damaged frame
    try:
        frame = frame[par06:(HEIGHT - par07 + 1), par08:(WIDTH - par09 + 1)]

        frame = M.getFrame(frame, statisticFrame, [modes[currentMode], modes[lastMode]], isTextShown)
        lastMode = currentMode

        cv2.imshow(WINDOW_CAM, frame)
        cv2.imshow(WINDOW_PARAMS, statisticFrame)

    except(cv2.error, TypeError):
        showMain = main.copy()
        A.putText(showMain, "NO SIGNAL", [int(WIDTH * .4), 50], WHITE)
        cv2.imshow(WINDOW_CAM, showMain)

    # <<< Control panel
    k = cv2.waitKey(10) & 0xFF
    if (k == ord('q')):  # Exit
        break

    elif (k == ord('a')):  # Change mode "to left"
        currentMode -= 1
        if (currentMode == -1): currentMode = len(modes) - 1

    elif (k == ord('d')):  # Change mode "to right"
        currentMode += 1
        if (currentMode == len(modes)): currentMode = 0

    elif (k == 9):  # Hide text
        isTextShown = not isTextShown

    elif (k == 32):  # Flip the frame
        checkForFlip = not checkForFlip

S.exit(isExternal, camera)
