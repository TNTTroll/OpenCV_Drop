# --- Imports
import numpy
import cv2
import gc
from threading import Thread, Lock, Semaphore
from queue import Queue
from time import time
from copy import deepcopy

from v2_0.IMVApi_2 import *


# --- Variables
startTime = time()
countFrames = 0

FOURCC = cv2.VideoWriter_fourcc(*'FMP4')
FPS = 30.0
RESOLUTION = (1920, 1200)

colors = {"white": "1",
          "green": "1;32",
          "red": "1;31",
          "gray": "1;37",
          "blue": "1;34",
          "purple": "1;35"}

# <<< GRAB THREAD
saveImages1 = numpy.zeros((300, 1200, 1920), numpy.uint8)
saveImages2 = numpy.zeros((300, 1200, 1920), numpy.uint8)

isGoing = True
isFirstArr = isFilling = False
arrFill = 0

lock = Lock()
s = Semaphore(2)

# <<< TWO ARRAYS
staticPointer = 0
staticArr = numpy.zeros((100, 1200, 1920), numpy.uint8)
dynamicPointer = 0
dynamicArr = numpy.zeros((1000, 1200, 1920), numpy.uint8)

# <<< SAVE VIDEO WRITER
codecNames = ["DIVX", "XVID", "WMV1", "WMV2", "FMP4", "mp4v", "mpg1"]

# <<< QUEUE
q = Queue(maxsize=500)
going = True
inProgress = True


# --- Class
class FPS:
    def __init__(self, _name, _color=colors['white']):
        self.startTime = time()
        self.frameCount = 0
        self.name = _name
        self.color = f"\033[{_color}m"

    def get(self):
        self.frameCount += 1
        deltaT = time() - self.startTime
        f = self.frameCount / deltaT

        print(f"{self.color}--- {self.name} ---\nTime {round(deltaT, 2)}, Frames {self.frameCount}\nFPS {round(f, 2)}\n\033[0m")
# --- Main
def queueThreadCopy():
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

        return userBuff

    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    cam = MvCamera()

    cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    cam.IMV_Open()
    cam.IMV_StartGrabbing()

    fps1 = FPS("SAVE", colors['purple'])
    fps2 = FPS("SHOW", colors['gray'])

    def recording(s: Semaphore):
        global going, q
        while going:
            frame = frameGrabbingProc(cam)
            with s: q.put(frame)

            fps1.get()

    def showing(s: Semaphore, lock: Lock):
        global going, q
        while going:
            with s: byte = deepcopy(q.get())

            frame = numpy.array(bytearray(byte)).reshape(1200, 1920)

            fps2.get()

            cv2.imshow("QUEUE THREAD", frame)
            if cv2.waitKey(1) == ord('q'):
                with lock: going = False

    t1 = Thread(target=recording, args=(s,), daemon=True)
    t2 = Thread(target=showing, args=(s, lock))

    t1.start()
    t2.start()

    t2.join()

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")


queueThreadCopy()


'''
Links:
CODECS: https://ru.wikipedia.org/wiki/Windows_Media_Video
'''