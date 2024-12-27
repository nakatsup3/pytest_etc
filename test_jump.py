import pyxel
from enum import Enum
from math import sin
from math import pi as PI
from math import log
from math import e

class State(Enum):
    STANDING      = 1 # 地面に立っている
    JUMPING       = 2 # ジャンプ中

GROUND_Y = 100
FPS = 60
CHARA_H = 16

class App:
    def __init__(self):
        pyxel.init(160, 120, title="MainWindow", fps=FPS)
        self.init()
        pyxel.run(self.update, self.draw)

    def init(self):
        '''
        ゲーム内部変数初期化
        '''
        # pyxel.mouse(True)
        pyxel.images[0].load(0, 0, "assets/cat_16x16.png")
        self.player = (72, GROUND_Y - CHARA_H)  # プレイヤー座標
        self.state = State.STANDING             # ジャンプ用状態遷移

        self.height = 45
        
        self.t = 0
        self.v0 = 9
        self.g = 0.9
        self.stand_y = GROUND_Y - CHARA_H
        self.jmpd = 0
        self.blocks = []
        grnd = GROUND_Y
        self.blocks.append((0, grnd, pyxel.width - 50, 10))
        self.blocks.append((pyxel.width - 30, grnd - 20, 30, 10))

    def update(self):
        x, y = self.player
        if self.state == State.STANDING:
            # ジャンプする
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.t = 1
                self.state = State.JUMPING
            if pyxel.btn(pyxel.KEY_RIGHT):
                x += 1

            y = 0.5 * self.g * self.t * self.t \
                        - self.v0 * self.t + self.stand_y

            if isHit(self.player, self.blocks[0]):
                if self.stand_y < y:
                    y = GROUND_Y - CHARA_H
                    self.state = State.STANDING
                    self.jmpd = self.t
            else:
                
                self.t = min(60, self.t + 1) 
            # if self.state == State.JUMPING:
            #     self.t = min(60, self.t + 1)    
        self.player = (x, y)
        

    def draw(self):
        pyxel.cls(pyxel.COLOR_GRAY)
        pyxel.rect(0, GROUND_Y, pyxel.width, pyxel.height, pyxel.COLOR_BROWN)
        x, y = self.player
        pyxel.blt(x, y, 0, 0, 0, CHARA_H, CHARA_H, colkey=13)
        pyxel.text(0,0, f'{self.jmpd}', 0)
        
        for b in self.blocks:
            l, t, w, h = b
            pyxel.rect(l, t, w, h, 0)


def isHit(player, block):
    '''
    当たり判定
    '''
    x, y = player
    l1 = x
    t1 = y
    r1 = x + 16
    b1 = y + 16

    l2, t2, r, b = block
    r2 = l2 + r
    b2 = t2 + b
    if r2 > l1 and r1 > l2 \
            and b2 > t1 and b1 > t2:
        return True  # ヒット
    return False  # ヒットなし


# 開始
App()

# jump
# __init__
        # self.t = 0              # from 0 to 1
        # self.distortion = 1   # ゆがみ

# update()
            # pattrn A
            # self.t += 1 / FPS
            # y = GROUND_Y + (self.height * e * self.t * log(self.t)) - CHARA_H
            
            # pattern B
            # y = (GROUND_Y - (1.0 - pow(1.0-sin(PI * self.t), self.distortion))
            #      * self.height) - CHARA_H 

            # if 1 < self.t:
            #     y = GROUND_Y - CHARA_H
            #     self.t = 0
            #     if self.state == State.JUMPING:
            #         self.state = State.STANDING