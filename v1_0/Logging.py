# --- Imports
import csv
import time
import cv2
import yaml
from os import listdir, mkdir, path

import Params as P
import Additional as A


# --- Defs
# <<< Video
def writeFrame(out, frame):
    try:
        if frame == 0: pass
    except(ValueError):
        out.write(frame)

def saveFrames(out, way):
    if out is None: return out

    if P.objectMoveReset == 0:
        mainLog(P.moveFrame, 0)
        P.lastFrames = P.windowBuffer

        P.objectMoveReset = 1

    P.writeStart = finish = 0
    if len(P.writeStaticToMove.split("&")) > 0:
        for pair in P.writeStaticToMove.split("&"):
            border = pair.split("|")

            if border[0] == "": break  # If there is no cuttings
            if pair.count("|") == 0: break  # If there is an overflow, no start position
            if border[1] == "":  # If there is an overflow, no finish position
                border[1] = 50 if way != "EXIT" else P.moveFrame

            for i in range(P.writeStart, int(border[0])):  # Saving static frames
                writeFrame(out, P.staticArray[i])
            for i in range(finish, int(border[1])):  # Saving dynamic frames
                writeFrame(out, P.moveArray[i][0])
            P.writeStart = int(border[0])
            finish = int(border[1])

    for i in range(P.cayotTime):
        if P.writeStart + i < 50:
            writeFrame(out, P.staticArray[P.writeStart + i])
        else: break

    if P.isImageSave:
        for i in range(finish):
            cv2.imwrite(P.logFolder + str(P.threadCount).zfill(4) + P.logImagesName
                        + str(i+1).zfill(4) + P.logFrameImageName,
                        P.moveArray[i][0])
            cv2.imwrite(P.logFolder + str(P.threadCount).zfill(4) + P.logImagesName
                        + str(i + 1).zfill(4) + P.logMaskImageName,
                        P.moveArray[i][1])

    out.release()
    if way != "EXIT": A.createFolder()

    P.writeStaticToMove = ""
    P.currentFrame = 0
    P.moveFrame = 0

    return out

# <<< Text
def frameLog(drops, folderPath):  # Logging every frame

    P.frameCount += 1
    with open(folderPath + P.logDetailedFrameName, "a+") as file:  # _detailed.yaml
        data = {
            "Droplets count": len(drops),
            "Frame number": P.frameCount,
            "Info": {}
        }

        for i in range(len(drops)):
            drop = {
                "Area in PX": int(drops[i].areaPX[0]),
                "Area in MM": int(drops[i].areaMM[0]),
                "Left offset": int(drops[i].left[0]),
                "Top offset": int(drops[i].top[0])
            }

            data["Info"]["drop_" + str(i+1).zfill(4)] = drop

        yaml.dump(data, file)

def mainLog(length, move):  # Main file with all logging
    P.frameCount = 0

    drops = ""
    for x in range(1, len(P.mainDrops)):
        drops = drops + str(P.mainDrops[x].getAreaMM()) + "|" + str( round(P.mainDrops[x].getSpeed(), 2) ) + ", "
    drops = drops[:-2]

    if len([f for f in listdir(P.logFolder) if f.count("_main")]) == 0:
        with open(P.logFolder + P.logMainName, 'w+', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["THREAD ID_DROP AMOUNT_FIRST DROP AREA_ALL DROPS AREAS_FRAME COUNT_CALIBRE ID_IsImageSave"])
            if len(P.mainDrops) > 0:
                writer.writerow([str(P.threadCount-1-move).zfill(4)] + [len(P.mainDrops)] + [P.mainDrops[0].getAreaMM()]
                                + [drops] + [length] + [P.calibreId] + [P.isImageSave])
    else:
        with open(P.logFolder + P.logMainName, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if len(P.mainDrops) > 0:
                writer.writerow([str(P.threadCount-1-move).zfill(4)] + [len(P.mainDrops)] + [P.mainDrops[0].getAreaMM()]
                                + [drops] + [length] + [P.calibreId] + [P.isImageSave])

    P.queueDrops = []
    P.inactiveDrops = 0

# <<< Calibration
def calibrationCreateFirst():
    filesInFolder = [f for f in listdir(P.logFolder) if f == P.calibrationFolder[:-1]]
    if len(filesInFolder) == 0:
        mkdir(P.logFolder + P.calibrationFolder)
def calibrationSetPrevious():
    listOfCalibrations = [f for f in listdir(P.logFolder + P.calibrationFolder) if not f.count(".")]
    if len(listOfCalibrations) > 0:
        prevCalFolder = P.logFolder + P.calibrationFolder + listOfCalibrations[-1]
        # Params
        with open(prevCalFolder + P.logParamsName, "r", newline="") as file:
            reader = csv.reader(file)
            firstRow = True
            for row in reader:
                if firstRow:
                    firstRow = False
                    break

                P.chessField[0] = row[0]
                P.chessField[1] = row[1]
                P.pxSizeFrame = row[2]

        # Chess
        pngExistence = [f for f in listdir(prevCalFolder) if f.endswith(".png")]
        if P.logChessName[1:] in pngExistence:
            P.chessPhoto = cv2.imread(prevCalFolder + P.logChessName)
            A.addText("Get a CHESS", (P.WIDTH*.78, P.HEIGHT*.05), size=25)
        else:
            A.addText("NO CHESS", (P.WIDTH*.75, P.HEIGHT*.05), size=25)

        # BG
        if P.logBGName[1:] in pngExistence:
            P.BG = cv2.imread(prevCalFolder + P.logBGName)
            A.addText("Get a BG", (P.WIDTH*.78, P.HEIGHT*.08), size=25)
        else:
            A.addText("NO BG", (P.WIDTH*.75, P.HEIGHT*.08), size=25)

    else:
        A.addText("No previous folder", (P.WIDTH * .75, 30), size=25)
def calibrationSaveNew():
    listOfCalibrations = [f for f in listdir(P.logFolder + P.calibrationFolder) if not f.count(".")]
    folderName = P.logFolder + P.calibrationFolder + "c"
    prevCalFolder = P.logFolder + P.calibrationFolder + listOfCalibrations[-1]
    P.calibreId = len(listOfCalibrations)+1
    folderName += str(str(P.calibreId).zfill(3))

    mkdir(folderName)
    # Params
    with open(folderName + P.logParamsName, "w+", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["CHESS WIDTH_CHESS HEIGHT_PIXEL SIZE"])
        writer.writerow([P.chessField[0], P.chessField[1], P.pxSizeFrame])

    # Chess
    pngExistence = [f for f in listdir(prevCalFolder) if f.endswith(".png")]
    try:
        if P.chessPhoto == None:
            if P.logChessName[1:] in pngExistence:
                P.chessPhoto = cv2.imread(prevCalFolder + P.logChessName)
                cv2.imwrite(folderName + P.logChessName, P.chessPhoto)
                A.addText("Prev CHESS", (P.WIDTH * .78, P.HEIGHT * .05), size=25)
            else:
                A.addText("NO CHESS", (P.WIDTH * .75, P.HEIGHT * .05), size=25)
    except(ValueError):
        cv2.imwrite(folderName + P.logChessName, P.chessPhoto)

    # BG
    try:
        if P.BG == None:
            if P.logBGName[1:] in pngExistence:
                P.BG = cv2.imread(prevCalFolder + P.logBGName)
                cv2.imwrite(folderName + P.logBGName, P.BG)
                A.addText("Prev BG", (P.WIDTH * .78, P.HEIGHT * .08), size=25)
            else:
                A.addText("NO BG", (P.WIDTH * .75, P.HEIGHT * .08), size=25)
    except(ValueError):
        cv2.imwrite(folderName + P.logBGName, P.BG)

