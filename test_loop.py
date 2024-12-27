import pyxel

# ウインドウ設定
WINDOW_HEIGHT = 128
WINDOW_WIDTH = 128
TITLE = 'MainWindow'
FPS = 60


class App:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS, display_scale=2)
        self.init()
        pyxel.run(self.update, self.draw)

    def init(self):
        '''
        ゲーム内部変数初期化
        '''
        pyxel.mouse(False)
        pyxel.images[0].load(0, 0, 'assets/Pallet.png', incl_colors=True)
        self.x = 0
        self.y = pyxel.height / 2
        self.x2 = pyxel.width * 2 

    def update(self):
        '''
        データ更新
        '''
        if self.x < -255:
            self.x = self.x2 + 128 * 2
        if self.x2 < -255:
            self.x2 = self.x + 128 * 2
        self.x -= 1
        self.x2 -= 1

    def draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_GRAY)
        pyxel.blt(self.x, self.y, 0, 0, 0, 256, 16)
        pyxel.blt(self.x2, self.y, 0, 0, 0, 256, 16)

App()
