import pyxel
from math import cos
from math import sin

# ウインドウ設定
WINDOW_HEIGHT = 128
WINDOW_WIDTH = 128
TITLE = 'MainWindow'
FPS = 60


class App:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS)
        self.init()
        pyxel.run(self.update, self.draw)

    def init(self):
        '''
        ゲーム内部変数初期化
        '''
        pyxel.mouse(False)
        self.x = 0
        self.y = 0
        self.angle = 0
        self.cx = pyxel.width / 2
        self.cy = pyxel.height / 2
        self.radius = 0
        self.length = 30
        self.draw_ary = []

    def update(self):
        '''
        データ更新
        '''
        radius = self.angle * 3.14 / 180.0
        ax = cos(radius) * self.length
        ay = sin(radius) * self.length
        self.x = self.cx + ax
        self.y = self.cy + ay
        self.angle += 5
        self.length -= 1
        if 360 < self.angle:
            self.angle = 0
        if self.length < 0:
            self.length = 30
        if pyxel.btn(pyxel.KEY_LEFT):
            self.cx -= 1
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.cx += 1
        if pyxel.btn(pyxel.KEY_UP):
            self.cy -= 1
        if pyxel.btn(pyxel.KEY_DOWN):
            self.cy += 1

        self.draw_ary.append((self.x, self.y))
        if 10 < len(self.draw_ary):
            del self.draw_ary[0]


    def draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_BLACK)
        
        pyxel.elli(self.cx - 1, self.cy - 1, 2, 2, pyxel.COLOR_WHITE)
        c = 0
        for p in self.draw_ary:
            x, y = p
            c += 1
            pyxel.elli(x - 1, y - 1, 2, 2, c)

App()
