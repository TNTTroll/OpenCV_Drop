import numpy as np


# CAMERA
cameraWidth = 1920 			# Real camera width
cameraHeight = 1200 		# Real camera height

coefficient = .5 			# Coefficient for resizing

WIDTH = int(cameraWidth * coefficient)
HEIGHT = int(cameraHeight * coefficient)

WINDOW_CAM = "Camera" 		# Name for Camera window
WINDOW_PARAMS = "Parametrs" # Name for Stat window
WINDOW_SET = "Settings"     # Name for Settings window

isExternal = None 			# Check if isExternal camera is ON

# WINDOWS
serialNumber = '22193655'   # Camera from SkolTech

statOffsetX = 30 			# X Offset for text in Stat window
statOffsetY = 50 			# Y Offset for text in Stat window

winSettings = np.zeros((100, 300, 3), np.uint8)
winSettings[:, :, :] = 240

# MODES
modes = ["DEFAULT", "SETTINGS", "CHECKBOARD", "DETECTING"] # Modes for camera

isTextShown = True 			# Show "mode" naming

realSize = 29.8 			# Real size for checkboard

# COLORS
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)



par00 = par01 = par02 = 0
par03 = par04 = par05 = 255

par06 = par07 = par08 = par09 = 0


cellPX = pxSizeframe = 0