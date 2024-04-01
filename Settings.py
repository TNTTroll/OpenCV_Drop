# --- Imports
import cv2
from pypylon import pylon
from pypylon_opencv_viewer import BaslerOpenCVViewer

import Params as P


# --- Defs
# <<< Program
def exit(isExternal, camera, program):
	if isExternal:
		closeExternalCam(camera)
	else:
		closeInternalCam(camera)

	program.quit()
	cv2.destroyAllWindows()
	cv2.waitKey(10)

	print("\n\nProgram has been closed")


# <<< Camera
def getCamBySerial():
	global cameraMode

	for i in pylon.TlFactory.GetInstance().EnumerateDevices():
		if i.GetSerialNumber() == P.serialNumber:
			cameraMode = 1

			camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(P.isExternal))
			camera.Open()

			setCamSize(camera)

			camera.StartGrabbing(1)

			return i, camera
	else:
		cameraMode = 0

		camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

		setCamSize(camera)

		return None, camera

def setCamSize(camera):
	if P.isExternal:
		if P.isTextShown:
			camera.Width.SetValue( int(P.cameraWidth * P.coefficient) )
			camera.Height.SetValue( int(P.cameraHeight * P.coefficient) )
		else:
			camera.Width.SetValue( P.cameraWidth )
			camera.Height.SetValue( P.cameraHeight )

	else:
		if P.isTextShown:
			camera.set( cv2.CAP_PROP_FRAME_WIDTH, int(P.cameraWidth * P.coefficient) )
			camera.set( cv2.CAP_PROP_FRAME_HEIGHT, int(P.cameraHeight * P.coefficient) )

		else:
			camera.set( cv2.CAP_PROP_FRAME_WIDTH, P.cameraWidth )
			camera.set( cv2.CAP_PROP_FRAME_HEIGHT, P.cameraHeight )

def getImageExternalCam(camera):
	grab = camera.RetrieveResult(2000, pylon.TimeoutHandling_Return)

	return grab.GetArray() if grab.GrabSucceeded() else None

def closeExternalCam(camera):
	camera.Close()

def getImageInteranlCam(camera):
	ret, frame = camera.read()

	return frame if ret else None

def closeInternalCam(camera):
	camera.release()