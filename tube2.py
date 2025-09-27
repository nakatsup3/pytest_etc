import pyxel
import copy
import math
from random import (shuffle, uniform)
from enum import Enum

# ウインドウ設定
WINDOW_HEIGHT = 256
WINDOW_WIDTH = 256
TITLE = 'ColorSort'
FPS = 60

# 最大9色の設定
C01 = pyxel.COLOR_RED
C02 = pyxel.COLOR_GREEN
C03 = pyxel.COLOR_DARK_BLUE
C04 = pyxel.COLOR_PINK
C05 = pyxel.COLOR_YELLOW
C06 = pyxel.COLOR_ORANGE
C07 = pyxel.COLOR_LIGHT_BLUE
C08 = pyxel.COLOR_PURPLE
C09 = pyxel.COLOR_LIME

# セル数設定
CELL_NUM = 4
CELL_W = 10
CELL_H = 10
PEEK_Y = 40

# チューブ設定
COLOR_NUM = 9
TUBE_NUM = 11
START_Y = 60
MARGIN_X = 20
MARGIN_Y = 50


class State(Enum):
    '''
    ゲーム状態遷移
    '''
    TITLE = 0
    INIT = 1
    POP = 2
    POP_MOVE = 3
    PUSH_SELECT = 4
    PUSH_JUDGE = 5
    PUSH_MOVE = 6
    RESULT = 7
    GAME_END = 8


class ObjectBase:
    def __init__(self, x: float, y: float, w: float, h: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Fragment(ObjectBase):
    def __init__(self, x, y):
        super().__init__(x, y, 1, 0)
        self.vx = uniform(-2, 2)
        self.vy = uniform(-2, 2)
        self.life = 30  # 破片の寿命
        self.is_complete = False

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self):
        if self.is_complete:
            return
        if 0 < self.life:
            pyxel.circ(self.x, self.y, self.w, pyxel.COLOR_WHITE)
        else:
            self.is_complete = True


class Cell(ObjectBase):
    def __init__(self, x: float, y: float, color: int):
        super().__init__(x, y, CELL_W, CELL_H)
        self.broken = False
        self.fragments = []
        self.color = color
    
    def update(self):
        pass
    
    def draw(self):
        pyxel.elli(self.x, self.y, self.w, self.h, self.color)


class Tube(ObjectBase):
    '''
    試験管クラス
    '''
    def __init__(self, x: float, y: float):
        super().__init__(x, y, CELL_W + 2, CELL_H * CELL_NUM + 2)
        self.values = []
        self.clicked = False
        self.is_all_same = False
        self.pop_limit = self.y - CELL_H * CELL_NUM - 2
        self.move_complete = False
        
        # self.sp = None
        self.ep = None
        self.mp = None
        self.duration = 60
        self.timer = 0
        # self.bx = 0
        # self.by = 0
        self.mid_x = 0
        self.mid_y = 0

    def get_cell_pos(self, i) -> Point:
        idx = (CELL_NUM - 1 - i)
        return Point(self.x, self.y + CELL_H * idx + 1)

    def set_values(self, values: list):
        '''
        セルの値設定
        '''
        colors = copy.deepcopy(values)
        self.values.clear()

        for i in range(len(colors)):
            p = self.get_cell_pos(i)
            self.values.append(Cell(p.x, p.y, colors[i]))

    def get_move_bits(self) -> int:
        move_color = self.get_last_color()
        result = 0
        val_len = len(self.values) - 1
        for _ in range(len(self.values)):
            if self.values[val_len].color == move_color:
                result = result | (1 << val_len)
            else:
                break
            val_len -= 1
        return result

    def get_last_color(self):
        if 0 < len(self.values):
            return self.values[-1].color
        return -1

    def cell_pos_reset(self):
        for i in range(len(self.values)):
            p = self.get_cell_pos(i)
            self.values[i].x = p.x
            self.values[i].y = p.y

    def is_empty(self):
        return len(self.values) <= 0

    def is_full(self):
        return CELL_NUM <= len(self.values)

    def calc_bejie(self, sp, ep, mp, t):
        # 2次ベジェ補間で放物線移動
        ax = (1 - t)**2 * sp.x + 2 * (1 - t) * t * mp.x + t**2 * ep.x
        ay = (1 - t)**2 * sp.y + 2 * (1 - t) * t * mp.y + t**2 * ep.y
        return ax, ay

    def update(self, state: State, bits: int):
        val_len = len(self.values)
        
        if CELL_NUM <= val_len or val_len == 0:
            self.is_all_same = len(set(list(map(lambda t: t.color, self.values)))) <= 1

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            # 描画範囲内をクリックしているか
            if (self.x <= pyxel.mouse_x <= self.x + self.w) \
                    and (self.y <= pyxel.mouse_y <= self.y + self.h):
                if self.clicked:
                    self.clicked = False
                else:
                    self.clicked = True

        if state == State.POP_MOVE:
            num = bits.bit_count()
            pos_cnt = num - 1
            offset = self.pop_limit + CELL_H * (CELL_NUM - num)
            move_cnt = 0
            for i in range(val_len):
                if 0 < bits & (1 << i):
                    if offset + pos_cnt * CELL_H < self.values[i].y:
                        self.values[i].y -= 1
                    else:
                        move_cnt += 1
                    pos_cnt -= 1
                if move_cnt == num:
                    self.move_complete = True

        if state == State.PUSH_MOVE:
            if not self.move_complete:
                t = self.timer / self.duration
                for i in range(val_len):
                    if 0 < bits & (1 << i):
                        x, y = self.calc_bejie(Point(self.values[i].x, self.values[i].y),
                                               self.ep)
                        self.values[i].x = 0
                        self.values[i].y = 0

    def draw(self):

        # 試験管っぽく描画
        pyxel.rect(self.x - 2, self.y - 1, self.w + 2,
                   CELL_H / 2, pyxel.COLOR_WHITE)
        pyxel.rect(self.x - 1, self.y, self.w,
                   self.h - CELL_H / 2, pyxel.COLOR_WHITE)
        pyxel.elli(self.x - 1, self.y + (CELL_NUM - 1) * CELL_H + 1,
                   self.w, CELL_H + 1, pyxel.COLOR_WHITE)

        # セル描画
        for i in range(len(self.values)):
            self.values[i].draw()


class App:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS, display_scale=2)
        pyxel.mouse(True)
        self.DefineVariables()
        pyxel.run(self.update, self.draw)

    def DefineVariables(self):
        '''
        内部変数初期化
        '''
        self.tubes = []
        # 配色ベース
        self.base_nums = [[C01] * CELL_NUM, [C02] * CELL_NUM, [C03] * CELL_NUM,
                          [C04] * CELL_NUM, [C05] * CELL_NUM, [C06] * CELL_NUM,
                          [C07] * CELL_NUM, [C08] * CELL_NUM, [C09] * CELL_NUM]
        self.problem = []
        self.state = State.INIT
        self.pop_idx = -1
        self.pop_bits = 0b0
        self.push_idx = -1
        self.push_bits = 0b0

        self.history = []


    def init(self):
        # 色のシャッフル初期化
        self.problem.clear()
        for b in self.base_nums:
            self.problem += b
        shuffle(self.problem)
        # 各チューブに色を配置
        self.color_set(self.tubes, self.problem)

    def color_set(self, tubes: list, problem: list):
        '''
        チューブに色を設定する
        '''
        tubes.clear()
        half_cnt = math.ceil(TUBE_NUM / 2)
        offset_x = pyxel.width / 2 - ((half_cnt / 2) * (CELL_W + MARGIN_X))
        cnt = -1
        y = START_Y

        for i in range(TUBE_NUM):
            cnt += 1
            if half_cnt <= cnt:  # 折り返し
                cnt = 0
                y = START_Y + CELL_H * CELL_NUM + MARGIN_Y

            tubes.append(Tube(offset_x + cnt * MARGIN_X, y))

            if i < COLOR_NUM:  # 色を入れる
                st = CELL_NUM * i
                ed = st + CELL_NUM
                tubes[i].set_values(problem[st:ed])

    def click_reset(self):
        for t in self.tubes:
            t.clicked = False
            t.move_complete = False

    def mask_from_msb(self, value, total_bits, keep_bits):
        shift = total_bits - keep_bits
        mask = ((1 << keep_bits) - 1) << shift
        return value & mask

    def update(self):
        if self.state == State.TITLE:
            pass

        elif self.state == State.INIT:
            self.init()
            self.state = State.POP

        elif self.state == State.POP:
            self.pop_idx = -1
            for i in range(len(self.tubes)):
                self.tubes[i].update(self.state, 0)
                if self.tubes[i].clicked:
                    if self.tubes[i].is_empty():
                        self.tubes[i].clicked = False
                    else:
                        self.pop_idx = i

            if 0 <= self.pop_idx:
                self.pop_bits = self.tubes[self.pop_idx].get_move_bits()
                self.state = State.POP_MOVE

        elif self.state == State.POP_MOVE:
            self.tubes[self.pop_idx].update(self.state, self.pop_bits)
            if self.tubes[self.pop_idx].move_complete:
                self.state = State.PUSH_SELECT

        elif self.state == State.PUSH_SELECT:
            self.push_idx = -1
            for i in range(len(self.tubes)):
                self.tubes[i].update(self.state, 0)
                if i == self.pop_idx:
                    if not self.tubes[i].clicked:
                        self.tubes[i].cell_pos_reset()
                        self.click_reset()
                        self.state = State.POP
                        return
                    continue
                if self.tubes[i].clicked:
                    if not self.tubes[i].is_full():
                        self.push_idx = i

            if 0 <= self.push_idx and 0 <= self.pop_idx:
                self.click_reset()
                pop_last = self.tubes[self.pop_idx].get_last_color()
                push_last = self.tubes[self.push_idx].get_last_color()
                if pop_last == push_last \
                        or self.tubes[self.push_idx].is_empty():
                    space = CELL_NUM - len(self.tubes[self.push_idx].values)
                    self.pop_bits = self.mask_from_msb(self.pop_bits, CELL_NUM, space)
                    pop_num = self.pop_bits.bit_count()
                    
                    ep = Point(self.tubes[self.push_idx].x,
                               self.tubes[self.push_idx].y - pop_num * CELL_H - 2)
                    self.tubes[self.pop_idx].ep = ep
                    self.state = State.PUSH_MOVE
                else:
                    self.tubes[self.pop_idx].cell_pos_reset()
                    self.click_reset()
                    self.state = State.POP

        elif self.state == State.PUSH_MOVE:
            self.tubes[self.pop_idx].update(self.state, self.pop_bits)


            
            

        # キー操作受付
        if self.state != State.TITLE:
            if pyxel.btnp(pyxel.KEY_R):  # 新しいゲームを始める
                self.state = State.INIT

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)

        if self.state == State.TITLE:
            pass
        else:
            for i in range(len(self.tubes)):
                self.tubes[i].draw()


App()
