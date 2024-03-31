# --- Imports
import cv2
from pypylon import pylon
from pypylon_opencv_viewer import BaslerOpenCVViewer

from Params import *


# --- Defs
# <<< Program
def setWindows():
	cv2.namedWindow(WINDOW_CAM)
	cv2.namedWindow(WINDOW_PARAMS)

	cv2.resizeWindow(WINDOW_PARAMS, 400, 600)

def exit(isExternal, camera):
	if isExternal:
		camera.Close()
	else:
		camera.release()

	cv2.destroyAllWindows()

	cv2.waitKey(10)

	print("Program has been closed")


# <<< Camera
def getCamBySerial():
	for i in pylon.TlFactory.GetInstance().EnumerateDevices():
		if i.GetSerialNumber() == serialNumber:
			return i
	else:
		print(f"There is no camera with {serialNumber} serial number")
		return None

def getImageExternalCam(camera):
	grab = camera.RetrieveResult(2000, pylon.TimeoutHandling_Return)
	if grab.GrabSucceeded():
	    frame = grab.GetArray()

	    return frame
	return None

def getImageInteranlCam(camera):
	ret, frame = camera.read()

	if ret:
		return frame
	return None