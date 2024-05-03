# ----- Imports
import cv2


# ----- Variables
WINDOW_VIDEO = "Video"
videoName = "1.mp4"
video = cv2.VideoCapture(videoName)

start = 0
playable = True

video.set(cv2.CAP_PROP_POS_FRAMES, start)

A = [x for x in range(10)]

# ----- Main
while True:


    ret, frame = video.read()


    print(A)
    print(sum(A))


    cv2.imshow(WINDOW_VIDEO, frame)

    k = cv2.waitKey(10)
    if k == ord('q'):
        break

# ----- Exit
cv2.destroyAllWindows()
cv2.waitKey(10)