import pyxel

# ウインドウ設定
WINDOW_HEIGHT = 128
WINDOW_WIDTH = 128
TITLE = 'MainWindow'
FPS = 60

DT = 1 / FPS
G = 98

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class ball:
    def __init__(self):
        self.pos = Vec2(0, 0)
        self.vec = 0
        self.vel = 0
        self.weight = 1
        self.time = 0
    
    def update(self, x, y, dx):
        self.pos.x = x
        self.pos.y = y
        self.vec = dx


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
        self.ball = ball()
        self.ball.update(0, 0, 0)

    def update(self):
        '''
        データ更新
        '''
        if self.ball.pos.y < WINDOW_HEIGHT:
            f = self.ball.weight * G
            a = f / self.ball.weight
            self.ball.vel += a * DT
            self.ball.pos.y += self.ball.vel * DT
            self.ball.time += DT
            self.ball.update(self.ball.pos.x,
                             self.ball.pos.y,
                             self.ball.vec)

    def draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_BLACK)
        pyxel.elli(self.ball.pos.x, self.ball.pos.y - 10,
                   10, 10, pyxel.COLOR_WHITE)


App()
