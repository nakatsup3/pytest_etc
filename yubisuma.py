import pyxel
from enum import Enum
import random

# ウインドウ設定
WINDOW_HEIGHT = 256
WINDOW_WIDTH = 256
TITLE = 'MainWindow'
FPS = 60
FNT_TYPE_JP = 1

LEFT = 0
RIGHT = 1

try:
    UMPLUS_J10R = pyxel.Font('assets/umplus_j10r.bdf')
except Exception:
    UMPLUS_J10R = None


class State(Enum):
    TITLE = 0
    PLAY = 1
    JUDGE = 2
    RESULT = 3
    GAME_END = 4


class Turn(Enum):
    PLAYER = 0
    COM = 1


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
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        self.draw_text_center('Initialize error',
                              pyxel.height / 2, pyxel.COLOR_WHITE)

    def draw_text_center(self, txt, y, color, fnt=0):
        '''
        中央寄せテキスト表示
        '''
        if fnt == FNT_TYPE_JP:
            x = pyxel.width / 2 - UMPLUS_J10R.text_width(txt) / 2
            if UMPLUS_J10R is not None:
                pyxel.text(x, y, txt, color, UMPLUS_J10R)
        else:
            x = pyxel.width / 2 - len(txt) * 2
            pyxel.text(x, y, txt, color)


class UnitBase(ObjectBase):
    def __init__(self, x: float, y: float, w: float, h: float):
        super().__init__(x, y, w, h)
        self.unit = [True, True]
        self.flg = [0, 0]
        self.selected = 0

        self.x_left = x - 1
        self.x_right = x + w + 1

    def toggleFlag(self, index: int):
        if self.unit[index]:
            if self.flg[index] == 0:
                self.flg[index] = 1
            else:
                self.flg[index] = 0
        else:
            self.flg[index] = 0
    
    def can_max_count(self)->int:
        return self.unit.count(True)
    
    def flag_count(self)->int:
        return sum(self.flg)
    
    def clear(self):
        self.unit[LEFT] = True
        self.unit[RIGHT] = True
        self.flg[LEFT] = 0
        self.flg[RIGHT] = 0

    def flag_clear(self):
        self.flg[LEFT] = 0
        self.flg[RIGHT] = 0
    
    def unit_down(self)->bool:
        if self.unit[0]:
            self.unit[0] = False
            return False
        else:
            self.unit[1] = False
            return True

    def draw(self):
        if self.unit[LEFT]:
            pyxel.rect(self.x_left, self.y, self.w, self.h, pyxel.COLOR_WHITE)
        if self.unit[RIGHT]:
            pyxel.rect(self.x_right, self.y, self.w, self.h, pyxel.COLOR_WHITE)
        if self.flg[LEFT] == 1:
            pyxel.rect(self.x - 1, self.y - 10, 10, 20, pyxel.COLOR_WHITE)
        if self.flg[RIGHT] == 1:
            pyxel.rect(self.x_right + self.w - 10, self.y - 10,
                       10, 20, pyxel.COLOR_WHITE)


class Player(UnitBase):
    def __init__(self):
        super().__init__(pyxel.width / 2 - 15, pyxel.height - 10, 15, 10)

    def update(self, turn: Turn):
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.toggleFlag(LEFT)
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.toggleFlag(RIGHT)
        if turn == Turn.PLAYER:
            if pyxel.btnp(pyxel.KEY_UP):
                self.selected -= 1
                if self.selected < 0:
                    self.selected = 0
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.selected += 1
                if 4 < self.selected:
                    self.selected = 4

    def draw(self, turn):
        super().draw()
        if turn == Turn.PLAYER:
            x = 5
            y = pyxel.height - 15
            for i in range(0, 5):
                pyxel.text(x, y, f'{4 - i}', pyxel.COLOR_WHITE)
                if self.selected == 4 - i:
                    pyxel.rectb(x - 1, y - 1, 6, 6, pyxel.COLOR_RED)
                y  -= 10


class Com(UnitBase):
    def __init__(self):
        super().__init__(pyxel.width / 2 - 15, pyxel.height / 2 - 10, 15, 10)
        self.selected

    def random_set(self, player: Player):
        self.flg[LEFT] = random.randint(0, 1) if self.unit[LEFT] else 0
        self.flg[RIGHT] = random.randint(0, 1) if self.unit[RIGHT] else 0
        com_max = self.can_max_count()
        player_max = player.can_max_count()
        max = com_max + player_max
        self.selected = random.randint(0, max)

    def draw(self, state, turn):
        super().draw()


class Selif(ObjectBase):
    def __init__(self):
        x = pyxel.width / 2
        super().__init__(x, 0, 0, 0)
        self.count = 0
        self.seno = 'せーの'
        self.seno_w = UMPLUS_J10R.text_width(self.seno) / 2

    def update(self):
        self.count += 1

    def draw(self, state: State, turn: Turn, selected: int, is_hit: bool):
        if state == State.PLAY:
            if UMPLUS_J10R is not None:
                self.draw_text_center(self.seno, pyxel.height / 2 + 5,
                                      pyxel.COLOR_WHITE, FNT_TYPE_JP)
        if state == State.RESULT:
            y = pyxel.height / 2 + 5
            self.draw_text_center(f'{selected}', y,
                                  pyxel.COLOR_WHITE, FNT_TYPE_JP)
            self.draw_text_center('Hit' if is_hit else 'Ummatch', y + 15,
                                  pyxel.COLOR_WHITE, FNT_TYPE_JP)
            


class App(ObjectBase):
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS, display_scale=2)
        pyxel.mouse(False)
        has_resource = self.ReadResources()
        if has_resource:
            self.DefineVariables()
            pyxel.run(self.update, self.draw)
        else:
            pyxel.run(self.err_update, self.err_draw)

    def ReadResources(self) -> bool:
        '''
        リソースファイルの読み込み
        '''
        if UMPLUS_J10R is None:
            return False
        return True

    def DefineVariables(self):
        '''
        内部変数初期化
        '''
        self.player = Player()
        self.com = Com()
        self.selif = Selif()
        self.state = State.TITLE
        self.turn = Turn.PLAYER
        self.is_hit = False

    def update(self):
        '''
        データ更新
        '''
        if self.state == State.TITLE:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.state = State.PLAY

        elif self.state == State.PLAY:
            self.player.update(self.turn)
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.state = State.JUDGE

        elif self.state == State.JUDGE:
            self.com.random_set(self.player)
            count = self.com.flag_count() + self.player.flag_count()
            if self.turn == Turn.PLAYER:
                self.is_hit = True if count == self.player.selected else False
            else:
                self.is_hit = True if count == self.com.selected else False
            self.state = State.RESULT
        
        elif self.state == State.RESULT:
            if pyxel.btnp(pyxel.KEY_RETURN):
                
                is_game_end = False
                if self.turn == Turn.PLAYER:
                    if self.is_hit:
                        is_game_end = self.player.unit_down()
                    self.turn = Turn.COM
                else:
                    if self.is_hit:
                        is_game_end = self.com.unit_down()
                    self.turn = Turn.PLAYER

                self.player.flag_clear()
                self.com.flag_clear()
                self.is_hit = False

                if is_game_end:
                    self.state = State.GAME_END
                else:
                    self.state = State.PLAY

        elif self.state == State.GAME_END:
            pass

    def draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_BLACK)

        if self.state == State.TITLE:
            txt = 'なまえわからんやつ'
            self.draw_text_center(txt, pyxel.height / 2 - 2,
                                  pyxel.COLOR_WHITE, FNT_TYPE_JP)
            txt = 'press space key'
            self.draw_text_center(txt, pyxel.height / 2 + 15,
                                  pyxel.COLOR_WHITE)
        else:
            selected = 0
            if self.turn == Turn.PLAYER:
                pyxel.text(1, 1, "player's turn", pyxel.COLOR_WHITE)
                selected = self.player.selected
            else:
                pyxel.text(1, 1, "com's turn", pyxel.COLOR_WHITE)
                selected = self.com.selected

            self.selif.draw(self.state, self.turn,
                            selected, self.is_hit)
            self.player.draw(self.turn)
            self.com.draw(self.state, self.turn)
            
            


App()
