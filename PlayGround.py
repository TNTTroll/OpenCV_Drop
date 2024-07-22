# --- Imports
import cv2
import numpy as np
import socket


# --- Variables
camera = cv2.VideoCapture(0)
windowName = 'Video'


HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)


# --- Main
'''
while False:
    ret, frame = camera.read()
    if not ret: break

    cv2.imshow(windowName, frame)
    if cv2.waitKey(1) == ord('q'):
        break
'''


# --- Exit
camera.release()
cv2.destroyAllWindows()
cv2.waitKey(10)