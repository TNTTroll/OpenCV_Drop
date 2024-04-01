# --- Imports
import pygame as pg


# --- Defs
# <<< Frames
def putText(screen, text, pos, color=(240, 240, 240), size=40):
    font = pg.font.SysFont(None, size)
    showText = font.render(str(text), True, color)
    screen.blit(showText, (pos[0], pos[1]))


def convertForPygame(cvFrame):
    cvImage = cvFrame[:, :].tobytes()
    cvShape = cvFrame.shape[1::-1]

    try:
        image = pg.image.frombuffer(cvImage, cvShape, 'BGR')

        return image

    except(IndexError, ValueError):
        image = pg.image.frombuffer(cvImage, cvShape, 'P')

        return image

# --- Links
'''
PyGame Image Convert: https://pg1.readthedocs.io/en/latest/ref/image.html#pygame.image.frombuffer
'''