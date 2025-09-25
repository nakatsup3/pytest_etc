import pyxel
import copy
from random import (shuffle, uniform)
from enum import Enum

# ウインドウ設定
WINDOW_HEIGHT = 256
WINDOW_WIDTH = 256
TITLE = 'ColorSort'
FPS = 60

# プログラムが等幅になるように定義名変更
RED = pyxel.COLOR_RED
GRN = pyxel.COLOR_GREEN
BLU = pyxel.COLOR_DARK_BLUE
PNK = pyxel.COLOR_PINK
YLW = pyxel.COLOR_YELLOW
ORG = pyxel.COLOR_ORANGE
BRW = pyxel.COLOR_LIGHT_BLUE
PPL = pyxel.COLOR_PURPLE
LIM = pyxel.COLOR_LIME

# セル数設定
CELL_NUM = 4
CELL_W = 10
CELL_H = 10

# UI 配置設定
MARGIN_X = 20
MARGIN_Y = 15
PEEK_Y = 40


class State(Enum):
    '''
    ゲーム状態遷移
    '''
    TITLE = 0
    INIT = 1
    PLAY_1 = 2
    PLAY_2 = 3
    JUDGE = 4
    ANIMATION = 5
    RESULT = 6
    GAME_END = 7


class AnimationState(Enum):
    '''
    セルの移動アニメーションの状態
    '''
    POP = 0
    MOVE = 1
    PUSH = 2


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


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Fragment:
    def __init__(self, x, y):
        self.x = x
        self.y = y
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
            pyxel.circ(self.x, self.y, 1, 7)
        else:
            self.is_complete = True


class Cell(ObjectBase):
    def __init__(self, x: float, y: float, color: int):
        super().__init__(x, y, CELL_W, CELL_H)
        self.broken = False
        self.fragments = []
        self.color = color
    
    def draw(self, x, y):
        pyxel.elli(self.x + x, self.y + y, self.w, self.h, self.color)


class Tube(ObjectBase):
    '''
    試験管クラス
    '''
    def __init__(self, x: float, y: float, index: int):
        super().__init__(x, y, CELL_W + 2, CELL_H * CELL_NUM + 2)
        self.index = index
        self.values = []
        self.clicked = False
        self.is_all_same = False
        self.hide = False

        # アニメーション用変数
        self.target_y = 0
        self.move_complete = False
        self.start_point = None
        self.end_point = None
        self.duration = 60
        self.timer = 0
        self.bx = 0
        self.by = 0
        self.mid_x = 0
        self.mid_y = 0

    def set_values(self, values: list):
        '''
        セルの値設定
        '''
        colors = copy.deepcopy(values)
        self.values.clear()

        for i in range(len(colors)):
            idx = (CELL_NUM - 1 - i)
            self.values.append(Cell(self.x + 1,
                                    self.y + CELL_H * idx + 1,
                                    colors[i]))

    def move_offset_clear(self):
        '''
        移動オフセットまとめてクリア
        '''
        self.target_y = 0
        self.move_complete = False
        self.start_point = None
        self.end_point = None
        self.timer = 0
        self.bx = 0
        self.by = 0
        self.mid_x = 0
        self.mid_y = 0

    def update(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            # 描画範囲内をクリックしているか
            if self.x < pyxel.mouse_x \
                    and pyxel.mouse_x < self.x + self.w \
                    and self.y < pyxel.mouse_y \
                    and pyxel.mouse_y < self.y + self.h:
                if self.clicked:
                    self.clicked = False
                else:
                    self.clicked = True

        if CELL_NUM <= len(self.values) or len(self.values) == 0:
            self.is_all_same = len(set(list(map(lambda t: t.color, self.values)))) <= 1
            if not self.is_all_same:
                self.hide = False
            else:
                if 0 < len(self.values):
                    self.hide = True
        else:
            self.is_all_same = False
            self.hide = False

    def set_pop_offset(self, deps: int):
        self.target_y = self.y - CELL_H * deps
        self.by = 0

    def set_push_offset(self, tube, count):
        offset = CELL_NUM - len(tube.values) - count
        self.target_y = tube.y + CELL_H * offset + 1

    def spawn_fragments(self):
        for _ in range(12):
            self.fragments.append(Fragment(self.x, self.y))

    def anime_update(self, state: AnimationState):
        '''
        アニメーション用の値更新
        '''
        if state == AnimationState.POP:
            # 上昇
            self.by -= 1
            if self.y + self.by <= self.target_y:
                self.move_complete = True

        elif state == AnimationState.MOVE:
            if not self.move_complete:
                t = self.timer / self.duration
                # 2次ベジェ補間で放物線移動
                ax = (1 - t)**2 * self.start_point.x + 2 * (1 - t) * t \
                    * self.mid_x + t**2 * self.end_point.x
                ay = (1 - t)**2 * self.start_point.y + 2 * (1 - t) * t \
                    * self.mid_y + t**2 * self.end_point.y

                # ベースの座標をもとに補正値を計算
                self.bx = ax - self.x - 1
                self.by = ay - self.y

                self.timer += 1
            if self.duration <= self.timer:
                self.move_complete = True
        else:
            self.by += 1
            if self.target_y < self.y + self.by:
                self.move_complete = True

    def cell_pos_reset(self):
        for i in range(len(self.values)):
            idx = (CELL_NUM - 1 - i)
            self.values[i].x = self.x + 1
            self.values[i].y = self.y + CELL_H * idx + 1

    def draw_cell(self, x, y, v: Cell):
        '''
        セルの描画
        '''
        v.draw(x, y)

    def draw(self, state: State, bits: int):
        if self.hide:
            return

        # 試験管っぽく描画
        pyxel.rect(self.x - 1, self.y - 1, self.w + 2,
                   CELL_H / 2, pyxel.COLOR_WHITE)
        pyxel.rect(self.x, self.y, self.w,
                   self.h - CELL_H / 2, pyxel.COLOR_WHITE)
        pyxel.elli(self.x, self.y + (CELL_NUM - 1) * CELL_H + 2,
                   self.w, CELL_H, pyxel.COLOR_WHITE)

        # セル描画
        for i in range(len(self.values)):
            if 0 < bits & (1 << i) and state == State.ANIMATION:
                self.draw_cell(self.bx, self.by, self.values[i])
            else:
                self.draw_cell(0, 0, self.values[i])

        # 選択肢任用の枠
        if self.clicked:
            pyxel.rectb(self.x - 1, self.y - 1,
                        self.w + 2, self.h + 2, pyxel.COLOR_RED)


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
        # 配色ベース
        self.base_nums = [[RED] * CELL_NUM, [GRN] * CELL_NUM, [BLU] * CELL_NUM,
                          [PNK] * CELL_NUM, [YLW] * CELL_NUM, [ORG] * CELL_NUM,
                          [BRW] * CELL_NUM, [PPL] * CELL_NUM, [LIM] * CELL_NUM]
        self.problem = []
        self.state = State.INIT
        self.select_pop = -1
        self.select_push = -1
        self.history = []

        # アニメーション用変数
        self.anime_sate = AnimationState.POP
        self.out_bits = 0b0
        self.in_bits = 0b0
        self.out_deps = 0

    def init(self):
        # 色のシャッフル初期化
        self.problem.clear()
        for b in self.base_nums:
            self.problem += b
        shuffle(self.problem)
        # 各チューブに色を配置
        self.color_set()
        # 操作履歴削除
        self.select_pop = -1
        self.select_push = -1
        self.history.clear()

    def color_set(self):
        max = 11
        self.tubes.clear()
        offset_x = 5
        cnt = 0
        y = pyxel.width / 2 - (CELL_H * CELL_NUM + 2) - MARGIN_Y

        for i in range(0, max):
            self.tubes.append(Tube(offset_x + cnt * MARGIN_X, y, i))
            cnt += 1
            if max / 2 < cnt:
                cnt = 0
                y = pyxel.height / 2 + MARGIN_Y
            if i < max - 2:
                cut_num = CELL_NUM * i
                self.tubes[i].set_values(
                    self.problem[cut_num:cut_num + CELL_NUM])

    def next_play(self):
        self.state = State.PLAY_1
        self.select_pop = -1
        self.select_push = -1
        self.out_bits = 0b0
        self.in_bits = 0b0

    def get_clicked(self):
        '''
        チューブのクリック状態取得
        '''
        flags = 0
        for i in range(len(self.tubes)):
            if self.tubes[i].clicked:
                flags = flags | (1 << i)
        return flags

    def get_stand_bit_index(self, bits: int) -> int:
        '''
        チューブのクリック状態をインデックスにして返す
        '''
        bit_length = bits.bit_length()
        for position in range(bit_length):
            if (bits & (1 << position)) != 0:
                return position
        return -1

    def get_move_values(self, values: list, limit: int) -> Cell:
        last_value = values[-1]
        count = 0
        rev_values = values[::-1]
        for i in range(len(values)):
            if limit == i:
                break
            if rev_values[i].color == last_value.color :
                count += 1
            else:
                break
        return values[-count:]

    def get_move_bits(self, values: list, moves: list) -> int:
        result = 0
        val_len = len(values) - 1
        for i in range(len(moves)):
            if values[val_len].color == moves[i].color:
                result = result | (1 << val_len)
            else:
                break
            val_len -= 1
        return result

    def get_space_bits(self, values: list):
        result = 0b0
        for i in range(CELL_NUM, 0, -1):
            if len(values) < i:
                result = result | (1 << i-1)
            else:
                break
        return result

    def get_bit_deps(self, bits: int):
        result = CELL_NUM
        for i in range(CELL_NUM):
            if 0 == bits & (1 << i):
                result -= 1
            else:
                return result
        return 0

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
            # ゲームクリア判定
            is_all = True
            for t in self.tubes:
                t.update()
                if not t.is_all_same:
                    is_all = False
            if is_all:
                self.state = State.GAME_END

            # 選択判定
            self.select_pop = self.get_stand_bit_index(self.get_clicked())
            if 0 <= self.select_pop:
                self.state = State.PLAY_2

        elif self.state == State.PLAY_2:
            for t in self.tubes:
                t.update()

            # 2つ目の選択判定
            bits = self.get_clicked()
            if bits.bit_count() < 1:
                # 一つ目の選択解除している
                self.next_play()
                return
            elif 2 <= bits.bit_count():
                # ２つ目を選択したので移動判定へ
                self.select_push = self.get_stand_bit_index(
                                    bits & ~(1 << self.select_pop))
                self.state = State.JUDGE

        elif self.state == State.JUDGE:
            # クリック解除
            for t in self.tubes:
                t.clicked = False
            # 移動できるか確認
            push_tube = self.tubes[self.select_push]
            in_space = CELL_NUM - len(push_tube.values)
            if in_space <= 0:
                # 入れる側に空き無し
                self.next_play()
                return
            pop_tube = self.tubes[self.select_pop]
            if len(pop_tube.values) < 1:
                # 取り出し側に値無
                self.next_play()
                return

            # 入れる側の色
            in_top = -1 if len(push_tube.values) < 1 \
                else push_tube.values[-1].color
            # 取り出し側の移動する値取得
            move_values = self.get_move_values(pop_tube.values, in_space)
            # self.anime_idx = move_values[0].color

            # 入れる側と取り出し側の色判定
            if in_top == -1 or move_values[0].color == in_top:
                out_len = -len(move_values)
                pop_tube.move_offset_clear()

                # 移動するセルと位置補正の設定
                self.out_bits = self.get_move_bits(pop_tube.values,
                                                   move_values)
                self.out_deps = self.get_bit_deps(self.out_bits)
                self.in_bits = self.get_space_bits(push_tube.values)
                pop_tube.set_pop_offset(self.out_deps)

                # 履歴作成
                self.history.append([self.select_pop,
                                     self.select_push,
                                     abs(out_len)])
                self.state = State.ANIMATION
            else:
                # 色が一致してない
                self.next_play()

        elif self.state == State.ANIMATION:
            pop_tube = self.tubes[self.select_pop]
            push_tube = self.tubes[self.select_push]
            # 位置更新
            if self.anime_sate == AnimationState.POP:
                pop_tube.anime_update(AnimationState.POP)
            elif self.anime_sate == AnimationState.MOVE:
                pop_tube.anime_update(AnimationState.MOVE)
            else:
                pop_tube.anime_update(AnimationState.PUSH)

            # 取り出し側のセルが画面外へ移動するまで待機

            if self.anime_sate == AnimationState.POP \
                    and pop_tube.move_complete:
                ps = Point(pop_tube.x + 1, pop_tube.target_y)
                pe = Point(push_tube.x + 1,
                           push_tube.y - self.out_deps * CELL_H - 5)
                pop_tube.move_offset_clear()

                pop_tube.start_point = ps
                pop_tube.end_point = pe
                pop_tube.mid_x = (ps.x + pe.x) / 2
                pop_tube.mid_y = min(ps.y, pe.y) - PEEK_Y
                push_tube.by = -self.out_deps * CELL_H # todo 調整

                self.anime_sate = AnimationState.MOVE

            if self.anime_sate == AnimationState.MOVE \
                    and pop_tube.move_complete:
                his = self.history[-1]
                pop_tube.set_push_offset(push_tube, his[2])
                
                pop_tube.move_complete = False
                self.anime_sate = AnimationState.PUSH

            # 入れ側 落ちて定位置に移動するまで待機
            if self.anime_sate == AnimationState.PUSH \
                    and pop_tube.move_complete:
                his = self.history[-1]
                moves = self.tubes[his[0]].values[-his[2]:]
                # 取り出し側からセルを除外
                self.tubes[his[0]].values \
                    = self.tubes[his[0]].values[:-his[2]]
                self.tubes[his[1]].values.extend(moves)
                pop_tube.move_offset_clear()
                push_tube.cell_pos_reset()
                self.anime_sate = AnimationState.POP
                self.next_play()

        elif self.state == State.GAME_END:
            # キー操作待ち
            pass

        if self.state == State.ANIMATION:
            # アニメーション中はキー操作不可
            return

        # キー操作受付
        if self.state != State.TITLE:
            if pyxel.btnp(pyxel.KEY_R):  # 新しいゲームを始める
                self.state = State.INIT
            if pyxel.btnp(pyxel.KEY_S):  # ゲームの初めから
                self.color_set()
                self.history.clear()
                self.next_play()

            if pyxel.btnp(pyxel.KEY_U):  # １手戻す
                if 0 < len(self.history):
                    his = self.history.pop()
                    undo_out = his[0]
                    undo_in = his[1]
                    cnt = his[2]
                    moves = self.tubes[undo_in].values[-cnt:]
                    self.tubes[undo_in].values \
                        = self.tubes[undo_in].values[:-cnt]
                    self.tubes[undo_out].values.extend(moves)
                    self.tubes[undo_out].cell_pos_reset()

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
                if i != self.select_pop and i != self.select_push:
                    self.tubes[i].draw(self.state, 0)
                if 0 <= self.select_push:
                    self.tubes[self.select_push].draw(self.state, self.in_bits)
                if 0 <= self.select_pop:
                    self.tubes[self.select_pop].draw(self.state, self.out_bits)

            if self.state == State.GAME_END:
                pyxel.text(pyxel.width / 2, pyxel.height / 2,
                           'GameClear', pyxel.COLOR_WHITE)


App()
