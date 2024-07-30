# --- Imports
from random import randint
import cv2
import pygame as pg
import pygame_gui
from time import time

import Params as P
import Additional as A
from IMVApi import *


# --- Defs
# <<< PROGRAM
def setScreen():
    P.screen = pg.display.set_mode((P.WIDTH, P.HEIGHT))
    P.manager = pygame_gui.UIManager((P.WIDTH, P.HEIGHT))

    A.addText("DropCV", (P.WIDTH // 2 - 100, 40), size=80, duration=-1)

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

    A.setText()

    return now

def exit(camera, program):
    if camera != None:
        closeCamera(camera)

    program.quit()
    cv2.destroyAllWindows()
    cv2.waitKey(10)

    print(f"\n\n\033[{P.fpsColor['purple']}mProgram has been closed\033[0m")

def updating(set):
    P.screen.fill(P.colors['black'])
    P.isUpdate = set
    
    if not set:
        font = pg.font.SysFont(None, 50)
        showText = font.render("RECORDING", True, P.colors['text'])
        P.screen.blit(showText, (P.WIDTH*.16, P.HEIGHT*.4))
        showText = font.render("(maybe)", True, P.colors['text'])
        P.screen.blit(showText, (P.WIDTH * .28, P.HEIGHT*.6))
        pg.display.flip()

        if P.isExtra: print(f"\n\033[{P.fpsColor['info']}m{A.getText()}\033[0m\n")

# <<< CAMERA
def getCamera():
    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    camera = MvCamera()

    camera.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    camera.IMV_Open()
    camera.IMV_StartGrabbing()

    if camera.IMV_GetFrame(IMV_Frame(), 1000) != 0:
        A.addText("NO CAM", (P.WIDTH // 2 - 50, P.HEIGHT * .9))
        print(f"\n\n\033[{P.fpsColor['camera']}mCamera not connected\033[0m")
        return None
    else:
        print(f"\n\n\033[{P.fpsColor['camera']}mCamera was opened\033[0m")
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

    print(f"\n\n\033[{P.fpsColor['camera']}mCamera was closed\033[0m")






















