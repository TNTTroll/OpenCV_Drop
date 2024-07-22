# --- Imports
import random

import pygame as pg
import pygame_gui as pg_gui


# --- Variables
# <<< WINDOW
windowTitle = "SNAKE"

width = 500
height = 500

fps = 30
speed = 4

# <<< COLOR
colorBG = (248, 242, 220)
colorHead = (43, 83, 32)
colorTail = (71, 123, 40)
colorApple = (166, 38, 46)

# <<< GRID
rows = 10
columns = 10

grid = [[['', colorBG] for x in range(rows)] for y in range(columns)]


# --- Defs
def setGrid():
    step = width // len(grid)
    offset = step // 4
    for i in range(rows):
        for j in range(columns):
            putText(grid[i][j][0], (i*step+offset, j*step+offset), grid[i][j][1])

def putText(text, pos, color, size=40):
    font = pg.font.SysFont(None, size)
    showText = font.render(str(text), True, color)
    screen.blit(showText, (pos[0], pos[1]))

def endGame(state):
    putText(state, (width*.25, height*.4), 'black', size=60)
    putText(f"Score: {snake.length}", (width * .35, height * .5), 'black', size=50)
    global reset
    reset.visible = True

def startGame():
    global snake, reset
    snake = Snake()
    reset.visible = False


# --- Class
class Snake:
    length = 1
    applePos = []

    headText = 'S'
    tailText = 'nake'
    tailEnd = '.'
    appleText = '@'

    side = "RIGHT"
    alive = True

    def __init__(self):
        self.headPos = [rows // 2, columns // 2]
        self.tail = [[rows//2, columns//2] for x in range(self.length)]

        for i in range(self.length):
            try:
                grid[self.tail[i][0]][self.tail[i][1]] = [self.tailText[i], colorTail]
            except(IndexError):
                grid[self.tail[i][0]][self.tail[i][1]] = [self.tailText[-1], colorTail]
        grid[self.headPos[0]][self.headPos[1]] = [self.headText, colorHead]

        self.setApple()
        self.setSnake()

    def setSnake(self):
        for i in range(rows):
            for j in range(columns):
                grid[i][j] = ['', colorBG]

        grid[self.applePos[0]][self.applePos[1]] = [self.appleText, colorApple]
        for i in range(self.length):
            try:
                grid[self.tail[i][0]][self.tail[i][1]] = [self.tailText[i], colorTail]
            except(IndexError):
                grid[self.tail[i][0]][self.tail[i][1]] = [self.tailText[-1], colorTail]
        grid[self.tail[-1][0]][self.tail[-1][1]] = [self.tailEnd, colorTail]
        grid[self.headPos[0]][self.headPos[1]] = [self.headText, colorHead]

    def makeMove(self):
        for i in range(self.length-1):
            self.tail[self.length-i-1] = self.tail[self.length-i-2]
        self.tail[0] = [self.headPos[0], self.headPos[1]]

        if self.side == "RIGHT":
            self.headPos[0] = self.headPos[0]+1 if self.headPos[0] < columns-1 else 0
        elif self.side == "LEFT":
            self.headPos[0] = self.headPos[0]-1 if self.headPos[0] > 0 else columns-1
        elif self.side == "DOWN":
            self.headPos[1] = self.headPos[1]+1 if self.headPos[1] < rows-1 else 0
        elif self.side == "UP":
            self.headPos[1] = self.headPos[1]-1 if self.headPos[1] > 0 else rows-1

        self.setSnake()
        self.checkCol()

    def newCell(self):
        self.length += 1
        self.tail.append([self.tail[-1]])
        self.tail[-1] = self.tail[-2]

        if self.length == 99:
            self.die("WIN")

    def setApple(self):
        arr = []
        for i in range(rows):
            for j in range(columns):
                if grid[i][j][0] == '':
                    arr.append([i, j])

        self.applePos = arr[random.randint(0, len(arr) - 1)]
        grid[self.applePos[0]][self.applePos[1]] = [self.appleText, colorApple]

    def checkCol(self):
        for i in range(self.length):  # Death
            if self.headPos == self.tail[i]:
                self.die("GAME OVER")

        if self.headPos == self.applePos:  # Apple
            self.newCell()
            self.setApple()

    def die(self, state):
        for i in range(rows):
            for j in range(columns):
                grid[i][j] = ['', colorBG]

        self.alive = False
        endGame(state)


# --- Main
pg.init()
pg.mixer.init()
pg.display.set_caption(windowTitle)
clock = pg.time.Clock()
screen = pg.display.set_mode((width, height))
manager = pg_gui.UIManager((width, height))

reset = pg_gui.elements.UIButton(relative_rect=pg.Rect((width*.3, height*.6), (200, 70)),
                                 text="RESTART", manager=manager, visible=False)

snake = Snake()

isRunning = True
count = 0
while isRunning:
    screen.fill(colorBG)

    if snake.alive:
        if count == speed:
            snake.makeMove()
    else:
        endGame("GAME OVER")

    setGrid()

    count = count+1 if count < speed else 0

    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_q:  # Exit the program
               isRunning = False

            if event.key == pg.K_a:  # Move left
               snake.side = "LEFT"
            elif event.key == pg.K_w:  # Move up
               snake.side = "UP"
            elif event.key == pg.K_d:  # Move right
               snake.side = "RIGHT"
            elif event.key == pg.K_s:  # Move down
               snake.side = "DOWN"

        if event.type == pg_gui.UI_BUTTON_PRESSED:
            if event.ui_element == reset:
                startGame()

        manager.process_events(event)

    clock.tick(fps)
    time_delta = clock.tick(60) / 1000.0
    manager.update(time_delta)

    manager.draw_ui(screen)
    pg.display.flip()