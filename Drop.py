# --- Imports
import Params as P


# --- Class
# Class for an object on the screen. Collecting all information, store and update it
class Drop:
    def __init__(self, _area, _width, _height, _left, _top):
        self.areaPX = [_area]
        self.areaMM = [round((self.areaPX / P.pxSizeFrame), 3) if P.pxSizeFrame != 0 else 0]
        self.width = [_width]
        self.height = [_height]
        self.left = [_left]
        self.top = [_top]

    def addParam(self, newState):
        self.areaPX.append(newState.areaPX[0])
        self.areaMM.append(newState.areaMM[0])
        self.width.append(newState.width[0])
        self.height.append(newState.height[0])
        self.left.append(newState.left[0])
        self.top.append(newState.top[0])

    def getAreaPX(self):
        return sum(self.areaPX) / len(self.areaPX)

    def getAreaMM(self):
        return sum(self.areaMM) / len(self.areaMM)

    def getLeft(self):
        return max(self.left)