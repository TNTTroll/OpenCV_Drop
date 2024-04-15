# ------------ Imports
import cv2
import os
import time
import numpy as np

# ------------ Variables
cam_Width = 640
cam_Height = 480

cameraName = "Camera"

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, cam_Width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_Height)

cv2.namedWindow(cameraName)


fourcc = cv2.VideoWriter_fourcc(*'XVID')
path = r"123.avi"

f = "%d.%m.%y_%H-%M-%S"

t = "folder/%s.avi"%(time.strftime(f, time.gmtime()))
out = cv2.VideoWriter(t, fourcc, 30, (640, 480))


# ------------ Camera
while True:
    ret, frame = cam.read()

    out.write(frame)


    cv2.imshow(cameraName, frame)

    k = cv2.waitKey(10) & 0xFF

    if ((not ret) or (k == ord('q') or k == ord('й'))):
        break

# ------------ Exit
out.release()

cam.release()
cv2.destroyAllWindows()
cv2.waitKey(10)