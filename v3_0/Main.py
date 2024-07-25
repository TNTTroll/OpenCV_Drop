# --- Imports
import pygame as pg
import pygame_gui
from time import time

import Params as P
import Additional as A
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
    frame = None

    # <<< Control Panel
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:  # Exit the program
            if event.key == pg.K_q:
                isRunning = False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == P.buttons[0]:  # Record
                pass

            if event.ui_element == P.buttons[1]:  # Replay
                pass

            if event.ui_element == P.buttons[2]:  #Logging
                A.setText("IN DEV", (P.WIDTH//2-50, P.HEIGHT*.9))

        P.manager.process_events(event)

    # <<< Process the window
    clock.tick(P.FPS)
    time_delta = clock.tick(60) / 1000.0
    P.manager.update(time_delta)

    P.manager.draw_ui(P.screen)
    pg.display.flip()


# --- Exit
S.exit(camera, pg)