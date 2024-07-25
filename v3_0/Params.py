# PROGRAM
screen = None
manager = None

WIDTH = 300
HEIGHT = 500

# CAMERA
cameraSize = [1920, 1200]        		# Camera size

coefficient = .5 			            # Coefficient for resizing

width = int(cameraSize[0] * coefficient)
height = int(cameraSize[1] * coefficient)

windowName = "Camera" 		            # Name for Camera window
FPS = 160.0                             # FPS

# UI
orbs = []

buttons = ["Record",                    # Record new material from camera
           "Replay",                    # Watch all the videos from the folder
           "Logging",                   # Process all the video from the folder
           ]

texts = []

# COLORS
colors = {"BG": (64, 93, 114),
          "orb": (117, 134, 148),
          "text": (247, 231, 220),
          }
