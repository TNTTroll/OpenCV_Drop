import numpy as np
import cv2

# PROGRAM
screen = None
manager = None

# CAMERA
cameraSizeInternal = [1920, 1080] 		# Real camera Internal
cameraSizeExternal = [1920, 1200] 		# Real camera External

coefficient = .5 			# Coefficient for resizing

WIDTH = int(cameraSizeInternal[0] * coefficient)
HEIGHT = int(cameraSizeInternal[1] * coefficient)

WINDOW_CAM = "Camera" 		# Name for Camera window
FPS = 24

isExternal = None 			# Check if isExternal camera is ON
cameraMode = 0              # Camera mode [None, Internal, External]
cameraModeText = ["None", "Internal", "External"]

isFlip = False        # Flip the frame horizontally

isGoing = True              # Pause the video

# WINDOWS
serialNumber = '22193655'   # Camera from SkolTech

winSettings = np.zeros((100, 300, 3), np.uint8)
winSettings[:, :, :] = 240

# MODES
currentMode = lastMode = 0  # Current and previous modes

modes = ["DEFAULT", "SETTINGS", "CHESS", "DIFFERENT", "MOVEMENT", "PLAY", "WINDOW"] # Modes for camera

isTextShown = True 			# Show "mode" naming

realSize = 29.8 			# Real size for checkerboard

sliders = []                # Sliders for 'Settings' mode
buttons = ["Cam Mode",      # Buttons
           "Record", "Stop",
           "Median"]

lastFrameMode = 0
lastFrames = []
lastFrameName = "Last Frames"

windowBuffer = []

# RECORD
fourcc = cv2.VideoWriter_fourcc(*'XVID')
folder = "folder/"
path = "_.avi"
timeFormat = "%d.%m.%y_%H-%M-%S"
out = None

timeGap = 1.3

isRecording = False         # Check for a recording state

# COLORS
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)

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
checkField = [4, 5]

cellPX = pxSizeframe = 0

# DIFFERENT
medianLength = 50
medianFrames = [x for x in range(medianLength)]

medianName = "Median_BG.jpg"

# MOVEMENT
timeStart = timeFramesCount = 0
isRecDynamic = False
dynamicLength = 3
dynamicFrames = []

# WINDOW
windowOut = None
currentFrame = moveFrame = 0
windowStaticArray = [0 for x in range(50)]   # For static frames
windowMoveArray = [0 for x in range(50)]  # For movements on the scene
windowMax = windowReset = 0