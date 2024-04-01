import cv2

cap = cv2.VideoCapture(0)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('C:/Users/Spectre/Desktop/Programming/Work/output.avi', fourcc, 20.0, (640, 480))

while (True):
    ret, frame = cap.read()

    cv2.imshow('Original', frame)

    out.write(frame)

    if cv2.waitKey(1) & 0xFF == ord('a'):
        break


cap.release()
out.release()
cv2.destroyAllWindows()