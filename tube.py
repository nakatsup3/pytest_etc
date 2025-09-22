import pyxel
import copy
from random import shuffle
from enum import Enum

# ウインドウ設定
WINDOW_HEIGHT = 128
WINDOW_WIDTH = 128
TITLE = 'ColorSort'
FPS = 60

RED = pyxel.COLOR_RED
GRN = pyxel.COLOR_GREEN
BLU = pyxel.COLOR_DARK_BLUE
PNK = pyxel.COLOR_PINK
YLW = pyxel.COLOR_YELLOW
ORG = pyxel.COLOR_ORANGE
BRW = pyxel.COLOR_LIGHT_BLUE
PPL = pyxel.COLOR_PURPLE
LIM = pyxel.COLOR_LIME

CELL_NUM = 4


class State(Enum):
    '''
    ゲーム状態遷移
    '''
    TITLE = 0
    INIT = 1
    PLAY_1 = 2
    PLAY_2 = 3
    JUDGE = 4
    RESULT = 5
    GAME_END = 6


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


class Tube(ObjectBase):
    def __init__(self, x: float, y: float, index: int):
        super().__init__(x, y, 12, 10 * CELL_NUM + 2)
        self.index = index
        self.values = []
        self.clicked = False
        self.is_all_same = False

    def update(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.x < pyxel.mouse_x \
                    and pyxel.mouse_x < self.x + self.w \
                    and self.y < pyxel.mouse_y \
                    and pyxel.mouse_y < self.y + self.h:
                if self.clicked:
                    self.clicked = False
                else:
                    self.clicked = True
        if CELL_NUM <= len(self.values) or len(self.values) == 0:
            self.is_all_same = len(set(self.values)) <= 1
        else:
            self.is_all_same = False

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, pyxel.COLOR_WHITE)
        i = 0
        for v in self.values:
            pyxel.rect(self.x + 1, self.y + (CELL_NUM - 1 - i) * 10 + 1,
                       10, 10, v)
            i += 1
        if self.clicked:
            pyxel.rectb(self.x - 1, self.y - 1,
                        self.w + 2, self.h + 2, pyxel.COLOR_RED)

    def set_values(self, values: list):
        self.values = copy.deepcopy(values)


class App(ObjectBase):
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS, display_scale=2)
        pyxel.mouse(True)
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
        return True

    def DefineVariables(self):
        '''
        内部変数初期化
        '''
        self.tubes = []
        self.base_nums = [[RED] * CELL_NUM, [GRN] * CELL_NUM, [BLU] * CELL_NUM,
                          [PNK] * CELL_NUM, [YLW] * CELL_NUM, [ORG] * CELL_NUM,
                          [BRW] * CELL_NUM, [PPL] * CELL_NUM, [LIM] * CELL_NUM]
        self.problem = []
        self.state = State.INIT
        self.select_out = -1
        self.select_in = -1
        self.history = []

    def init(self):
        # 色のシャッフル初期化
        self.problem.clear()
        for b in self.base_nums:
            self.problem += b
        shuffle(self.problem)
        # 各チューブに色を配置
        self.color_set()
        # 操作履歴削除
        self.select_out = 0
        self.select_in = 0
        self.history.clear()

    def color_set(self):
        max = 11
        self.tubes.clear()
        offset_x = 5
        cnt = 0
        y = pyxel.width / 2 - (10 * CELL_NUM + 2) - 5

        for i in range(0, max):
            self.tubes.append(Tube(offset_x + cnt * 15, y, i))
            cnt += 1
            if max / 2 < cnt:
                cnt = 0
                y = pyxel.height / 2 + 5
            if i < max - 2:
                cut_num = CELL_NUM * i
                self.tubes[i].set_values(
                    self.problem[cut_num:cut_num + CELL_NUM])

    def is_clicked(self):
        flags = 0
        for i in range(len(self.tubes)):
            if self.tubes[i].clicked:
                flags = flags | (1 << i)
        return flags

    def is_bit_set(self, number, position):
        # 指定した位置のビットが立っているか確認
        return (number & (1 << position)) != 0

    def find_stand_bit(self, bits: int) -> int:
        bit_length = bits.bit_length()
        for position in range(bit_length):
            if self.is_bit_set(bits, position):
                return position
        return -1

    def get_move_values(self, values: list):
        last_value = values[-1]
        count = 0

        for i in reversed(values):
            if i == last_value:
                count += 1
            else:
                break
        return values[-count:]

    def update(self):
        '''
        データ更新
        '''
        if self.state == State.TITLE:
            pass

        elif self.state == State.INIT:
            self.init()
            self.state = State.PLAY_1

        elif self.state == State.PLAY_1:
            is_all = True
            for t in self.tubes:
                t.update()
                if not t.is_all_same:
                    is_all = False
            if is_all:
                self.state = State.GAME_END
            self.select_out = self.find_stand_bit(self.is_clicked())
            if 0 <= self.select_out:
                self.state = State.PLAY_2

        elif self.state == State.PLAY_2:
            for t in self.tubes:
                t.update()
            bits = self.is_clicked()
            if bits.bit_count() < 1:
                self.state = State.PLAY_1
            elif 2 <= bits.bit_count():
                self.select_in = self.find_stand_bit(
                                    bits & ~(1 << self.select_out))
                self.state = State.JUDGE

        elif self.state == State.JUDGE:
            for t in self.tubes:
                t.clicked = False
            in_idx = self.select_in
            if CELL_NUM <= len(self.tubes[in_idx].values):
                # 入れる側に空き無し
                self.state = State.PLAY_1
                return
            out_idx = self.select_out
            if len(self.tubes[out_idx].values) < 1:
                # 取り出し側に値無
                self.state = State.PLAY_1
                return

            move_values = self.get_move_values(self.tubes[out_idx].values)
            in_top = -1 if len(self.tubes[in_idx].values) < 1 \
                else self.tubes[in_idx].values[-1]
            if in_top == -1 or move_values[0] == in_top:
                out_len = -len(move_values)
                self.tubes[out_idx].values \
                    = self.tubes[out_idx].values[:out_len]
                self.tubes[in_idx].values.extend(move_values)
                self.history.append([out_idx, in_idx, out_len * -1])
            self.state = State.PLAY_1
        elif self.state == State.GAME_END:
            pass

        if self.state != State.TITLE:
            if pyxel.btnp(pyxel.KEY_R):
                self.state = State.INIT
            if pyxel.btnp(pyxel.KEY_S):
                self.select_out = 0
                self.select_in = 0
                self.color_set()
                self.history.clear()
                self.state = State.PLAY_1
            if pyxel.btnp(pyxel.KEY_U):
                if 0 < len(self.history):
                    his = self.history.pop()
                    undo_out = his[0]
                    undo_in = his[1]
                    cnt = his[2]
                    moves = self.tubes[undo_in].values[-cnt:]
                    self.tubes[undo_in].values \
                        = self.tubes[undo_in].values[:-cnt]
                    self.tubes[undo_out].values.extend(moves)

    def draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_BLACK)

        if self.state == State.TITLE:
            pass
        else:
            pyxel.text(5, 5, 'R: restart, S: reset, U: undo',
                       pyxel.COLOR_WHITE)
            pyxel.text(5, pyxel.height - 10,
                       f'move count: {len(self.history)}', pyxel.COLOR_WHITE)
            for i in range(0, len(self.tubes)):
                self.tubes[i].draw()
            
            if self.state == State.GAME_END:
                pyxel.text(pyxel.width / 2,
                           pyxel.height / 2,
                           'GameClear',
                           pyxel.COLOR_WHITE)


App()
