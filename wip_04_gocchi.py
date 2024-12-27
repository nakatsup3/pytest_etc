import pyxel
from datetime import datetime

# ウインドウ設定
WINDOW_HEIGHT = 64
WINDOW_WIDTH = 64
TITLE = 'MainWindow'
FPS = 15

ICON_W = WINDOW_WIDTH / 4
ICON_A_X = 5
ICON_B_X = 5 + ICON_W
ICON_C_X = 5 + ICON_W * 2
ICON_D_X = 5 + ICON_W * 3

BOTTOM_MENU_TOP = WINDOW_HEIGHT - 10
BOTTOM_ICO_TOP = BOTTOM_MENU_TOP + 2
JP_FONT = pyxel.Font("assets/umplus_j10r.bdf")

class Gocchi:
    def __init__(self):
        # 位置情報
        self.x = pyxel.width / 2 - 5
        self.y = BOTTOM_MENU_TOP - 15
        self.is_jump = False

        # 健康パラメータ
        self.is_helth = True    # 健康
        self.stmac = 0          # 空腹
        self.stress = 0         # ストレス

        # ステータス
        self.MAX_HP = 10    # 体力　最大値
        self.HP = 10        # 体力 現在値
        self.IQ = 0         # 知能

    def update(self):
        if pyxel.frame_count % 15 == 0:
            if self.is_jump:
                self.y += 6
            else:
                self.y -= 6
            self.is_jump = not self.is_jump
    
    def draw(self):
        pyxel.text(self.x, self.y, 'C', 0, JP_FONT)


class App:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS)
        self.init()
        pyxel.run(self.update, self.draw)

    def init(self):
        '''
        内部変数初期化
        '''
        pyxel.mouse(False)
        self.gocchi = Gocchi()
        self.menu_y = 0
        self.menu_x = 0

    def update(self):
        '''
        データ更新
        '''
        self.gocchi.update()
        if pyxel.btn(pyxel.KEY_LEFT):
            self.menu_x = max(0, self.menu_x - 1)
        if pyxel.btn(pyxel.KEY_UP):
            self.menu_y = max(0, self.menu_y - 1)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.menu_x = min(3, self.menu_x + 1)
        if pyxel.btn(pyxel.KEY_DOWN):
            self.menu_y = min(3, self.menu_y + 1)

    def draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_LIME)
        self.DrawMenu()
        self.gocchi.draw()

    def DrawMenu(self):
        pyxel.rect(0, 0, pyxel.width, 10, pyxel.COLOR_GRAY)
        pyxel.rect(0, BOTTOM_MENU_TOP, pyxel.width, 10, pyxel.COLOR_GRAY)

        pyxel.elli(ICON_A_X, 2, 6, 6, pyxel.COLOR_LIGHT_BLUE)
        pyxel.elli(ICON_B_X, 2, 6, 6, pyxel.COLOR_LIGHT_BLUE)
        pyxel.elli(ICON_C_X, 2, 6, 6, pyxel.COLOR_LIGHT_BLUE)
        pyxel.elli(ICON_D_X, 2, 6, 6, pyxel.COLOR_LIGHT_BLUE)
        
        pyxel.elli(ICON_A_X, BOTTOM_ICO_TOP, 6, 6, pyxel.COLOR_LIGHT_BLUE)
        pyxel.elli(ICON_B_X, BOTTOM_ICO_TOP, 6, 6, pyxel.COLOR_LIGHT_BLUE)
        pyxel.elli(ICON_C_X, BOTTOM_ICO_TOP, 6, 6, pyxel.COLOR_LIGHT_BLUE)
        pyxel.elli(ICON_D_X, BOTTOM_ICO_TOP, 6, 6, pyxel.COLOR_LIGHT_BLUE)

        if self.menu_y == 0:
            y = 2
        else:
            y = BOTTOM_ICO_TOP
        x = 5 + ICON_W * self.menu_x
        pyxel.elli(x, y, 6, 6, pyxel.COLOR_BLACK)
App()
