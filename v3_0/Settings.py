# --- Imports
from random import randint
import cv2
import pygame as pg
import pygame_gui
from time import time

import Params as P
import Additional as A
from v3_0.IMVApi import *


# --- Defs
# <<< Program
def setScreen():
    P.screen = pg.display.set_mode((P.WIDTH, P.HEIGHT))
    P.manager = pygame_gui.UIManager((P.WIDTH, P.HEIGHT))

    # Record
    P.buttons[0] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH*.15, 150), (P.WIDTH*.7, P.HEIGHT*.15)),
                                                text=P.buttons[0], manager=P.manager)

    # Replay
    P.buttons[1] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH*.15, 250), (P.WIDTH*.7, P.HEIGHT*.15)),
                                                text=P.buttons[1], manager=P.manager)

    # Logging
    P.buttons[2] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH*.15, 350), (P.WIDTH*.7, P.HEIGHT*.15)),
                                                text=P.buttons[2], manager=P.manager)

def setBG(lastTime):
    P.screen.fill(P.colors['BG'])

    now = lastTime
    i = 0
    if time() - lastTime > .5:
        P.orbs.append( A.Orb([float(randint(0, P.WIDTH)), 0]) )
        now = time()
    while i < len(P.orbs):
        if P.orbs[i].drop(): P.orbs.pop(i)
        i += 1

    A.setText("DropCV", (P.WIDTH//2-100, 40), size=80)

    return now

def exit(camera, program):
    closeCamera(camera)

    program.quit()
    cv2.destroyAllWindows()
    cv2.waitKey(10)

    print("\n\n\033[1;35mProgram has been closed")

# <<< Camera
def getCamera():
    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    camera = MvCamera()

    camera.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    camera.IMV_Open()
    camera.IMV_StartGrabbing()

    return camera

def getImage(camera):
    frame = IMV_Frame()

    stPixelConvertParam = IMV_PixelConvertParam()
    camera.IMV_GetFrame(frame, 1000)

    nDstBufSize = frame.frameInfo.width * frame.frameInfo.height
    memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))

    stPixelConvertParam.nDstBufSize = nDstBufSize
    stPixelConvertParam.pSrcData = frame.pData

    camera.IMV_ReleaseFrame(frame)

    imageBuff = stPixelConvertParam.pSrcData
    userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
    memmove(userBuff, imageBuff, stPixelConvertParam.nDstBufSize)

    return userBuff

def closeCamera(camera):
    camera.IMV_StopGrabbing()
    camera.IMV_Close()
    if camera.handle: camera.IMV_DestroyHandle()
