# --- Imports
import cv2
import pygame as pg
import pygame_gui
from pypylon import pylon
from pypylon_opencv_viewer import BaslerOpenCVViewer

import Params as P
import Additional as A


# --- Defs
# <<< Program
def setScreen():
    P.screen = pg.display.set_mode((P.WIDTH, P.HEIGHT))
    P.manager = pygame_gui.UIManager((P.WIDTH, P.HEIGHT))

    P.sliders = [ pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pg.Rect((P.WIDTH - 250, 70 + (25 * x)), (175, 25)),
        manager=P.manager, start_value=P.sets[x],
        value_range=[0, P.maxs[x]], visible=False) for x in range(len(P.sets)) ]

    # Switch camera
    P.buttons[0] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH - 60, 10), (50, 50)),
                                                text=P.cameraModeText[P.cameraMode][0],
                                                manager=P.manager)

    # Start/Stop record
    P.buttons[1] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH * .75, P.HEIGHT//2-25), (150, 50)),
                                                text="Record", manager=P.manager, visible=False)

    P.buttons[2] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH * .75, P.HEIGHT//2-25), (150, 50)),
                                                text="Stop", manager=P.manager, visible=False)

    # Set a median
    P.buttons[3] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH * .75, P.HEIGHT // 2 + 50), (150, 50)),
                                                text="Background", manager=P.manager, visible=False)


def exit(camera, program):
    closeExternalCam(camera) if P.isExternal else closeInternalCam(camera)

    program.quit()
    cv2.destroyAllWindows()
    cv2.waitKey(10)

    print("\n\nProgram has been closed")


# <<< Camera
def getCamBySerial():

    if P.cameraMode == 2:
        P.cameraMode = 1

        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        setCamSize(camera, "Internal")

        return None, camera, camera.get(3) * 1.75, camera.get(4)

    for i in pylon.TlFactory.GetInstance().EnumerateDevices():
        if i.GetSerialNumber() == P.serialNumber:
            P.cameraMode = 2

            camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(i))
            camera.Open()

            setCamSize(camera, "External")

            camera.StartGrabbing(1)

            return i, camera, camera.Width.GetValue() * 1.35, camera.Height.GetValue()
    else:
        P.cameraMode = 1

        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        setCamSize(camera, "Internal")

        return None, camera, camera.get(3) * 1.5, camera.get(4)

def setCamSize(camera, type):
    if type == "External":
        if P.isTextShown:
            camera.Width.SetValue( int(P.cameraSizeExternal[0] * P.coefficient) )
            camera.Height.SetValue( int(P.cameraSizeExternal[1] * P.coefficient) )
        else:
            camera.Width.SetValue( P.cameraSizeExternal[0] )
            camera.Height.SetValue( P.cameraSizeExternal[1] )

    else:
        if P.isTextShown:
            camera.set( cv2.CAP_PROP_FRAME_WIDTH, int(P.cameraSizeInternal[0] * P.coefficient) )
            camera.set( cv2.CAP_PROP_FRAME_HEIGHT, int(P.cameraSizeInternal[1] * P.coefficient) )

        else:
            camera.set( cv2.CAP_PROP_FRAME_WIDTH, P.cameraSizeInternal[0] )
            camera.set( cv2.CAP_PROP_FRAME_HEIGHT, P.cameraSizeInternal[1] )

def getImageExternalCam(camera):
    grab = camera.RetrieveResult(2000, pylon.TimeoutHandling_Return)

    if grab != None:
        if grab.GrabSucceeded():
            return grab.GetArray()
    return None
def closeExternalCam(camera):
    camera.Close()

def getImageInteranlCam(camera):
    ret, frame = camera.read()

    return frame if ret else None
def closeInternalCam(camera):
    camera.release()