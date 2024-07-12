# --- Imports
import cv2
import numpy as np
import gc
import pygame as pg
import pygame_gui
from os import listdir
from time import time
from shutil import rmtree

import Params as P
import Logging as L
import Additional as A
from v1_0.IMVApi_1 import *


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
    P.buttons[1] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH * .75, P.HEIGHT // 2 - 25), (150, 50)),
                                                text="Record", manager=P.manager, visible=False)

    P.buttons[2] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH * .75, P.HEIGHT // 2 - 25), (150, 50)),
                                                text="Stop", manager=P.manager, visible=False)

    # Set a median
    P.buttons[3] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH * .75, P.HEIGHT // 2 + 50), (150, 50)),
                                                text="Background", manager=P.manager, visible=False)

    # Enable an image saving mode
    P.buttons[4] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH * .75, P.HEIGHT // 2 + 125), (150, 50)),
                                                text="Save images", manager=P.manager, visible=False)

    # Calibration
    P.buttons[5] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH * .75, P.HEIGHT // 2 - 100), (75, 50)),
                                                text="Set", manager=P.manager, visible=False)

    P.buttons[6] = pygame_gui.elements.UIButton(relative_rect=pg.Rect((P.WIDTH * .825, P.HEIGHT // 2 - 100), (75, 50)),
                                                text="Save", manager=P.manager, visible=False)


def exit(camera, program):
    closeExternalCam(camera) if P.isExternal else closeInternalCam(camera)

    closeFiles()

    program.quit()
    cv2.destroyAllWindows()
    cv2.waitKey(10)

    print("\n\nProgram has been closed")

def closeFiles():
    L.saveFrames(P.out, "EXIT")
    if P.objectMoveReset == 0: L.mainLog(P.moveFrame, 0)

    try:
        if P.threadCount > 0:
            path = P.logFolder + str(P.threadCount).zfill(4)
            listOfFiles = [f for f in listdir(path + "/") if f.count(".yaml")]
            if len(listOfFiles) == 0: rmtree(path)
    except(FileNotFoundError):
        pass

def fps():
    P.FPSCount += 1
    P.FPSEnd = time()
    timeDiff = P.FPSEnd - P.FPSStart
    if P.FPSEnd - P.FPSStart > 10:
        P.isFPS = False
        A.addText(f"FPS: {round((P.FPSCount / timeDiff), 3)}", (P.WIDTH*.68, P.HEIGHT*.05), color=P.GREEN, size=20)

    A.putTextPy(f"FPS: {round(P.FPSCount / timeDiff, 3)}", (P.WIDTH * .68, P.HEIGHT * .05), size=20)
    A.putTextPy(f"{P.FPSCount}/{round(timeDiff, 3)}s", (P.WIDTH * .68, P.HEIGHT * .1), size=20)

# <<< Camera
def getCamBySerial():

    if P.cameraMode == 2:
        P.cameraMode = 1

        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        setCamSize(camera, "Internal")

        return None, camera, camera.get(3) * 1.75, camera.get(4)

    else:
        P.cameraMode = 2

        deviceList = IMV_DeviceList()
        interfaceType = IMV_EInterfaceType.interfaceTypeAll

        nRet = MvCamera.IMV_EnumDevices(deviceList, interfaceType)
        if IMV_OK != nRet:
            print("Device's connection failed! ErrorCode:", nRet)
            sys.exit()
        if deviceList.nDevNum == 0:
            print("No devices found!")
            sys.exit()

        camera = MvCamera()
        getAllInfoExternalCam(camera)

        setCamSize(camera, "External")

        #return 1, camera, 1500 * (P.coefficient + .2), 1200 * P.coefficient
        return 1, camera, 1200 * (P.coefficient + .25), 1920 * (P.coefficient - .17)

def setCamSize(camera, type):
    if type != "External":
        if P.isReady:
            camera.set( cv2.CAP_PROP_FRAME_WIDTH, int(P.cameraSizeInternal[0] * P.coefficient) )
            camera.set( cv2.CAP_PROP_FRAME_HEIGHT, int(P.cameraSizeInternal[1] * P.coefficient) )

        else:
            camera.set( cv2.CAP_PROP_FRAME_WIDTH, P.cameraSizeInternal[0] )
            camera.set( cv2.CAP_PROP_FRAME_HEIGHT, P.cameraSizeInternal[1] )

def getImageExternalCam(camera):
    frame = IMV_Frame()
    stPixelConvertParam = IMV_PixelConvertParam()

    nRet = camera.IMV_GetFrame(frame, 1000)

    if IMV_OK != nRet:
        print("getFrame fail! Timeout:[1000]ms")
        return None

    if None == byref(frame):
        print("pFrame is NULL!")
        return None

    if IMV_EPixelType.gvspPixelMono8 == frame.frameInfo.pixelFormat:
        nDstBufSize = frame.frameInfo.width * frame.frameInfo.height
    else:
        nDstBufSize = frame.frameInfo.width * frame.frameInfo.height * 3

    pDstBuf = (c_ubyte * nDstBufSize)()
    memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))

    stPixelConvertParam.nWidth = frame.frameInfo.width
    stPixelConvertParam.nHeight = frame.frameInfo.height
    stPixelConvertParam.ePixelFormat = frame.frameInfo.pixelFormat
    stPixelConvertParam.pSrcData = frame.pData
    stPixelConvertParam.nSrcDataLen = frame.frameInfo.size
    stPixelConvertParam.nPaddingX = frame.frameInfo.paddingX
    stPixelConvertParam.nPaddingY = frame.frameInfo.paddingY
    stPixelConvertParam.eBayerDemosaic = IMV_EBayerDemosaic.demosaicNearestNeighbor
    stPixelConvertParam.eDstPixelFormat = frame.frameInfo.pixelFormat
    stPixelConvertParam.pDstBuf = pDstBuf
    stPixelConvertParam.nDstBufSize = nDstBufSize

    nRet = camera.IMV_ReleaseFrame(frame)
    if IMV_OK != nRet:
        print("Release frame failed! ErrorCode[%d]\n", nRet)
        sys.exit()

    if stPixelConvertParam.ePixelFormat == IMV_EPixelType.gvspPixelMono8:
        imageBuff = stPixelConvertParam.pSrcData
        userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)

        memmove(userBuff, imageBuff, stPixelConvertParam.nDstBufSize)
        grayByteArray = bytearray(userBuff)

        cvImage = np.array(grayByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth)

    else:
        stPixelConvertParam.eDstPixelFormat = IMV_EPixelType.gvspPixelBGR8

        nRet = camera.IMV_PixelConvert(stPixelConvertParam)
        if IMV_OK != nRet:
            print("Image convertation failed! ErrorCode[%d]" % nRet)
            del pDstBuf
            sys.exit()
        rgbBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        memmove(rgbBuff, stPixelConvertParam.pDstBuf, stPixelConvertParam.nDstBufSize)
        colorByteArray = bytearray(rgbBuff)
        cvImage = np.array(colorByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth, 3)
        if None != pDstBuf:
            del pDstBuf
            pass

    gc.collect()

    cvImage = cv2.resize(cvImage, ( int(cvImage.shape[1] * P.coefficient), int(cvImage.shape[0] * P.coefficient) ))
    return cvImage
def closeExternalCam(camera):
    nRet = camera.IMV_StopGrabbing()
    if IMV_OK != nRet:
        print("Stop grabbing failed! ErrorCode:", nRet)
        sys.exit()

    nRet = camera.IMV_Close()
    if IMV_OK != nRet:
        print("Camera closing failed! ErrorCode:", nRet)
        sys.exit()

    if camera.handle: nRet = camera.IMV_DestroyHandle()

def getImageInteranlCam(camera):
    ret, frame = camera.read()

    return frame if ret else None
def closeInternalCam(camera):
    camera.release()

def getAllInfoExternalCam(camera):
    nRet = camera.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    if IMV_OK != nRet:
        print("Camera creation failed! ErrorCode:", nRet)
        sys.exit()

    nRet = camera.IMV_Open()
    if IMV_OK != nRet:
        print("Camera opening failed! ErrorCode:", nRet)
        sys.exit()

    nRet = camera.IMV_SetEnumFeatureSymbol("TriggerSource", "Software")
    if IMV_OK != nRet:
        print("Trigger source set value failed! ErrorCode[%d]" % nRet)
        sys.exit()

    nRet = camera.IMV_SetEnumFeatureSymbol("TriggerSelector", "FrameStart")
    if IMV_OK != nRet:
        print("Trigger selector set value failed! ErrorCode[%d]" % nRet)
        sys.exit()

    nRet = camera.IMV_SetEnumFeatureSymbol("TriggerMode", "Off")
    if IMV_OK != nRet:
        print("Trigger mode set value failed! ErrorCode[%d]" % nRet)
        sys.exit()

    nRet = camera.IMV_StartGrabbing()
    if IMV_OK != nRet:
        print("Start grabbing failed! ErrorCode:", nRet)
        sys.exit()
