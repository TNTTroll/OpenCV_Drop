import numpy as np
import cv2


# PROGRAM
screen = None
manager = None

# CAMERA
cameraSizeInternal = [1920, 1080] 		# Real camera Internal
cameraSizeExternal = [1920, 1200] 		    # Real camera External

coefficient = .5 			# Coefficient for resizing

WIDTH = int(cameraSizeInternal[0] * coefficient)
HEIGHT = int(cameraSizeInternal[1] * coefficient)

WINDOW_CAM = "Camera" 		# Name for Camera window
FPS = 160

isExternal = None 			# Check if isExternal camera is ON
cameraMode = 2              # Camera mode [None, External, Internal]
cameraModeText = ["None", "Internal", "External"]

isFlip = False        # Flip the frame horizontally

isGoing = True              # Pause the video

frameCount = 0
threadCount = 0

isFPS = False
FPSCount = 0
FPSStart = FPSEnd = 0

# WINDOWS
winSettings = np.zeros((100, 300, 3), np.uint8)
winSettings[:, :, :] = 240

texts = []
textTimeShow = 20

BG = None

# MODES
currentMode = lastMode = 0  # Current and previous modes

modes = ["DEFAULT", "SETTINGS", "CHESS", "DIFFERENT", "MOVEMENT", "PLAY", "WINDOW", "POST"]  # Modes for camera

isReady = True 			    # Show "mode" naming

realSize = 2.16 * 6 			    # Real size for checkerboard

sliders = []                # Sliders for 'Settings' mode
buttons = ["Cam Mode",          # Buttons
           "Record", "Stop",    # Recording frames
           "Median",            # Save median
           "Save images",       # Enable saving images during recording
           "Previous", "Save"]  # Set/Save calibration

lastFrameMode = 0
lastFrames = []
lastFrameName = "Last Frames"

windowBuffer = []

# RECORD
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
folder = "folder/"
fileType = ".avi"
path = "_" + fileType
lastPath = path
timeFormat = "%d.%m.%y_%H-%M-%S"
out = None

timeGap = 1.3

isRecording = False         # Check for a recording state

cayotTime = staticFrames = 10
objectMoveReset = 1
isCayotPause = False

currentFrame = moveFrame = 0
arrLength = 50
staticArray = np.ndarray(shape=arrLength, dtype=np.ndarray)  # For static on the scene
moveArray = np.ndarray(shape=(arrLength, 2), dtype=np.ndarray)  # For movements on the scene
staticArray.fill(0)
moveArray.fill(0)

writeStaticToMove = ""
writeStart = 0

# COLORS
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
GREEN = (121, 147, 81)
RED = (238, 78, 78)

# SLIDERS
slidersSettingsNames = ["B1", "G1", "R1",  # Names for sliders in 'Settings' mode
                        "B2", "G2", "R2",
                        "H1", "H2",
                        "W1", "W2",
                        "Sq"]
slidersCheckboardMode = ["NCol", "NRow"]
slidersMovementMode = ["Min", "Max"]
slidersWindowMode = ["Ero", "Dil", "Opn", "Cls"]

sets = [0, 0, 0, 255, 255, 255, 0, 0, 0, 0, WIDTH*HEIGHT//2]
maxs = [255, 255, 255, 255, 255, 255,
        1000, 1000, 1000, 1000,
        WIDTH*HEIGHT]

# CHESS
chessField = [4, 5]
chessPhoto = None

cellPX = pxSizeFrame = 0

# DIFFERENT
medianLength = 50
medianFrames = [x for x in range(medianLength)]

medianName = "Median_BG.jpg"

# MOVEMENT
timeStart = timeFramesCount = 0
isRecDynamic = False
dynamicLength = 20
dynamicFrames = []

# WINDOW
windowMax = 1

# POST

# LOGGING
logFolder = "data/"
logImagesName = "/images/"
logMainName = "_main.csv"
logParamsName = "/params.csv"
logFrameName = "_test.yaml"
logDetailedFrameName = "_detailed.yaml"
logChessName = "/chess.png"
logBGName = "/bg.png"
logFrameImageName = "_frame.png"
logMaskImageName = "_mask.png"

inactiveDrops = 0
mainDrops = []
logMain = None
logFrame = None

isImageSave = True

# CALIBRATION
calibrationFolder = "_calibration/"
calibrationText = "Calibration settings"

calibreId = -1
