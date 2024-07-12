# --- Class
# Class for showing text on the screen limited amount of frames
class Text:
    def __init__(self, _timer, _text, _pos, _color, _size):
        self.timer = _timer
        self.text = _text
        self.pos = _pos
        self.color = _color
        self.size = _size

    def getInfo(self):
        self.timer -= 1
        if self.timer != 0:
            return [self.text, self.pos, self.color, self.size]
        return 0
