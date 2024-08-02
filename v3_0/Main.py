# --- Imports
import pygame as pg
import pygame_gui
from time import time

import Params as P
import Additional as A
import Modes as M
import Logging as L
import Settings as S


# --- Variables
pg.init()
pg.mixer.init()
pg.display.set_caption(P.windowName)
clock = pg.time.Clock()

S.setScreen()
camera = S.getCamera()


# --- Camera
isRunning = True
t = time()
while isRunning:

    t = S.setBG(t)

    # <<< CONTROL PANEL
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:  # Exit the program
            if event.key == pg.K_q:
                isRunning = False

            if event.key == pg.K_SPACE:  # Enter 'real-time' mode
                if camera == None:
                    camera = S.getCamera()
                if camera != None:
                    M.videoPool(camera)

            if event.key == pg.K_e:
                P.recordMode = P.recordMode+1 if P.recordMode < 1 else 0
                A.addText(f"{P.recording[P.recordMode]}", (int(P.WIDTH * .3), int(P.HEIGHT * .9)))

            if event.key == pg.K_g:
                print(f"\n\033[{P.fpsColor['info']}m{A.getText()}\033[0m\n")

            if event.key == pg.K_m:  # Change measurement mode
                P.measureMode = P.measureMode+1 if P.measureMode < len(P.measurement)-1 else 0
                A.addText(f"{P.measurement[P.measureMode]}", (int(P.WIDTH*.3), int(P.HEIGHT*.9)))

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == P.buttons[0]:  # Record
                if camera == None:
                    camera = S.getCamera()
                if camera != None:
                    M.startRecord(camera, P.recordMode)

            if event.ui_element == P.buttons[1]:  # Replay
                M.replay()

            if event.ui_element == P.buttons[2]:  # Logging
                L.logging()

            if event.ui_element == P.buttons[3]:  # Chessboard
                if camera == None:
                    camera = S.getCamera()
                if camera != None:
                    M.modeChess(camera)

            if event.ui_element == P.buttons[4]:  # Background
                if camera == None:
                    camera = S.getCamera()
                if camera != None:
                    A.getMedian(camera)

        P.manager.process_events(event)

    # <<< PROCESS THE WINDOW
    if P.isUpdate:
        clock.tick(P.FPS)
        time_delta = clock.tick(60) / 1000.0
        P.manager.update(time_delta)

        P.manager.draw_ui(P.screen)
        pg.display.flip()


# --- Exit
S.exit(camera, pg)