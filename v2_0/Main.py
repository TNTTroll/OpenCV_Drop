# --- Imports
import numpy
import cv2
import gc
from threading import Thread, Lock
from time import time

from v2_0.IMVApi_2 import *


# --- Variables
startTime = time()
countFrames = 0

FOURCC = cv2.VideoWriter_fourcc(*'MJPG')
FPS = 30.0
RESOLUTION = (1920, 1200)


# <<< GRAB THREAD
saveImages1 = numpy.zeros((300, 1200, 1920), numpy.uint8)
saveImages2 = numpy.zeros((300, 1200, 1920), numpy.uint8)

fileCounter = 0
outThread = cv2.VideoWriter(f"V2_0/grabThread/{str(fileCounter).zfill(4)}.avi", FOURCC, FPS, RESOLUTION)

isGoing = True
isFirstArr = isFilling = False
arrFill = 0

lock = Lock()

# <<< TWO ARRAYS
staticPointer = 0
staticArr = numpy.zeros((100, 1200, 1920), numpy.uint8)
dynamicPointer = 0
dynamicArr = numpy.zeros((1000, 1200, 1920), numpy.uint8)

outTwoArr = cv2.VideoWriter(f"V2_0/twoArr/{str(fileCounter).zfill(4)}.avi", FOURCC, FPS, RESOLUTION)

# <<< NUMPY SLICE
#saveSlices = numpy.zeros((1000, ctypes.c_char_p * 2304000), numpy.uint8)


# --- Defs
def fps():
    global countFrames
    countFrames += 1
    deltaT = time() - startTime
    f = countFrames / deltaT

    print(f"Time {round(deltaT, 2)}, Frames {countFrames}\nFPS {round(f, 2)}\n")


# --- Main
def openCV():
    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    cam = MvCamera()

    cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    cam.IMV_Open()
    cam.IMV_SetEnumFeatureSymbol("TriggerSource", "Software")
    cam.IMV_SetEnumFeatureSymbol("TriggerSelector", "FrameStart")
    cam.IMV_SetEnumFeatureSymbol("TriggerMode", "Off")
    cam.IMV_StartGrabbing()

    while True:
        frame = IMV_Frame()
        stPixelConvertParam = IMV_PixelConvertParam()

        cam.IMV_GetFrame(frame, 1000)

        if None == byref(frame): continue

        memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))

        stPixelConvertParam.nWidth = frame.frameInfo.width
        stPixelConvertParam.nHeight = frame.frameInfo.height
        stPixelConvertParam.pSrcData = frame.pData
        stPixelConvertParam.nDstBufSize = frame.frameInfo.width * frame.frameInfo.height

        cam.IMV_ReleaseFrame(frame)

        imageBuff = stPixelConvertParam.pSrcData
        userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        memmove(userBuff, imageBuff, stPixelConvertParam.nDstBufSize)
        grayByteArray = bytearray(userBuff)

        cvImage = numpy.array(grayByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth)

        fps()

        cv2.imshow('OPENCV', cvImage)
        gc.collect()

        if cv2.waitKey(1) == ord('q'):
            break

    cam.IMV_StopGrabbing()
    cam.IMV_Close()

    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")

def grabReal():
    def frameGrabbingProc(cam):
        frame = IMV_Frame()

        stPixelConvertParam = IMV_PixelConvertParam()
        cam.IMV_GetFrame(frame, 1000)

        nDstBufSize = frame.frameInfo.width * frame.frameInfo.height
        pDstBuf = (c_ubyte * nDstBufSize)()
        memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))

        stPixelConvertParam.nWidth = frame.frameInfo.width
        stPixelConvertParam.nHeight = frame.frameInfo.height
        stPixelConvertParam.nDstBufSize = nDstBufSize
        stPixelConvertParam.pDstBuf = pDstBuf
        stPixelConvertParam.pSrcData = frame.pData

        cam.IMV_ReleaseFrame(frame)

        imageBuff = stPixelConvertParam.pSrcData
        userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        memmove(userBuff, imageBuff, stPixelConvertParam.nDstBufSize)
        grayByteArray = bytearray(userBuff)

        cvImage = numpy.array(grayByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth)

        return cvImage

    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    cam = MvCamera()

    cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    cam.IMV_Open()
    cam.IMV_StartGrabbing()

    while True:
        frame = frameGrabbingProc(cam)

        fps()

        cv2.imshow("GRAB REAL", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")

def grabArray():
    def frameGrabbingProc(cam):
        frame = IMV_Frame()

        stPixelConvertParam = IMV_PixelConvertParam()
        cam.IMV_GetFrame(frame, 1000)

        nDstBufSize = frame.frameInfo.width * frame.frameInfo.height
        pDstBuf = (c_ubyte * nDstBufSize)()
        memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))

        stPixelConvertParam.nWidth = frame.frameInfo.width
        stPixelConvertParam.nHeight = frame.frameInfo.height
        stPixelConvertParam.nDstBufSize = nDstBufSize
        stPixelConvertParam.pDstBuf = pDstBuf
        stPixelConvertParam.pSrcData = frame.pData

        cam.IMV_ReleaseFrame(frame)

        imageBuff = stPixelConvertParam.pSrcData
        userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        memmove(userBuff, imageBuff, stPixelConvertParam.nDstBufSize)
        grayByteArray = bytearray(userBuff)

        cvImage = numpy.array(grayByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth)

        return cvImage

    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    cam = MvCamera()

    cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    cam.IMV_Open()
    cam.IMV_StartGrabbing()

    arrFill = 0
    saveImages = numpy.zeros((100, 1200, 1920), numpy.uint8)
    while True:
        frame = frameGrabbingProc(cam)

        saveImages[arrFill % saveImages.shape[0]] = frame
        arrFill += 1

        fps()

        cv2.imshow("GRAB ARRAY", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")

def grabSave():
    def frameGrabbingProc(cam):
        frame = IMV_Frame()

        stPixelConvertParam = IMV_PixelConvertParam()
        cam.IMV_GetFrame(frame, 1000)

        nDstBufSize = frame.frameInfo.width * frame.frameInfo.height
        pDstBuf = (c_ubyte * nDstBufSize)()
        memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))

        stPixelConvertParam.nWidth = frame.frameInfo.width
        stPixelConvertParam.nHeight = frame.frameInfo.height
        stPixelConvertParam.nDstBufSize = nDstBufSize
        stPixelConvertParam.pDstBuf = pDstBuf
        stPixelConvertParam.pSrcData = frame.pData

        cam.IMV_ReleaseFrame(frame)

        imageBuff = stPixelConvertParam.pSrcData
        userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        memmove(userBuff, imageBuff, stPixelConvertParam.nDstBufSize)
        grayByteArray = bytearray(userBuff)

        cvImage = numpy.array(grayByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth)

        return cvImage

    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    cam = MvCamera()

    cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    cam.IMV_Open()
    cam.IMV_StartGrabbing()

    out = cv2.VideoWriter("grabSave/out.avi", FOURCC, FPS, RESOLUTION)
    while True:
        frame = frameGrabbingProc(cam)

        fps()

        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        out.write(frame)

        cv2.imshow("GRAB SAVE", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    out.release()

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")

def grabArrSave():
    def frameGrabbingProc(cam):
        frame = IMV_Frame()

        stPixelConvertParam = IMV_PixelConvertParam()
        cam.IMV_GetFrame(frame, 1000)

        nDstBufSize = frame.frameInfo.width * frame.frameInfo.height
        pDstBuf = (c_ubyte * nDstBufSize)()
        memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))

        stPixelConvertParam.nWidth = frame.frameInfo.width
        stPixelConvertParam.nHeight = frame.frameInfo.height
        stPixelConvertParam.nDstBufSize = nDstBufSize
        stPixelConvertParam.pDstBuf = pDstBuf
        stPixelConvertParam.pSrcData = frame.pData

        cam.IMV_ReleaseFrame(frame)

        imageBuff = stPixelConvertParam.pSrcData
        userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        memmove(userBuff, imageBuff, stPixelConvertParam.nDstBufSize)
        grayByteArray = bytearray(userBuff)

        cvImage = numpy.array(grayByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth)

        return cvImage

    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    cam = MvCamera()

    cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    cam.IMV_Open()
    cam.IMV_StartGrabbing()

    arrFill = 0
    fileCounter = 0
    saveImages = numpy.zeros((100, 1200, 1920), numpy.uint8)
    out = cv2.VideoWriter(f"grabArrSave/{str(fileCounter).zfill(4)}.avi",
                          FOURCC, FPS, RESOLUTION)
    while True:
        frame = frameGrabbingProc(cam)

        saveImages[arrFill % saveImages.shape[0]] = frame
        arrFill += 1

        if arrFill % saveImages.shape[0] == 0:
            print("--- SAVING ---")
            for i in range(saveImages.shape[0]):
                s = cv2.cvtColor(saveImages[i], cv2.COLOR_GRAY2BGR)
                out.write(s)

            fileCounter += 1
            out.release()
            out = cv2.VideoWriter(f"grabArrSave/{str(fileCounter).zfill(4)}.avi",
                                  FOURCC, FPS, RESOLUTION)

        fps()

        cv2.imshow("GRAB ARRAY SAVE", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    out.release()

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")

def twoArrays():
    def frameGrabbingProc(cam):
        frame = IMV_Frame()

        stPixelConvertParam = IMV_PixelConvertParam()
        cam.IMV_GetFrame(frame, 1000)

        nDstBufSize = frame.frameInfo.width * frame.frameInfo.height
        pDstBuf = (c_ubyte * nDstBufSize)()
        memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))

        stPixelConvertParam.nWidth = frame.frameInfo.width
        stPixelConvertParam.nHeight = frame.frameInfo.height
        stPixelConvertParam.nDstBufSize = nDstBufSize
        stPixelConvertParam.pDstBuf = pDstBuf
        stPixelConvertParam.pSrcData = frame.pData

        cam.IMV_ReleaseFrame(frame)

        imageBuff = stPixelConvertParam.pSrcData
        userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        memmove(userBuff, imageBuff, stPixelConvertParam.nDstBufSize)
        grayByteArray = bytearray(userBuff)

        cvImage = numpy.array(grayByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth)

        return cvImage

    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    cam = MvCamera()

    cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    cam.IMV_Open()
    cam.IMV_StartGrabbing()

    median = []
    isMove = False
    fileCounter = 0
    global staticArr, staticPointer, dynamicArr, dynamicPointer, outTwoArr
    while True:
        frame = frameGrabbingProc(cam)

        if len(median) != 0:
            frame = cv2.absdiff(frame, median)
            thresh = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY)[1]
            mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel=numpy.ones((4, 4)), iterations=4)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=numpy.ones((4, 4)), iterations=1)
            frame = cv2.bitwise_and(frame, frame, mask=mask)

            output = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
            num_labels = output[0]
            stats = output[2]

            for i in range(1, num_labels):
                t = stats[i, cv2.CC_STAT_TOP]
                l = stats[i, cv2.CC_STAT_LEFT]

                cv2.rectangle(frame, (l, t),
                             (stats[i, cv2.CC_STAT_WIDTH] + l, stats[i, cv2.CC_STAT_HEIGHT] + t),
                             (255, 0, 255), 1)

            if num_labels > 1:  # Movement
                print(f"There are objects [{num_labels-1}]")

                isMove = True
                dynamicArr[dynamicPointer] = frame
                dynamicPointer += 1

            else:  # Static
                if isMove:  # Last frame was with movement
                    print("--- SAVING ---")
                    for i in range(staticPointer, staticPointer + staticArr.shape[0]):
                        s = cv2.cvtColor(staticArr[i % staticArr.shape[0]], cv2.COLOR_GRAY2BGR)
                        outTwoArr.write(s)

                    for i in range(staticArr.shape[0], staticArr.shape[0] + dynamicPointer):
                        s = cv2.cvtColor(dynamicArr[i], cv2.COLOR_GRAY2BGR)
                        outTwoArr.write(s)

                    dynamicPointer = 0

                    outTwoArr.release()
                    fileCounter += 1
                    outTwoArr = cv2.VideoWriter(f"V2_0/twoArr/{str(fileCounter).zfill(4)}.avi", FOURCC, FPS, RESOLUTION)

                staticPointer = 0 if staticPointer == staticArr.shape[0] - 1 else staticPointer + 1
                staticArr[staticPointer] = frame
                isMove = False

        fps()


        cv2.imshow("GRAB ARRAY SAVE", frame)

        k = cv2.waitKey(1)
        if k == ord('q'):
            break
        elif k == 32:
            median = frame

    outTwoArr.release()

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")

def grabThread():
    def frameGrabbingProc(cam):
        frame = IMV_Frame()

        stPixelConvertParam = IMV_PixelConvertParam()
        cam.IMV_GetFrame(frame, 1000)

        nDstBufSize = frame.frameInfo.width * frame.frameInfo.height
        pDstBuf = (c_ubyte * nDstBufSize)()
        memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))

        stPixelConvertParam.nWidth = frame.frameInfo.width
        stPixelConvertParam.nHeight = frame.frameInfo.height
        stPixelConvertParam.nDstBufSize = nDstBufSize
        stPixelConvertParam.pDstBuf = pDstBuf
        stPixelConvertParam.pSrcData = frame.pData

        cam.IMV_ReleaseFrame(frame)

        imageBuff = stPixelConvertParam.pSrcData
        userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        memmove(userBuff, imageBuff, stPixelConvertParam.nDstBufSize)
        grayByteArray = bytearray(userBuff)

        cvImage = numpy.array(grayByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth)

        return cvImage

    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    cam = MvCamera()

    cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    cam.IMV_Open()
    cam.IMV_StartGrabbing()

    def fillArray():
        global arrFill, saveImages1, saveImages2, isFirstArr, isFilling, isGoing

        while True:
            frame = frameGrabbingProc(cam)
            frame[::] = 0 if isFirstArr else 255

            #fps()

            if isFirstArr:
                saveImages1[arrFill % saveImages1.shape[0]] = frame
            else:
                saveImages2[arrFill % saveImages2.shape[0]] = frame
            arrFill = 0 if arrFill == saveImages1.shape[0] - 1 else arrFill + 1

            if arrFill % saveImages1.shape[0] == 0:
                with lock:
                    isFilling = True
                    isFirstArr = not isFirstArr

            cv2.putText(frame, str(arrFill), (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.imshow("GRAB ARRAY SAVE", frame)
            if cv2.waitKey(1) == ord('q'):
                with lock: isGoing = False
                break

    def toFile():
        global isFilling, fileCounter, outThread, isFirstArr, isGoing

        while isGoing:

            if isFilling:
                print("START")
                startRec = time()
                if isFirstArr:
                    for i in range(0, saveImages1.shape[0], 4):
                        s = cv2.cvtColor(saveImages1[i], cv2.COLOR_GRAY2BGR)
                        with lock: outThread.write(s)
                else:
                    for i in range(0, saveImages2.shape[0], 4):
                        s = cv2.cvtColor(saveImages2[i], cv2.COLOR_GRAY2BGR)
                        with lock: outThread.write(s)

                with lock:
                    print(f"END after {round((time() - startRec),3)}")
                    isFilling = False
                    outThread.release()
                    fileCounter += 1
                    outThread = cv2.VideoWriter(f"V2_0/grabThread/{str(fileCounter).zfill(4)}.avi", FOURCC, FPS, RESOLUTION)


    t1 = Thread(target=fillArray)
    t2 = Thread(target=toFile)

    t1.start()
    t2.start()

    t1.join()
    t2.join()


    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")

def numpySlice():
    def frameGrabbingProc(cam):
        global currentSlice, saveSlices
        frame = IMV_Frame()

        stPixelConvertParam = IMV_PixelConvertParam()
        cam.IMV_GetFrame(frame, 1000)

        nDstBufSize = frame.frameInfo.width * frame.frameInfo.height
        pDstBuf = (c_ubyte * nDstBufSize)()
        memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))

        stPixelConvertParam.nWidth = frame.frameInfo.width
        stPixelConvertParam.nHeight = frame.frameInfo.height
        stPixelConvertParam.nDstBufSize = nDstBufSize
        stPixelConvertParam.pDstBuf = pDstBuf
        stPixelConvertParam.pSrcData = frame.pData

        cam.IMV_ReleaseFrame(frame)

        imageBuff = stPixelConvertParam.pSrcData
        userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        memmove(userBuff, imageBuff, stPixelConvertParam.nDstBufSize)

        print(saveSlices.shape)

    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    cam = MvCamera()

    cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    cam.IMV_Open()
    cam.IMV_StartGrabbing()

    for i in range(500):
        frameGrabbingProc(cam)

        fps()

    for i in range(500):
        grayByteArray = bytearray(saveSlices[i])
        frame = numpy.array(grayByteArray).reshape(1200, 1920)

        cv2.imshow("NUMPY SLICE", frame)
        cv2.waitKey(1)

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")


numpySlice()