# --- Imports
import cv2
import pygame as pg
import pygame_gui

import Params as P
import Settings as S
import Additional as A
import Modes as M


# --- Variables
isExternal, camera = S.getCamBySerial()

WIDTH = camera.get(3) * 1.5
HEIGHT = camera.get(4)

pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.NOFRAME)
pg.display.set_caption(P.WINDOW_CAM)
clock = pg.time.Clock()

manager = pygame_gui.UIManager((WIDTH, HEIGHT))
# hello_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((WIDTH - 150, 50), (100, 50)), text='Say Hello', manager=manager)
sliders = [pygame_gui.elements.UIHorizontalSlider(relative_rect=pg.Rect((P.WIDTH - 300, P.statOffsetY + (25 * x) + 150), (200, 25)),
                                                  manager=manager, start_value=P.sets[x],
                                                  value_range=[0, 255], visible=False) for x in range(10)]

# --- Camera
isRunning = True
while isRunning:

    screen.fill((0, 0, 0))
    frame = None

    # <<< Get a frame from camera
    if isExternal:
        frame = S.getImageExternalCam(camera)
    else:
        frame = S.getImageInteranlCam(camera)

    # <<< Check for damaged frame
    try:
        frame = M.getFrame(frame, screen, sliders, [P.modes[P.currentMode], P.modes[P.lastMode]])
        P.lastMode = P.currentMode

        screen.blit(A.convertForPygame(frame), (0, 0))

    except(cv2.error, TypeError):
        A.putText(screen, "| NO SIGNAL |", (WIDTH // 4, HEIGHT // 2))

    # <<< Control Panel
    for i in pg.event.get():
        if i.type == pg.KEYDOWN:  # Exit the program
            if i.key == pg.K_q:
                isRunning = False

            if i.key == pg.K_a:  # Previous mode
                P.currentMode -= 1
                if P.currentMode == -1: P.currentMode = len(P.modes) - 1

            if i.key == pg.K_d:  # Next mode
                P.currentMode += 1
                if P.currentMode == len(P.modes): P.currentMode = 0

            if i.key == pg.K_TAB:  # Toggle fullscreen mode
                P.isTextShown = not P.isTextShown
                if not P.isTextShown:
                    screen = pg.display.set_mode((0, 0), pg.FULLSCREEN, pg.NOFRAME)
                else:
                    screen = pg.display.set_mode((WIDTH, HEIGHT), pg.NOFRAME)

                S.setCamSize(camera)

            if i.key == pg.K_SPACE:  # Flip the frame
                P.checkForFlip = not P.checkForFlip

        # if i.type == pygame_gui.UI_BUTTON_PRESSED:
        #    if i.ui_element == hello_button:
        #        checkForFlip = not checkForFlip

        manager.process_events(i)

    clock.tick(P.FPS)
    time_delta = clock.tick(60) / 1000.0
    manager.update(time_delta)

    manager.draw_ui(screen)
    pg.display.flip()

# --- Exit
S.exit(isExternal, camera, pg)


# --- Links
'''
OpenCV + PyGame: https://memotut.com/en/f26e2756da774c164a47/
PyGame Widgets: https://pygamewidgets.readthedocs.io/en/stable/
PyGame GUI: https://pygame-gui.readthedocs.io/en/latest/index.html
'''