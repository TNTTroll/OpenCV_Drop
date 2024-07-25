# --- Imports
import random

import cv2
import numpy as np
import math
import time


# --- Variables
windowName = 'Shape'

dimension = (350, 200)

i = 100
print(i)

i = float(i)
print(i)

# --- Defs
def findMask(photo):
    frame = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY_INV)[1]

    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

def findPoints(frame):
    temp = frame.copy()

    gray = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
    border = cv2.copyMakeBorder(gray, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    contours, hierarchy = cv2.findContours(border, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, offset=(-1, -1))

    distances = []
    for i in range(len(contours[0])-1):
        for j in range(i+1, len(contours[0])):
            p1 = contours[0][i][0]
            p2 = contours[0][j][0]
            dist = math.sqrt( math.pow(p1[0]-p2[0], 2) + math.pow(p1[1] - p2[1], 2) )

            distances.append([dist, i, j])

    distances.sort(reverse=True)
    for dist in distances:
        p1 = contours[0][dist[1]][0]
        p2 = contours[0][dist[2]][0]
        if ( p1, p2, frame ):
            cv2.line( temp, p1, p2, (255, 0, 255), 1 )
            break

    return temp

def isInside(p1, p2, mask) -> bool:
    line = np.unique(np.round(np.linspace(p1, p2, num=1000)), axis=0).astype('uint8')
    return np.all(mask[line[:, 1], line[:, 0]] == 255)


# --- Main
rows = []
start = time.time()
for i in range(3):
    photo = cv2.resize( cv2.imread(f"V2_0/{i+1}.png"), dimension)

    mask = findMask(photo)

    points = findPoints(mask)

    row = np.hstack(( photo, mask, points ))
    rows.append(row)

print(f"Time: {(time.time() - start)/3}")

show = np.vstack((rows))
cv2.imshow(windowName, show)

if cv2.waitKey(0) == ord('q'):
    cv2.destroyAllWindows()
    cv2.waitKey(10)




'''
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