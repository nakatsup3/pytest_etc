import pyxel

# ウインドウ設定
WINDOW_HEIGHT = 128
WINDOW_WIDTH = 128
TITLE = 'MainWindow'
FPS = 60


class ObjectBase:
    def __init__(self, x: float, y: float, w: float, h: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def err_update(self):
        '''
        データ更新
        '''
        pass

    def err_draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_BLACK)
        pyxel.text(5, 5, 'Initialize error', pyxel.COLOR_WHITE)


class Punch(ObjectBase):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 10, 10)
        self.wait = 80
        self.speed = 0

    def update(self):
        if self.wait <= 0:
            self.x = pyxel.rndi(0, pyxel.width - self.w)
            self.y = pyxel.rndi(0, pyxel.height - self.h)
            self.wait = 80
        self.wait -= 1

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, pyxel.COLOR_WHITE)

class App(ObjectBase):
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS, display_scale=2)
        pyxel.mouse(False)
        has_resource = self.ReadResources()
        self.DefineVariables()
        if has_resource:
            pyxel.run(self.update, self.draw)
        else:
            pyxel.run(self.err_update, self.err_draw)

    def ReadResources(self) -> bool:
        '''
        リソースファイルの読み込み
        '''
        # pyxel.images[0].load(0, 0, 'assets/Pallet.png', incl_colors=True)
        # self.fnt_jp_10 = pyxel.Font('assets/umplus_j10r.bdf')
        return True

    def DefineVariables(self):
        '''
        内部変数初期化
        '''
        self.punch = Punch(64, 64)

    def update(self):
        '''
        データ更新
        '''
        self.punch.update()

    def draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_BLACK)
        self.punch.draw()


App()
