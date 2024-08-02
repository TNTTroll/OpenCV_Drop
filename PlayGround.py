# --- Imports
import cv2
import numpy as np
import math
import time


# --- Variables
dimension = [350, 200]
windowName = "DIAGONAL"


images = "15"


# --- Main
def showImages(img1, img2 = None):
    rows = []

    photo = cv2.resize(cv2.imread(f"V2_0/{img1}.png"), dimension)

    lines, radius = findPoints(photo)
    # square = findBorder(photo, lines, radius)
    ellipse = findEllipse(photo)

    rows.append(np.hstack((photo, lines, ellipse)))

    if img2 != None:
        photo = cv2.resize(cv2.imread(f"V2_0/{img2}.png"), dimension)

        lines, radius = findPoints(photo)
        # square = findBorder(photo, lines, radius)
        ellipse = findEllipse(photo)

        rows.append(np.hstack((photo, lines, ellipse)))

    show = np.vstack((rows))
    return show


def text(frame, text, pos, color=(0, 0, 0)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (pos[0], pos[1])

    cv2.putText(frame, str(text), org, font,
                .5, color, 2, cv2.LINE_AA)

    return frame

def getMask(frame):
    try:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    except:
        pass

    thresh = cv2.threshold(frame, 30, 255, cv2.THRESH_BINARY_INV)[1]

    im_floodfill = thresh.copy()
    h, w = thresh.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(im_floodfill, mask, (0, 0), 255)
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)
    im_out = im_floodfill_inv | thresh

    cv2.imshow("OUT", im_out)

    return im_out

def findPoints(frame):
    temp = frame.copy()

    mask = getMask(temp)
    thresh = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]

    border = cv2.copyMakeBorder(thresh, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    contours, hierarchy = cv2.findContours(border, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(-1, -1))

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

    output = cv2.connectedComponentsWithStats(getMask(frame), 4, cv2.CV_32S)
    num_labels = output[0]
    stats = output[2]

    for i in range(num_labels):
        if stats[i, cv2.CC_STAT_WIDTH] != frame.shape[1]:
            volume = math.pi * radius[0] * radius[1] / 4
            a = stats[i, cv2.CC_STAT_AREA]

            text(temp, f"V: {round(volume, 2)}", (50, 20), (100, 0, 100))
            text(temp, f"A: {a}", (50, 40), (150, 150, 100))
            text(temp, f"{round((abs(volume-a)/volume*100), 2)}%", (50, 60), (150, 0, 150))

    text(temp, f"Mine", (frame.shape[1]-50, 20), (10, 10, 10))
    return temp, radius

def findBorder(frame, lines, radius):
    c = lines.copy()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    mask = getMask(gray)

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
            #text(c, f"{round(percent, 2)}%", (l + w, t))

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

def findEllipse(frame):
    temp = frame.copy()

    gray = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)[1]

    border = cv2.copyMakeBorder(thresh, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    contours, hierarchy = cv2.findContours(border, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(-1, -1))

    for i in range(len(contours)):
        if len(contours[i]) >= 5:
            h = cv2.fitEllipse(contours[i])
            cv2.ellipse(temp, h, (0, 255, 0), 1)

            cx = int(h[0][0])
            cy = int(h[0][1])

            angle = (h[2] * math.pi) / 180
            a = h[1][0] / 2
            b = h[1][1] / 2

            dots = []
            for i in range(4):
                alpha = angle + (math.pi/2) * i
                side = a if i%2==0 else b
                x = cx + int(side * math.cos(alpha))
                y = cy + int(side * math.sin(alpha))
                dots.append([x, y])

            cv2.line(temp, dots[0], dots[2], (255, 0, 0), 1)
            cv2.line(temp, dots[1], dots[3], (255, 0, 255), 1)

    output = cv2.connectedComponentsWithStats(getMask(frame), 4, cv2.CV_32S)
    num_labels = output[0]
    stats = output[2]

    for i in range(num_labels):
        if stats[i, cv2.CC_STAT_WIDTH] != frame.shape[1]:
            volume = math.pi * a * b
            a = stats[i, cv2.CC_STAT_AREA]

            text(temp, f"V: {round(volume, 2)}", (50, 20), (100, 0, 100))
            text(temp, f"A: {a}", (50, 40), (150, 150, 100))
            text(temp, f"{round((abs(volume-a)/volume*100), 2)}%", (50, 60), (150, 0, 150))

    volume = math.pi * a * b
    #text(temp, round(volume, 2), (cx+50, cy+50))

    text(temp, f"Fit", (frame.shape[1] - 50, 20), (10, 10, 10))
    return temp

image = images.split(" ")
counter = len(image)//2
for i in range(counter):
    cv2.imshow(f"Photos {i}", showImages(image[2*i], image[2*i+1]))

if len(image) % 2 != 0:
    cv2.imshow("Photo", showImages(image[-1]))

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