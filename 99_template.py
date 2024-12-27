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
        # self.x = 0
        pass

    def update(self):
        '''
        データ更新
        '''
        # if pyxel.btn(pyxel.KEY_LEFT):
        #     pass
        pass

    def draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_BLACK)


App()
