# --- Imports
import pygame as pg
import pygame_gui
from os import listdir
from time import time

import Params as P
import Settings as S
import Additional as A
import Modes as M
import Logging as L

# --- Variables
P.isExternal, camera, P.WIDTH, P.HEIGHT = S.getCamBySerial()

pg.init()
pg.mixer.init()
pg.display.set_caption(P.WINDOW_CAM)
clock = pg.time.Clock()

S.setScreen()
#L.calibrationCreateFirst()

#P.threadCount = int( len([f for f in listdir(P.logFolder) if not f.count(".") and
#                 not f.count(P.calibrationFolder[:-1])]) )


# --- Camera
saveFrame = None
isRunning = True
while isRunning:

    P.screen.fill((0, 0, 0))
    frame = None

    # <<< Get a frame from camera
    if P.isExternal:
        frame = S.getImageExternalCam(camera)
    else:
        frame = S.getImageInteranlCam(camera)

    # <<< Get a new median
    A.getMedian(frame)

    # <<< Control Panel
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:  # Exit the program
            if event.key == pg.K_q:
                if not P.isRecording:
                    isRunning = False
                else:
                    A.recording(False)

            if event.key == pg.K_a:  # Previous mode
                P.currentMode -= 1
                if P.currentMode == -1: P.currentMode = len(P.modes) - 1

            if event.key == pg.K_d:  # Next mode
                P.currentMode += 1
                if P.currentMode == len(P.modes): P.currentMode = 0

            if event.key == pg.K_TAB:  # Toggle Settings and Recording modes
                P.isReady = not P.isReady

            if event.key == pg.K_f:  # Flip the frame
                P.isFlip = not P.isFlip

            if event.key == pg.K_SPACE:  # Pause the video
                P.isGoing = not P.isGoing

            if event.key == pg.K_F3 and not P.isFPS:  # Get camera FPS
                P.isFPS = not P.isFPS
                P.FPSStart = time()
                P.FPSCount = 0

            # Control the "Last frame" mode
            if event.key == pg.K_w:
                P.lastFrameMode += 1
            elif event.key == pg.K_s:
                P.lastFrameMode -= 1

            P.lastFrameMode = min(P.lastFrameMode, 4)
            P.lastFrameMode = max(P.lastFrameMode, 0)

            P.lastFrames = [0 for x in range(P.lastFrameMode)]

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == P.buttons[0]:  # Switch camera

                if P.cameraMode != 0:
                    S.closeExternalCam(camera) if P.isExternal else S.closeInternalCam(camera)

                previousCam = P.cameraMode
                P.isExternal, camera, P.WIDTH, P.HEIGHT = S.getCamBySerial()

                S.setScreen()
                M.setModeChoise(P.modes[P.currentMode], True)

                if previousCam == P.cameraMode:
                    A.addText("No Connection", (P.WIDTH * .75 + 30, 30), size=20)
                else:
                    A.resetAllParams()

            if event.ui_element == P.buttons[1]:  # Start recording
                A.recording(True)

            if event.ui_element == P.buttons[2]:  # Stop recording
                A.recording(False)

            if event.ui_element == P.buttons[3]:  # Set a background
                P.medianFrames = []

            if event.ui_element == P.buttons[4]:  # Is saving images enabled
                P.isImageSave = not P.isImageSave

            if event.ui_element == P.buttons[5]:  # Set previous calibration settings
                L.calibrationSetPrevious()

            if event.ui_element == P.buttons[6]:  # Save new calibration settings
                L.calibrationSaveNew()

        P.manager.process_events(event)

    if P.isGoing:
        saveFrame = frame
    else:
        A.addText("PAUSE", (P.WIDTH * .8, P.HEIGHT // 3 - 60))

    # <<< Work with frame
    M.getFrame(saveFrame, [P.modes[P.currentMode], P.modes[P.lastMode]])
    P.lastMode = P.currentMode

    # <<< FPS
    if P.isFPS: S.fps()

    # <<< Process the window
    clock.tick(P.FPS)
    time_delta = clock.tick(60) / 1000.0
    P.manager.update(time_delta)

    P.manager.draw_ui(P.screen)
    pg.display.flip()

# --- Exit
S.exit(camera, pg)


# --- Links
'''
OpenCV + PyGame: https://memotut.com/en/f26e2756da774c164a47/
PyGame Widgets: https://pygamewidgets.readthedocs.io/en/stable/
PyGame GUI: https://pygame-gui.readthedocs.io/en/latest/index.html
'''

'''
- Попробовать записывать видео с ухудшением качества
'''
