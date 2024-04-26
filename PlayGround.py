# ----- Imports
import cv2


# ----- Variables
WINDOW_VIDEO = "Video"
videoName = "1.mp4"
video = cv2.VideoCapture(videoName)

start = 0
playable = True

video.set(cv2.CAP_PROP_POS_FRAMES, start)

A = [0, 1, 2, 3]
# ----- Main
while True:


    ret, frame = video.read()


    print(A[:-2])


    cv2.imshow(WINDOW_VIDEO, frame)

    k = cv2.waitKey(10)
    if k == ord('q'):
        break

# ----- Exit
cv2.destroyAllWindows()
cv2.waitKey(10)