import pyxel
from math import sqrt
from copy import deepcopy

# ウインドウ設定
WINDOW_HEIGHT = 128
WINDOW_WIDTH = 200
TITLE = 'MasterMind'
FPS = 60

BALL_SIZE = 10
JUDGE_SIZE = 6
MISS = 1
SUCCESS = 2
TOP = 35
ANSWER_COUNT = 4

# 使用する玉の配色
COLS = [pyxel.COLOR_RED, pyxel.COLOR_DARK_BLUE, pyxel.COLOR_GREEN,
        pyxel.COLOR_CYAN, pyxel.COLOR_PINK, pyxel.COLOR_YELLOW,
        pyxel.COLOR_WHITE]


class ObjBase:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def isMouseOver(self):
        '''
        オブジェクト上にマウスがあるか？
        '''
        if self.x < pyxel.mouse_x \
                and pyxel.mouse_x < self.x + self.w \
                and self.y < pyxel.mouse_y \
                and pyxel.mouse_y < self.y + self.h:
            return True
        return False


def isHit(obj_a: ObjBase, obj_b: ObjBase) -> bool:
    '''
    オブジェクト(丸)同士の当たり判定
    '''
    # 中心点
    x = obj_a.x + BALL_SIZE / 2
    y = obj_a.y + BALL_SIZE / 2
    tx = obj_b.x + BALL_SIZE / 2
    ty = obj_b.y + BALL_SIZE / 2
    # 半径
    r = obj_a.h / 2 + obj_b.h / 2
    # 距離
    xl = abs(x - tx)
    a = xl * xl
    yl = abs(y - ty)
    b = yl * yl
    c = sqrt(a + b)

    if c < r:
        return True, c
    return False, c


class Hole(ObjBase):
    def __init__(self, x, y, w=BALL_SIZE, h=BALL_SIZE):
        super().__init__(x, y, w, h)
        self.col = pyxel.COLOR_BLACK
        self.is_fill = False

    def update(self):
        '''
        クリックで塗りつぶし解除
        '''
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.isMouseOver():
                self.col = pyxel.COLOR_BLACK
                self.is_fill = False

    def FillInHole(self, col: int):
        '''
        塗りつぶし設定
        '''
        self.col = col
        self.is_fill = True

    def draw(self):
        '''
        穴の描画
        '''
        if self.is_fill:
            pyxel.elli(self.x, self.y, self.w, self.h, self.col)
        else:
            pyxel.ellib(self.x, self.y, self.w, self.h, pyxel.COLOR_BLACK)


class Ball(ObjBase):
    def __init__(self, x, y, w=BALL_SIZE, h=BALL_SIZE, col=pyxel.COLOR_WHITE):
        super().__init__(x, y, w, h)
        self.col = col
        self.base_x = x
        self.base_y = y

    def Reset(self):
        '''
        定位置へ戻す
        '''
        self.x = self.base_x
        self.y = self.base_y

    def update(self):
        '''
        マウス追従
        '''
        self.x = pyxel.mouse_x - BALL_SIZE / 2
        self.y = pyxel.mouse_y - BALL_SIZE / 2

    def draw(self):
        '''
        玉描画
        '''
        pyxel.elli(self.x, self.y, self.w, self.h, self.col)


class Button(ObjBase):
    def __init__(self, x: float, y: float,
                 fst: str, scd: str = None):
        w = len(fst) * 4 + 5
        super().__init__(x, y, w, 10)
        self.is_mouse_click = False
        self.first_txt = fst
        if scd is None:
            self.second_txt = fst
        else:
            self.second_txt = scd

    def update(self):
        '''
        ボタン押下
        '''
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.isMouseOver():
                self.is_mouse_click = True

    def draw(self):
        '''
        ボタン描画
        '''
        if self.is_mouse_click:
            # クリックした後
            pyxel.rect(self.x, self.y,
                       self.w, self.h, pyxel.COLOR_BROWN)
            pyxel.text(self.x + 2.5, self.y + 2, self.second_txt,
                       pyxel.COLOR_WHITE)
        else:
            # クリックする前
            pyxel.rect(self.x, self.y,
                       self.w, self.h, pyxel.COLOR_RED)
            pyxel.text(self.x + 2.5, self.y + 2, self.first_txt,
                       pyxel.COLOR_WHITE)


class SetPlace(ObjBase):
    def __init__(self, x, y):
        super().__init__(x, y, 16, 53)
        self.holes = []
        for r in range(4):
            self.holes.append(Hole(self.x + 3,
                                   self.y + 3 + r * 10 + r * 2))
        self.button = Button(self.x, self.y + self.h,
                             'OK?', 'chk')

        # ヒットアンドブローの表示
        self.ansewers = [0, 0, 0, 0]
        self.judge_holes = []
        self.judge_holes.append(Hole(self.x + 2,
                                self.y - (JUDGE_SIZE * 2),
                                JUDGE_SIZE, JUDGE_SIZE))
        self.judge_holes.append(Hole(self.x + JUDGE_SIZE + 2,
                                self.y - (JUDGE_SIZE * 2),
                                JUDGE_SIZE, JUDGE_SIZE))
        self.judge_holes.append(Hole(self.x + 2,
                                self.y - JUDGE_SIZE,
                                JUDGE_SIZE, JUDGE_SIZE))
        self.judge_holes.append(Hole(self.x + JUDGE_SIZE + 2,
                                self.y - JUDGE_SIZE,
                                JUDGE_SIZE, JUDGE_SIZE))

    def update(self, balls: list[Ball]) -> int:
        for h in self.holes:
            h.update()

        # ヒットアンドブローチェック
        self.button.update()
        if self.button.is_mouse_click:
            results = self.judge(balls)
            sum = 0
            for r in range(len(results)):
                if results[r] != 0:
                    if results[r] == pyxel.COLOR_RED:
                        sum += 1
                    self.judge_holes[r].FillInHole(results[r])
            if 4 <= sum:
                return SUCCESS
            return MISS
        return 0

    def draw(self):
        for b in self.holes:
            b.draw()
        self.button.draw()

        # チェック
        for j in self.judge_holes:
            j.draw()

    def IsHoleIn(self, ball: Ball):
        '''
        ドラッグアンドドロップで玉の色を穴に設定する
        '''
        i = 0
        calc = []
        for h in self.holes:
            bl, val = isHit(ball, h)
            calc.append((bl, val, i))
            i += 1
        if 0 < len(calc):
            # 一番近いほうへ適用する
            srt = sorted(calc, key=lambda x: x[1])
            ret, _, idx = srt[0]
            if ret:
                self.holes[idx].FillInHole(ball.col)

    def judge(self, balls: list[Ball]) -> list[int]:
        '''
        ヒット数、ブロー数のカウント
        '''
        b_tmp = deepcopy(balls)
        h_tmp = deepcopy(self.holes)
        result = []
        for i in range(ANSWER_COUNT):
            if h_tmp[i].col == b_tmp[i].col:
                b_tmp[i].col = -1
                h_tmp[i].col = -1
                result.append(pyxel.COLOR_RED)
        # 正解
        if len(result) == ANSWER_COUNT:
            return result
        # マッチしたやつ除外
        tmp = []
        while h_tmp:
            h = h_tmp.pop()
            if 0 <= h.col:
                tmp.append(h)
        # 色一致(ブロー)を捜査
        for th in tmp:
            for i in range(ANSWER_COUNT):
                if th.col == b_tmp[i].col:
                    b_tmp[i].col = -1
                    result.append(pyxel.COLOR_WHITE)
                    break
        # 不正解
        return result


class MasterPlace(ObjBase):
    def __init__(self, x, y):
        super().__init__(x, y, 16, 53)
        self.balls = []
        bc_list = []
        for clr in COLS:
            bc_list.append((clr, pyxel.rndf(0.0, 1.0)))
        srt = sorted(bc_list, key=lambda x: x[1])
        for r in range(ANSWER_COUNT):
            self.balls.append(Ball(self.x + 3,
                                   self.y + 3 + r * 10 + r * 2,
                                   col=srt[r][0]))
        self.is_open = False

    def update(self, resiut: int, play_count: int):
        '''
        正解の玉の表示・非表示切り替え
        '''
        if pyxel.btnp(pyxel.KEY_D):
            self.is_open = not self.is_open
        if SUCCESS == resiut or 8 <= play_count:
            self.is_open = True

    def draw(self):
        '''
        正解の描画
        '''
        if self.is_open:
            for b in self.balls:
                b.draw()
        else:
            pyxel.rect(self.x, self.y, self.w, self.h, 0)


class App:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS, display_scale=1)
        pyxel.mouse(True)
        self.init()
        pyxel.run(self.update, self.draw)

    def init(self):
        '''
        ゲーム内部変数初期化
        '''
        self.balls = []
        for i in range(len(COLS)):
            self.balls.append(Ball(5 + i * BALL_SIZE + i * 1, 5, col=COLS[i]))
        self.drag_idx = -1

        self.set_area = SetPlace(5, TOP)
        self.played_area = []
        self.master = MasterPlace(pyxel.width - 19, TOP)
        self.reset_btn = Button(2, pyxel.height - 12, 'reset')
        self.play_count = 0

    def update(self):
        '''
        データ更新
        '''
        # 玉をつかんで移動
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for i in range(len(self.balls)):
                if self.balls[i].isMouseOver():
                    self.drag_idx = i
                    break
        elif pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            if 0 <= self.drag_idx:
                self.balls[self.drag_idx].update()

        # 玉を離す
        elif pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            if 0 <= self.drag_idx:
                self.set_area.IsHoleIn(self.balls[self.drag_idx])
                self.balls[self.drag_idx].Reset()
            self.drag_idx = -1

        # ヒットアンドブロー判定
        ret = self.set_area.update(self.master.balls)
        if ret == MISS and self.play_count < 7:
            self.played_area.append(self.set_area)
            self.set_area = SetPlace(
                self.set_area.x + self.set_area.w + 2,
                self.set_area.y)
        if ret == MISS or ret == SUCCESS:
            self.play_count += 1
        self.master.update(ret, self.play_count)

        # もう一度遊ぶためのリセットボタン
        self.reset_btn.update()
        if self.reset_btn.is_mouse_click:
            self.reset_btn.is_mouse_click = False
            self.master = MasterPlace(pyxel.width - 19, TOP)
            self.played_area.clear()
            self.set_area = SetPlace(5, TOP)
            self.play_count = 0

    def draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_GRAY)
        for p in self.played_area:
            p.draw()
        self.set_area.draw()

        # 操作
        for i in range(len(self.balls)):
            self.balls[i].draw()
            pyxel.ellib(5 + i * BALL_SIZE + i * 1, 5,
                        BALL_SIZE, BALL_SIZE, COLS[i])

        self.master.draw()
        self.reset_btn.draw()


App()
