# --- Imports
import cv2
import numpy as np
import ctypes


# --- Variables
camera = cv2.VideoCapture(0)
WINDOW_NAME = 'Video'


x = []
x.append('1')
x.append('4')
x.append('5')
print(x)

x = [elt.encode("utf-8") for elt in x]
print(x)

buffer = (ctypes.c_char_p * 3)(*x)
print(buffer)

arr = [elt.decode("utf-8") for elt in buffer]
print(arr)


# --- Main
while False:
    _, frame = camera.read()

    cv2.imshow(WINDOW_NAME, frame)
    if cv2.waitKey(1) == ord('q'):
        break


# --- Exit
camera.release()
cv2.destroyAllWindows()
cv2.waitKey(10)