# <<< GRAB
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

    fps = FPS("OPENCV")
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

        fps.get()

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

    fps = FPS("GRAB REAL")
    while True:
        frame = frameGrabbingProc(cam)

        fps.get()

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

    fps = FPS("GRAB ARRAY")
    arrFill = 0
    saveImages = numpy.zeros((100, 1200, 1920), numpy.uint8)
    while True:
        frame = frameGrabbingProc(cam)

        saveImages[arrFill % saveImages.shape[0]] = frame
        arrFill += 1

        fps.get()

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

    fps = FPS("GRAB SAVE")
    out = cv2.VideoWriter("V2_0/save/out.avi", FOURCC, FPS, RESOLUTION)
    while True:
        frame = frameGrabbingProc(cam)

        fps.get()

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

    fps = FPS("GRAB ARR SAVE")
    arrFill = 0
    fileCounter = 0
    saveImages = numpy.zeros((100, 1200, 1920), numpy.uint8)
    out = cv2.VideoWriter(f"save/{str(fileCounter).zfill(4)}.avi",
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
            out = cv2.VideoWriter(f"save/{str(fileCounter).zfill(4)}.avi",
                                  FOURCC, FPS, RESOLUTION)

        fps.get()

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

    fps = FPS("TWO ARRAY")

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
                print(f"There are objects [{num_labels - 1}]")

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
                    outTwoArr = cv2.VideoWriter(f"V2_0/save/{str(fileCounter).zfill(4)}.avi", FOURCC, FPS, RESOLUTION)

                staticPointer = 0 if staticPointer == staticArr.shape[0] - 1 else staticPointer + 1
                staticArr[staticPointer] = frame
                isMove = False

        fps.get()

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

    fps = FPS("GRAB THREAD")

    def fillArray():
        global arrFill, saveImages1, saveImages2, isFirstArr, isFilling, isGoing

        while True:
            frame = frameGrabbingProc(cam)
            frame[::] = 0 if isFirstArr else 255

            fps.get()

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
                    print(f"END after {round((time() - startRec), 3)}")
                    isFilling = False
                    outThread.release()
                    fileCounter += 1
                    outThread = cv2.VideoWriter(f"V2_0/save/{str(fileCounter).zfill(4)}.avi", FOURCC, FPS, RESOLUTION)

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


# <<< NUMPY
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

    fps = FPS("NUMPY SLICE")

    for i in range(500):
        frameGrabbingProc(cam)

        fps.get()

    for i in range(500):
        grayByteArray = bytearray(saveSlices[i])
        frame = numpy.array(grayByteArray).reshape(1200, 1920)

        cv2.imshow("NUMPY SLICE", frame)
        cv2.waitKey(1)

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")


# <<< WRITER
def saveVideoWriter():
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

    fps = FPS("SAVE VIDEO WRITER")

    count = 0
    outVideoWriter = cv2.VideoWriter(f"V2_0/save/{codecNames[count]}.avi", cv2.VideoWriter_fourcc(*codecNames[count]),
                                     30.0, (1920, 1200))
    while True:
        frame = frameGrabbingProc(cam)

        global countFrames, startTime
        countFrames += 1

        fps.get()

        if countFrames == 100:
            outVideoWriter.release()
            count += 1
            if count == len(codecNames): break
            outVideoWriter = cv2.VideoWriter(f"V2_0/save/{codecNames[count]}.avi",
                                             cv2.VideoWriter_fourcc(*codecNames[count]), 30.0, (1920, 1200))

            deltaT = time() - startTime
            f = countFrames / deltaT
            print(
                f"\n----------\n{codecNames[count - 1]} recorded in {round(f, 2)}. {codecNames[count]} in progress\n----------\n")

            countFrames = 0
            startTime = time()

        outVideoWriter.write(cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR))

        cv2.imshow("SAVE VIDEO WRITER", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    deltaT = time() - startTime
    f = countFrames / deltaT
    print(f"\n----------\n{codecNames[count - 1]} recorded in {round(f, 2)}.\n----------\n")
    outVideoWriter.release()

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")


def saveImWrite():
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

    fps = FPS("SAVE IMWRITE")

    count = 0
    while True:
        frame = frameGrabbingProc(cam)

        fps.get()

        cv2.imwrite(f"V2_0/imwrite/{str(count).zfill(4)}.jpg", frame)
        count += 1

        cv2.imshow("SAVE VIDEO WRITER", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")


# <<< QUEUE
def queueShow():
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

        q.put(userBuff)

    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    cam = MvCamera()

    cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    cam.IMV_Open()
    cam.IMV_StartGrabbing()

    fps1 = FPS("SAVE")
    fps2 = FPS("SHOW")

    count = 0
    while count < 750:
        frameGrabbingProc(cam)
        count += 1

        fps1.get()

    print("\n\nSHOWING\n\n")
    global countFrames, startTime
    countFrames = 0
    startTime = time()
    for i in range(q.qsize()):
        frame = numpy.array(bytearray(q.get())).reshape(1200, 1920)

        fps2.get()

        cv2.imshow("QUEUE SHOW", frame)
        cv2.waitKey(1)

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")


def queueSave():
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

        q.put(userBuff)

    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    cam = MvCamera()

    cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    cam.IMV_Open()
    cam.IMV_StartGrabbing()

    fps1 = FPS("SAVE")
    fps2 = FPS("SHOW")

    count = 0
    while count < 750:
        frameGrabbingProc(cam)
        count += 1

        fps1.get()

    global countFrames, startTime
    countFrames = 0
    startTime = time()
    queueOut = cv2.VideoWriter(f"V2_0/queue.avi", FOURCC, FPS, RESOLUTION)
    for i in range(q.qsize()):
        frame = numpy.array(bytearray(q.get())).reshape(1200, 1920)
        queueOut.write(cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR))

        fps2.get()

        cv2.imshow("QUEUE SAVE", frame)
        cv2.waitKey(1)

    queueOut.release()
    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")


def queueAttempt():
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

        q.put(userBuff)

    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    cam = MvCamera()

    cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    cam.IMV_Open()
    cam.IMV_StartGrabbing()

    for attempt in range(20):
        startTime = time()
        count = 0
        while count < 750:
            frameGrabbingProc(cam)
            count += 1

            if count == 720:
                deltaT = time() - startTime
                print(
                    f"\nATTEMPT #{attempt}\n------ RECORD ------\nTime {round(deltaT, 2)}, Frames {count}\nFPS {round(count / deltaT, 2)}")

        for i in range(q.qsize()):
            frame = numpy.array(bytearray(q.get())).reshape(1200, 1920)

            cv2.imshow("QUEUE ATTEMPT", frame)
            cv2.waitKey(1)

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")


def queueSaveAfter():
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

        q.put(userBuff)

    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll

    MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    cam = MvCamera()

    cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    cam.IMV_Open()
    cam.IMV_StartGrabbing()

    fps = FPS("SAVE")

    count = 0
    out = cv2.VideoWriter(f"V2_0/save/{str(count).zfill(4)}.avi", FOURCC, FPS, RESOLUTION)
    while True:
        frameGrabbingProc(cam)

        fps.get()

        if q.qsize() == 750:
            start = time()
            for i in range(q.qsize()):
                frame = numpy.array(bytearray(q.get())).reshape(1200, 1920)

                out.write(cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR))

                cv2.imshow("QUEUE SAVE AFTER", frame)
                if cv2.waitKey(1) == ord('q'):
                    break

            out.release()
            count += 1
            out = cv2.VideoWriter(f"V2_0/save/{str(count).zfill(4)}.avi", FOURCC, FPS, RESOLUTION)

            print(f"Took: {round((time() - start), 2)}s")

    out.release()

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")


def queueThread():
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

    fps1 = FPS("SAVE")
    fps2 = FPS("SHOW")

    def recording(s: Semaphore):
        global going, q
        while going:
            frame = frameGrabbingProc(cam)
            with s: q.put(frame)

            fps1.get()

    def showing(s: Semaphore, lock: Lock):
        global going, q
        while going:
            with s:
                frame = numpy.array(bytearray(q.get())).reshape(1200, 1920)

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


def queueThreadSave():
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

    fps1 = FPS("SAVE")
    fps2 = FPS("SHOW")

    def recording(s: Semaphore):
        global going, q
        while going:
            frame = frameGrabbingProc(cam)
            with s: q.put(frame)

            fps1.get()

    def showing(s: Semaphore, lock: Lock):
        global going, q
        while going:
            with s:
                frame = numpy.array(bytearray(q.get())).reshape(1200, 1920)

            fps2.get()

            queueOut.write(cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR))

            cv2.imshow("QUEUE THREAD SAVE", frame)
            if cv2.waitKey(1) == ord('q'):
                with lock: going = False

    queueOut = cv2.VideoWriter(f"V2_0/queue.avi", FOURCC, FPS, RESOLUTION)
    t1 = Thread(target=recording, args=(s,), daemon=True)
    t2 = Thread(target=showing, args=(s, lock))

    t1.start()
    t2.start()

    t2.join()

    queueOut.release()

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")


# <<< NUMPY + QUEUE
def queueNumpy():
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

    fps1 = FPS("SAVE")
    fps2 = FPS("NUMPY")
    fps3 = FPS("SHOW")

    def recording(s: Semaphore, limit):
        global q
        for i in range(limit):
            frame = frameGrabbingProc(cam)
            with s: q.put(frame)

            fps1.get()

    def numpying(s: Semaphore, limit):
        global q
        for i in range(limit):
            with s: byte = bytearray(q.get())
            arr[countFrames] = byte

            fps2.get()

    def showing(limit):
        for i in range(limit):
            frame = arr[i].reshape(1920, 1200)

            fps3.get()

            cv2.imshow("QUEUE NUMPY", frame)
            cv2.waitKey(1)

    limit = 500
    arr = numpy.zeros((limit, 2304000))
    t1 = Thread(target=recording, args=(s, limit,), daemon=True)
    t2 = Thread(target=numpying, args=(s, limit,))

    t1.start()
    t2.start()

    t2.join()
    showing(limit)

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")


def queueTripleNumpy():
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

    fps1 = FPS("SAVE")
    fps2 = FPS("NUMPY")
    fps3 = FPS("SHOW")

    def recording(s: Semaphore, limit):
        global going, q, inProgress
        while going:
            if inProgress:
                for i in range(limit):
                    frame = frameGrabbingProc(cam)
                    with s: q.put(frame)

            fps1.get()

    def numpying(s: Semaphore, limit):
        global going, q, inProgress
        while going:
            if inProgress:
                for i in range(limit):
                    with s: byte = q.get()
                    byte = bytearray(byte)
                    arr[i] = byte

                    fps2.get()

                with lock:
                    inProgress = False

    def showing(limit):
        global going, inProgress
        while going:
            if not inProgress:
                for i in range(limit):
                    frame = arr[i].reshape(1920, 1200)

                    fps3.get()

                    cv2.imshow("QUEUE TRIPLE NUMPY", frame)
                    if cv2.waitKey(1) == ord('q'):
                        with lock: going = False
                        break
                with lock:
                    inProgress = True

    limit = 500
    arr = numpy.zeros((limit, 2304000), dtype=uint8_t)
    t1 = Thread(target=recording, args=(s, limit,), daemon=True)
    t2 = Thread(target=numpying, args=(s, limit,), daemon=True)
    t3 = Thread(target=showing, args=(limit,))

    t1.start()
    t2.start()
    t3.start()

    t3.join()

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")


def queueNowait():
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

    fps1 = FPS("SAVE")
    fps2 = FPS("SHOW")

    def recording():
        global going, q
        while going:
            q.put(frameGrabbingProc(cam))
            fps1.get()

    def showing(lock: Lock):
        global going, q
        while going:
            frame = numpy.array(bytearray(q.get())).reshape(1920, 1200)

            fps2.get()

            cv2.imshow("QUEUE NOWAIT", frame)
            if cv2.waitKey(1) == ord('q'):
                with lock: going = False

    t1 = Thread(target=recording, daemon=True)
    t2 = Thread(target=showing)

    t1.start()
    t2.start()

    t2.join()

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")


def queueSize():
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

    fps1 = FPS("SAVE")
    fps2 = FPS("SHOW")

    def recording(s: Semaphore, q1: Queue, q2: Queue, switch):
        global going
        while going:
            if switch:
                with s:
                    q1.put(frameGrabbingProc(cam))
            else:
                with s:
                    q2.put(frameGrabbingProc(cam))

            fps1.get()

    def showing(s: Semaphore, lock: Lock, q1: Queue, q2: Queue, switch):
        global going
        while going:
            if switch:
                while q1.qsize() > 0:
                    with s: byte = q1.get()
                    print(f"1: {q1.qsize()}")
            else:
                while q2.qsize() > 0:
                    with s: byte = q2.get()
                    print(f"2 {q2.qsize()}")

            switch = not switch
            print(byte)
            frame = numpy.array(bytearray(byte)).reshape(1920, 1200)

            fps2.get()

            cv2.imshow("QUEUE SIZE", frame)
            if cv2.waitKey(1) == ord('q'):
                with lock: going = False

    q1 = Queue(maxsize=200)
    q2 = Queue(maxsize=200)
    switch = True

    t1 = Thread(target=recording, args=(s, q1, q2, switch), daemon=True)
    t2 = Thread(target=showing, args=(s, lock, q1, q2, switch))

    t1.start()
    t2.start()

    t2.join()

    cam.IMV_StopGrabbing()
    cam.IMV_Close()
    if cam.handle: cam.IMV_DestroyHandle()

    print("CLOSED")