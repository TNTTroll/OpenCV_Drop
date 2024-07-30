# --- Imports
from queue import Queue
import numpy as np


# --- Variables
# PROGRAM
screen = None
manager = None

WIDTH = 300
HEIGHT = 540

isUpdate = True

measureMode = 0
measurement = ["Area", "Diagonal"]

# CAMERA
cameraSize = [1920, 1200]        		# Camera size

coefficient = .5 			            # Coefficient for resizing

width = int(cameraSize[0] * coefficient)
height = int(cameraSize[1] * coefficient)

windowName = "DropCV" 		            # Name for Camera window
FPS = 160.0                             # FPS

# UI
orbs = []

buttons = ["Record",                    # Record new material from camera
           "Replay",                    # Watch all the videos from the folder
           "Measure",                   # Process all the video from the folder
           "Chessboard",                # Get a chess size
           "Background"]                # Gather new frames to BG

texts = []

# COLORS
colors = {"black": (0, 0, 0),

          "BG": (64, 93, 114),
          "orb": (117, 134, 148),
          "text": (247, 231, 220),
          }

fpsColor = {"white": "1",
            "green": "1;32",
            "red": "1;31",
            "gray": "1;37",
            "blue": "1;34",
            "purple": "1;35",

            "camera": "1;91",
            "info": "4",
            }

# QUEUE
queueLimit = 500
queue = Queue(maxsize=queueLimit)

matrix = np.zeros((queueLimit, cameraSize[1], cameraSize[0]), np.uint8)

queueFileCounter = 0

medianName = "Median.jpg"

# CHESSBOARD
cellPX = pxSizeFrame = 0
realSize = 5.93

# BG
medianLength = 50
medianFrames = [x for x in range(medianLength)]

medianName = "Median.jpg"