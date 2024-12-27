import pyxel
from math import sin
from math import cos
from math import pi as PI
import random
from enum import Enum


class State(Enum):
    Stop = 1
    Playing = 2


class App():

    MAX_SPEED = 5
    MIN_SPEED = 1
    BAR_WIDTH = 2

    def __init__(self):
        pyxel.init(256, 256, title="BallPongPong", fps=60)
        self.init()
        pyxel.run(self.update, self.draw)

    def init(self):
        '''
        内部変数初期化
        '''
        random.seed()
        # 日本語対応フォント
        self.umplus10 = pyxel.Font("assets/umplus_j10r.bdf")

        self.game_satate = State.Stop   # ボール制動
        self.speed = 2                  # 移動速度
        self.h = 10                     # 高さ
        self.w = 10                     # 幅
        self.theta = 0                  # 移動方向
        x, y = self.BallCenterPos()     # 初期位置 中央
        self.x = x
        self.y = y

        # プレイヤー得点
        self.l_point = 0
        self.r_point = 0
        # プレイヤー位置・大きさ
        self.l_bar_h = 20
        self.l_bar_y = pyxel.height / 2 - self.l_bar_h / 2
        self.l_speed = 1
        self.r_bar_h = 20
        self.r_bar_y = pyxel.height / 2 - self.r_bar_h / 2
        self.r_speed = 1

    def update(self):
        '''
        入力受付・内部変数更新
        '''
        if self.game_satate == State.Playing:
            # ユーザ操作受け付け
            self.PlayerInput()
            # 移動先座標計算
            x, y = self.NextLocation(self.theta, self.speed)
            # 当たり判定　+ 反射角更新
            px, py, th = self.WallHitDetection(
                            self.x + x, self.y + y, self.theta)
            # 位置更新
            self.x = px
            self.y = py
            self.theta = th

        # ボールストップ/スタート
        if self.game_satate == State.Stop:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.game_satate = State.Playing
                # 移動方向はランダム
                self.x, self.y = self.BallCenterPos()
                self.theta = random.randrange(360)

    def draw(self):
        '''
        画面描画更新
        '''
        # 背景
        pyxel.cls(pyxel.COLOR_BLACK)

        # 得点エリア
        pyxel.rect(0, 0, 2, pyxel.height, pyxel.COLOR_YELLOW)
        pyxel.rect(pyxel.width - 2, 0, 2, pyxel.height, pyxel.COLOR_YELLOW)

        # 操作メッセージ
        y = pyxel.height / 2
        if self.game_satate == State.Stop:
            self.DrawMsgCenter('start: space', y)
        else:
            self.DrawMsgCenter('stop: space', y)
        self.DrawMsgCenter('exit: esc', y + 10)
        self.DrawMsgCenter(f'{self.l_point:02}-{self.r_point:02}', 5)

        # ボール
        pyxel.elli(self.x, self.y, self.w, self.h, pyxel.COLOR_WHITE)

        # バー
        # pyxel.rect(0, self.l_bar_y - 1,
        #            self.BAR_WIDTH + 1, self.l_bar_h + 2, pyxel.COLOR_GRAY)
        # pyxel.rect(0, self.l_bar_y,
        #            self.BAR_WIDTH, self.l_bar_h, pyxel.COLOR_WHITE)
        r = self.l_bar_h / 2
        pyxel.elli(0, self.l_bar_y - r / 2,
                   r, r, pyxel.COLOR_WHITE)
        pyxel.elli(0, self.l_bar_y + r / 2,
                   r, r, pyxel.COLOR_WHITE)

        pyxel.rect(pyxel.width - (self.BAR_WIDTH + 1), self.r_bar_y - 1,
                   self.BAR_WIDTH + 1, self.r_bar_h + 2, pyxel.COLOR_GRAY)
        pyxel.rect(pyxel.width - self.BAR_WIDTH, self.r_bar_y,
                   self.BAR_WIDTH, self.r_bar_h, pyxel.COLOR_WHITE)

    def PlayerInput(self):
        '''
        プレイヤー操作 バー移動
        '''
        # 左側操作
        if pyxel.btn(pyxel.KEY_Q):
            self.l_bar_y = max(self.l_bar_y - self.l_speed, 1)
        if pyxel.btn(pyxel.KEY_A):
            lh = self.l_bar_y + self.l_bar_h + self.l_speed
            if lh < pyxel.height:
                self.l_bar_y += self.l_speed
        # 右側操作
        if pyxel.btn(pyxel.KEY_UP):
            self.r_bar_y = max(self.r_bar_y - self.r_speed, 1)
        if pyxel.btn(pyxel.KEY_DOWN):
            rh = self.r_bar_y + self.r_bar_h + self.r_speed
            if rh < pyxel.height:
                self.r_bar_y += self.r_speed

    def BallCenterPos(self):
        '''
        ボール中央位置
        '''
        x = pyxel.width / 2 - self.w / 2
        y = pyxel.height / 2 - self.h / 2
        return x, y

    def WallHitDetection(self, px: float, py: float, th: float):
        '''
        画面端当たり判定
        '''
        # 左端 プレイヤーレシーブ
        if px < self.BAR_WIDTH and (self.l_bar_y < py + self.h
                                    and py < self.l_bar_y + self.l_bar_h):
            px = self.BAR_WIDTH
            if 90 < th and th <= 180:
                th = 180 - th
            else:
                th = 360 - (th - 180)
        # 左端　壁　得点
        if px < 0:
            px = 0
            self.game_satate = State.Stop
            self.r_point += 1

        # 右端 プレイヤーレシーブ
        if pyxel.width - self.w - self.BAR_WIDTH < px \
            and (self.r_bar_y < py + self.h
                 and py < self.r_bar_y + self.r_bar_h):
            px = pyxel.width - self.w - self.BAR_WIDTH
            if 0 < th and th <= 90:
                th = 180 - th
            else:
                th = 360 - (th - 180)
        # 右端　壁　得点
        if pyxel.width - self.w < px:
            px = pyxel.width - self.w
            self.game_satate = State.Stop
            self.l_point += 1

        # 上端
        if py < 0:
            py = 0
            th = 360 - th
        # 下端
        if pyxel.height - self.h < py:
            py = pyxel.height - self.h
            th = 360 - th

        return px, py, th

    def NextLocation(self, th: float, c: float):
        '''
        斜辺(c) と 角度θ(th) から 底辺(a) と 高さ(b) を求める
        '''
        rad = th * PI / 180
        a = c * cos(rad)    # x移動量
        b = c * sin(rad)    # y移動量
        return a, b

    def DrawMsgCenter(self, msg: str, y_offset: float, col: int = None):
        '''
        中央ぞろえでテキストを描画。高さは任意。
        '''
        if col is None:
            col = pyxel.COLOR_RED
        x = pyxel.width / 2 - self.umplus10.text_width(msg) / 2
        pyxel.text(x, y_offset, msg, col, self.umplus10)


App()
