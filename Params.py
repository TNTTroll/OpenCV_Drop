import numpy as np


# CAMERA
cameraWidth = 1920 			# Real camera width
cameraHeight = 1080 		# Real camera height

coefficient = .5 			# Coefficient for resizing

WIDTH = int(cameraWidth * coefficient)
HEIGHT = int(cameraHeight * coefficient)

WINDOW_CAM = "Camera" 		# Name for Camera window
FPS = 30

isExternal = None 			# Check if isExternal camera is ON
cameraMode = 0              # Camera mode [Internal, External]

checkForFlip = False        # Flip the frame horizontally

# WINDOWS
serialNumber = '22193655'   # Camera from SkolTech

statOffsetX = WIDTH*.7		# X Offset for text in Stat window
statOffsetY = 50 			# Y Offset for text in Stat window

winSettings = np.zeros((100, 300, 3), np.uint8)
winSettings[:, :, :] = 240

# MODES
currentMode = lastMode = 0  # Current and previous modes

modes = ["DEFAULT", "SETTINGS", "CHECKBOARD", "DETECTING"] # Modes for camera

isTextShown = True 			# Show "mode" naming

realSize = 29.8 			# Real size for checkerboard

# COLORS
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)


sets = [0, 0, 0, 255, 255, 255, 0, 0, 0, 0]
checkField = [4, 5]


cellPX = pxSizeframe = 0