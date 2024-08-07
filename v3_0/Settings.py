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
    P.buttons[0] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH*.15, 120), (P.WIDTH*.7, P.HEIGHT*.12)),
                                                text=P.buttons[0], manager=P.manager)

    # Replay
    P.buttons[1] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH*.15, 190), (P.WIDTH*.7, P.HEIGHT*.12)),
                                                text=P.buttons[1], manager=P.manager)

    # Measure
    P.buttons[2] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH*.15, 260), (P.WIDTH*.7, P.HEIGHT*.12)),
                                                text=P.buttons[2], manager=P.manager)

    # Chessboard
    P.buttons[3] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH*.15, 330), (P.WIDTH*.7, P.HEIGHT*.12)),
                                                text=P.buttons[3], manager=P.manager)

    # Background
    P.buttons[4] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH*.15, 400), (P.WIDTH*.7, P.HEIGHT*.12)),
                                                text=P.buttons[4], manager=P.manager)

def setBG(lastTime):
    P.screen.fill(P.colors['BG'])

    now = lastTime
    i = 0
    if time() - lastTime > .5:
        P.orbs.append( A.Orb([float(randint(0, P.WIDTH)), 0], randint(5, 15)) )
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

def saving():
    P.screen.fill(P.colors['black'])

    font = pg.font.SysFont(None, 50)
    showText = font.render("SAVING", True, P.colors['text'])
    P.screen.blit(showText, (P.WIDTH * .30, P.HEIGHT * .4))
    showText = font.render("(truly)", True, P.colors['text'])
    P.screen.blit(showText, (P.WIDTH * .32, P.HEIGHT * .6))
    pg.display.flip()

# <<< CAMERA
def getCamera():
    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    camera = MvCamera()

    camera.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    camera.IMV_Open()
    camera.IMV_StartGrabbing()

    frame = IMV_Frame()
    camera.IMV_GetFrame(frame, 1000)
    if frame.frameInfo.width != 0:
        P.cameraSize[0] = frame.frameInfo.width
        P.cameraSize[1] = frame.frameInfo.height
        print(f"\n\n\033[{P.fpsColor['info']}mCamera [{P.cameraSize[0]}:{P.cameraSize[1]}]\033[0m")

    if camera.IMV_GetFrame(IMV_Frame(), 1000) != 0:
        A.addText("NO CAM", (P.WIDTH // 2 - 50, P.HEIGHT * .9))
        print(f"\n\n\033[{P.fpsColor['camera']}mCamera not connected\033[0m")
        return None
    else:
        print(f"\n\n\033[{P.fpsColor['camera']}mCamera was opened\033[0m")
        return camera

def rotateImage(camera):
    frame = IMV_Frame()
    camera.IMV_GetFrame(frame, 500)

    stRotateImageParam = IMV_RotateImageParam()
    memset(byref(stRotateImageParam), 0, sizeof(stRotateImageParam))

    stRotateImageParam.pSrcData = frame.pData
    stRotateImageParam.nSrcDataLen = frame.frameInfo.width * frame.frameInfo.height
    stRotateImageParam.ePixelFormat = frame.frameInfo.pixelFormat

    nRotateBufSize = frame.frameInfo.width * frame.frameInfo.height

    stRotateImageParam.nWidth = frame.frameInfo.width
    stRotateImageParam.nHeight = frame.frameInfo.height
    stRotateImageParam.eRotationAngle = 2
    stRotateImageParam.pDstBuf = (c_ubyte * nRotateBufSize)()
    stRotateImageParam.nDstBufSize = nRotateBufSize

    camera.IMV_RotateImage(stRotateImageParam)
    camera.IMV_ReleaseFrame(frame)

    user_buff = (c_ubyte * stRotateImageParam.nDstBufSize)()
    cdll.msvcrt.memcpy(byref(user_buff), stRotateImageParam.pDstBuf, stRotateImageParam.nDstBufSize)

    return user_buff

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






















