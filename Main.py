# --- Imports
import cv2
import pygame as pg
import pygame_gui

import Params as P
import Settings as S
import Additional as A
import Modes as M


# --- Variables
P.isExternal, camera, P.WIDTH, P.HEIGHT = S.getCamBySerial()

pg.init()
pg.mixer.init()
pg.display.set_caption(P.WINDOW_CAM)
clock = pg.time.Clock()

S.setScreen()


# --- Camera
isRunning = True
while isRunning:

    P.screen.fill((0, 0, 0))
    frame = None

    # <<< Get a frame from camera
    if P.isExternal:
        frame = S.getImageExternalCam(camera)
    else:
        frame = S.getImageInteranlCam(camera)

    # <<< Work with frame
    M.getFrame(frame, [P.modes[P.currentMode], P.modes[P.lastMode]])
    P.lastMode = P.currentMode

    # <<< Control Panel
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:  # Exit the program
            if event.key == pg.K_q:
                if not P.isRecording:
                    isRunning = False
                else:
                    A.putTextPy("Recording in progress", (P.WIDTH * .75, P.HEIGHT//2-80), size=25)

            if event.key == pg.K_a:  # Previous mode
                P.currentMode -= 1
                if P.currentMode == -1: P.currentMode = len(P.modes) - 1

            if event.key == pg.K_d:  # Next mode
                P.currentMode += 1
                if P.currentMode == len(P.modes): P.currentMode = 0

            if event.key == pg.K_TAB:  # Toggle Settings and Recording modes
                if not P.isRecording:
                    P.isTextShown = not P.isTextShown
                else:
                    A.putTextPy("Recording in progress", (P.WIDTH * .75, P.HEIGHT//2-80), size=25)

            if event.key == pg.K_SPACE:  # Flip the frame
                P.checkForFlip = not P.checkForFlip

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == P.buttons[0]:  # Switch camera

                if P.cameraMode != 0:
                    S.closeExternalCam(camera) if P.isExternal else S.closeInternalCam(camera)

                previousCam = P.cameraMode
                P.isExternal, camera, P.WIDTH, P.HEIGHT = S.getCamBySerial()

                S.setScreen()
                M.setModeChoise(P.modes[P.currentMode], True)

                if previousCam == P.cameraMode:
                    A.putTextPy("No Connection", (P.WIDTH*.75+30, 30), size=20)

            if event.ui_element == P.buttons[1]:  # Start recording
                P.isRecording = True
                print("\nStart a recording")

                P.out = cv2.VideoWriter(P.path, P.fourcc, P.FPS, (640, 480))

            if event.ui_element == P.buttons[2]:  # Stop recording
                P.isRecording = False
                print("\nStop a recording")

                P.out.release()

        P.manager.process_events(event)

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
- Сохранение фона 
- Вычитание из фона
- Попробовать фильтр Собеля
'''