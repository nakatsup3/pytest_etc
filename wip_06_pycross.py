import pyxel
from pyxel import btnp


# ウインドウ設定
WINDOW_HEIGHT = 288
WINDOW_WIDTH = 288
TITLE = 'Pycross'
FPS = 60

ON = 1
OFF = 0

CELL_SIZE = 10


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
        self.umplus10 = pyxel.Font("assets/umplus_j10r.bdf")
        self.x = 0
        self.y = 0
        self.cell_row = 20
        self.cell_col = 20
        self.margin = 50
        self.player_map = [[OFF for _ in range(self.cell_row)]
                           for _ in range(self.cell_col)]
        self.answer_map = []

    def update(self):
        '''
        データ更新
        '''
        if btnp(pyxel.KEY_DOWN):
            self.y = min(self.cell_row - 1, self.y + 1)
        if btnp(pyxel.KEY_UP):
            self.y = max(0, self.y - 1)
        if btnp(pyxel.KEY_LEFT):
            self.x = max(0, self.x - 1)
        if btnp(pyxel.KEY_RIGHT):
            self.x = min(self.cell_col - 1, self.x + 1)
        if pyxel.btn(pyxel.KEY_SPACE):
            self.player_map[self.y][self.x] = ON
        if pyxel.btn(pyxel.KEY_X):
            self.player_map[self.y][self.x] = OFF

    def draw(self):
        '''
        描画更新
        '''
        # 背景
        pyxel.cls(pyxel.COLOR_BLACK)

        # 入力描画
        line_length = CELL_SIZE * self.cell_row + self.margin
        for r in range(self.cell_row):
            dy = r * CELL_SIZE + self.margin
            pyxel.line(0, dy, line_length, dy, pyxel.COLOR_GRAY)
            for c in range(self.cell_col):
                dx = c * CELL_SIZE + self.margin
                pyxel.line(dx, 0, dx, line_length, pyxel.COLOR_GRAY)
                if self.player_map[r][c] == ON:
                    pyxel.rect(dx + 1, dy + 1,
                               CELL_SIZE - 1, CELL_SIZE - 1, pyxel.COLOR_WHITE)
        # 最後の線
        dy = self.cell_row * CELL_SIZE + self.margin
        dx = self.cell_col * CELL_SIZE + self.margin
        pyxel.line(0, dy, line_length, dy, pyxel.COLOR_GRAY)
        pyxel.line(dx, 0, dx, line_length, pyxel.COLOR_GRAY)

        # 入力枠 移動
        x = self.x * CELL_SIZE + self.margin
        y = self.y * CELL_SIZE + self.margin
        pyxel.rectb(x, y, CELL_SIZE + 1, CELL_SIZE + 1, pyxel.COLOR_RED)
        
        for i in range(self.cell_row):
            pyxel.text(20, self.margin + i * CELL_SIZE + 4, '123456',
                       pyxel.COLOR_WHITE)
        for i in range(self.cell_col):
            pyxel.text(self.margin + 3 + i * CELL_SIZE, self.margin - 20,
                       '1\n2\n3', pyxel.COLOR_WHITE)



App()
