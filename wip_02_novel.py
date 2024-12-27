import pyxel
from enum import Enum

# ウインドウ設定
WINDOW_HEIGHT = 256
WINDOW_WIDTH = 256
TITLE = 'MainWindow'
FPS = 60

TEXT_MAX_ROW = 16
TEXT_MAX_LEN = 23
TEXT_HEIGHT = 15


class State(Enum):
    Title = 1
    Read = 2
    Message = 3
    Wait = 4
    Select = 5


class App:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS)
        pyxel.mouse(True)

        self.umplus10 = pyxel.Font("assets/umplus_j10r.bdf")
        self.text_buff = []
        self.text_disp = ['' for _ in range(TEXT_MAX_ROW)]
        self.tr = 0
        self.tc = 0
        self.is_next_page = False
        self.state = State.Read
        self.senario = []
        with open('assets/senario.txt', mode='r', encoding='utf-8') as f:
            self.senario = f.read().split('\n')

        pyxel.run(self.update, self.draw)

    def update(self):
        '''
        データ更新
        '''
        if self.state == State.Read:
            self.tc = 0
            while self.senario:
                s = self.senario.pop(0)
                if s == ',':
                    self.state = State.Message
                    self.is_next_page = False
                    break
                if s == '.':
                    self.state == State.Message
                    self.tr = 0
                    self.is_next_page = True
                    break
                if s.startswith('['):
                    self.text_buff.append(s.lstrip('['))
            if len(self.senario) <= 0:
                self.state = State.Message

        elif self.state == State.Message:
            if self.tr < len(self.text_buff):
                buff = self.text_buff[self.tr]
                if self.tc < len(buff):
                    self.text_disp[self.tr] += self.text_buff[self.tr][self.tc]
                    self.tc += 1
                else:
                    self.tr += 1
                    self.tc = 0
            else:
                self.state = State.Wait

        elif self.state == State.Wait:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.state = State.Read
                if self.is_next_page:
                    for s in range(len(self.text_disp)):
                        self.text_disp[s] = ''
                    self.text_buff.clear()
                    self.tr = 0
                    self.tc = 0

    def draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_GRAY)
        pyxel.dither(0.5)
        pyxel.rect(5, 5, pyxel.width - 10, pyxel.height - 10, pyxel.COLOR_BLACK)
        pyxel.dither(1.0)
        for i in range(16):
            self.draw_text_mid(10 + i * TEXT_HEIGHT, self.text_disp[i],
                               pyxel.COLOR_WHITE, pyxel.COLOR_RED)

    def draw_text_mid(self, y, s, col, bcol=None):
        '''
        テキスト描画
        '''
        # x = pyxel.width / 2 - self.umplus10.text_width(s) / 2
        if bcol is None:
            bcol = pyxel.COLOR_BLACK
        # アウトライン描画
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx != 0 or dy != 0:
                    pyxel.text(13 + dx, y + dy, s, bcol, self.umplus10)
        # 
        pyxel.text(13, y, s, col, self.umplus10)

App()
