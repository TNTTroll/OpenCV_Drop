# --- Imports
import cv2
import numpy as np
import math
import time


# --- Variables
dimension = [350, 200]
windowName = "DIAGONAL"


# --- Main
def text(frame, text, pos):
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (pos[0], pos[1])

    cv2.putText(frame, str(text), org, font,
                .5, (0, 0, 0), 2, cv2.LINE_AA)

    return frame

def findPoints(frame):
    temp = frame.copy()

    gray = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)[1]

    border = cv2.copyMakeBorder(thresh, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    contours, hierarchy = cv2.findContours(border, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(-1, -1))

    h = cv2.fitEllipse(contours[0])
    m = cv2.ellipse(temp, h, (0, 255, 0), 2)

    radius = [0, 0]
    distances = []
    for i in range(len(contours[0])-1):
        for j in range(i+1, len(contours[0])):
            p1 = contours[0][i][0]
            p2 = contours[0][j][0]
            dist = math.sqrt(math.pow(p1[0]-p2[0], 2) + math.pow(p1[1] - p2[1], 2))

            distances.append([dist, i, j])

    start = None
    distances.sort(reverse=True)
    for dist in distances:
        p1 = contours[0][dist[1]][0]
        p2 = contours[0][dist[2]][0]

        line = np.unique(np.round(np.linspace(p1, p2, num=1000)), axis=0).astype('uint8')
        if np.all(thresh[line[:, 1], line[:, 0]] == 255):
            cv2.line(temp, p1, p2, (255, 0, 255), 1)
            start = dist[1]
            radius[0] = dist[0]
            break

    orthogonal = []
    for i in range(len(contours[0])):
        try:
            p1 = contours[0][start+i][0]
            p2 = contours[0][start-i][0]
            dist = math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))

            orthogonal.append([dist, i])
        except(IndexError):
            break

    orthogonal.sort(reverse=True)
    for dist in orthogonal:
        p1 = contours[0][start+dist[1]][0]
        p2 = contours[0][start-dist[1]][0]

        line = np.unique(np.round(np.linspace(p1, p2, num=1000)), axis=0).astype('uint8')
        if np.all(thresh[line[:, 1], line[:, 0]] == 255):
            cv2.line(temp, p1, p2, (255, 0, 255), 1)
            radius[1] = dist[0]
            break

    return temp, radius, m

def findBorder(frame, lines, radius):
    c = lines.copy()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]

    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel=np.ones((1, 1)), iterations=1)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=np.ones((4, 4)), iterations=1)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=np.ones((4, 4)), iterations=1)

    output = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
    num_labels = output[0]
    stats = output[2]

    for i in range(num_labels):
        a = stats[i, cv2.CC_STAT_AREA]
        t = stats[i, cv2.CC_STAT_TOP]
        l = stats[i, cv2.CC_STAT_LEFT]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]

        if w != frame.shape[1]:
            cv2.rectangle(c, (l, t), (l + w, t + h), (255, 0, 255), 1)
            #text(c, round(radius[1], 2), (int(l + w*.3), int(t + h)))
            #text(c, round(radius[0], 2), (int(l + w), int(t + h * .5)))

            #text(c, a, (int(l + w), int(t + h)))
            volume = math.pi * radius[0] * radius[1] / 4
            diff = abs(volume - a)
            percent = diff / a * 100
            text(c, f"{round(percent, 2)}%", (l + w, t))

            #text(c, f"V: {round(volume, 2)}", (l + w, t))

    return c

def getDiagonals(frame):
    temp = frame.copy()

    gray = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)[1]

    border = cv2.copyMakeBorder(thresh, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    contours, hierarchy = cv2.findContours(border, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(-1, -1))

    radius = [0, 0]
    distances = []
    for i in range(len(contours[0]) - 1):
        for j in range(i + 1, len(contours[0])):
            p1 = contours[0][i][0]
            p2 = contours[0][j][0]
            dist = math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))
            distances.append([dist, i, j])

    start = None
    distances.sort(reverse=True)
    for dist in distances:
        p1 = contours[0][dist[1]][0]
        p2 = contours[0][dist[2]][0]

        line = np.unique(np.round(np.linspace(p1, p2, num=1000)), axis=0).astype('uint8')
        if np.all(thresh[line[:, 1], line[:, 0]] == 255):
            cv2.line(temp, p1, p2, (255, 0, 255), 1)
            start = dist[1]
            radius[0] = dist[0]
            break

    orthogonal = []
    for i in range(len(contours[0])):
        try:
            p1 = contours[0][start + i][0]
            p2 = contours[0][start - i][0]
            dist = math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))
            orthogonal.append([dist, i])
        except(IndexError):
            break

    orthogonal.sort(reverse=True)
    for dist in orthogonal:
        p1 = contours[0][start + dist[1]][0]
        p2 = contours[0][start - dist[1]][0]

        line = np.unique(np.round(np.linspace(p1, p2, num=1000)), axis=0).astype('uint8')
        if np.all(thresh[line[:, 1], line[:, 0]] == 255):
            cv2.line(temp, p1, p2, (255, 0, 255), 1)
            radius[1] = dist[0]
            break

    print(f"Square: {math.pi * radius[0] * radius[1] / 4}")

    return temp


rows = []
start = time.time()
for i in range(3):
    photo = cv2.resize( cv2.imread(f"V2_0/{i+1}.png"), dimension)

    lines, radius, h = findPoints(photo)
    square = findBorder(photo, lines, radius)
    ellipse = getDiagonals(photo)

    row = np.hstack(( photo, ellipse ))
    rows.append(row)

print(f"Time: {(time.time() - start)/3}")

show = np.vstack((rows))
cv2.imshow(windowName, show)

if cv2.waitKey(0) == ord('q'):
    cv2.destroyAllWindows()
    cv2.waitKey(10)

# --- Savings
'''
# --- ARDUINO
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())

for port in ports:
    print(f"Порт: {port.device}")
    print(f"Описание: {port.description}")
    print(f"Производитель: {port.manufacturer}\n")

Arduino: https://amperkot.ru/blog/serial-py/


# --- ORB CLASS
class Orb:
    def __init__(self, _pos, _path):
        self.pos = _pos
        self.radius = 10
        self.step = 0

        self.angle = random() * pi * 2
        self.inPos = True
        self.goTo = deepcopy(_pos)
        self.path = _path

    def move(self, dt):
        if not self.inPos:
            if self.step >= self.path:
                self.inPos = True
                self.step = 0

            angle = atan(abs(self.goTo[1] - self.pos[1]) / abs(self.goTo[0] - self.pos[0]))
            s = dt*50

            if self.goTo[0] - self.pos[0] > 0:
                self.pos[0] += s * cos(angle)
            else:
                self.pos[0] -= s * cos(angle)

            if self.goTo[1] - self.pos[1] > 0:
                self.pos[1] += s * sin(angle)
            else:
                self.pos[1] -= s * sin(angle)

            self.step += 1

        else:
            if self.goTo[0] < -2000: self.goTo[0] += 500
            if self.goTo[0] > 2000:   self.goTo[0] -= 500
            if self.goTo[1] < -2000:  self.goTo[1] += 500
            if self.goTo[1] > 2000:   self.goTo[1] -= 500

            self.angle += .1
            choice = randint(1, 4)

            if choice == 1:
                self.goTo[0] += cos(self.angle) * 100
                self.goTo[1] += sin(self.angle) * 100
            elif choice == 2:
                self.goTo[0] -= cos(self.angle) * 100
                self.goTo[1] += sin(self.angle) * 100
            elif choice == 3:
                self.goTo[0] += cos(self.angle) * 100
                self.goTo[1] -= sin(self.angle) * 100
            else:
                self.goTo[0] -= cos(self.angle) * 100
                self.goTo[1] -= sin(self.angle) * 100

            self.inPos = False

        if not (1 < self.pos[0] < P.WIDTH and 1 < self.pos[1] < P.HEIGHT):
            self.pos[0] = P.WIDTH / 2
            self.pos[1] = P.HEIGHT / 2
            self.goTo[0] = self.pos[0] - 10
            self.goTo[1] = self.pos[1] - 10

        pg.draw.circle(P.screen, P.colors['orb'], self.pos, 20)
'''