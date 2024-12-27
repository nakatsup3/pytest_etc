import pyxel
from enum import Enum


# 状態の列挙体クラス
class State(Enum):
    STANDING      = 1 # 地面に立っている
    JUMPING       = 2 # ジャンプ中
    AERIAL_ATTACK = 3 # 空中攻撃中
    RECOVERY      = 4 # 硬直中
    
class GameMode(Enum):
    TITLE = 1
    PLAY = 2

GROUND_Y = 100
PLAYER_IMG = 0
MAP_IMG = 1

class App:
    

    def __init__(self):
        pyxel.init(160, 120, title="MainWindow", fps=60)
        self.init()
        pyxel.run(self.update, self.draw)


    def init(self):
        '''
        ゲーム内部変数初期化
        '''
        pyxel.images[PLAYER_IMG].load(0, 0, "assets/cat_16x16.png")
        pyxel.images[MAP_IMG] = pyxel.Image.from_image(
            "assets/urban_rpg.png", incl_colors=True
        )
        self.umplus10 = pyxel.Font("assets/umplus_j10r.bdf")

        self.player = (72, GROUND_Y - 16)       # プレイヤー座標
        self.v0 = 9                             # 初速
        self.time = 20                          # ジャンプ経過時間
        self.gravity = 0.9                      # 重力加速度
        self.state = State.STANDING             # ジャンプ用状態遷移
        self.recovery_frame = 0                 # ジャンプ硬直時間
        self.game_mode = GameMode.TITLE         # タイトル・プレイ画面切り替え
        self.score = 0                          # スコア
        self.life = 5                           # 体力

    def draw_text_mid(self, x, y, s, col, bcol=None):
        '''
        テキスト描画
        '''
        if bcol is None:
            bcol = pyxel.COLOR_BLACK
        # アウトライン描画
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx != 0 or dy != 0:
                    pyxel.text(x + dx, y + dy, s, bcol, self.umplus10)
        # 
        pyxel.text(x, y, s, col, self.umplus10)

    def input_character_control_key(self):
        '''
        キャラ操作キー入力
        '''
        if self.state == State.STANDING:
            if pyxel.btnp(pyxel.KEY_SPACE):
                # ジャンプする
                self.time = 0
                self.state = State.JUMPING
        elif self.state == State.JUMPING:
            if pyxel.btnp(pyxel.KEY_SPACE):
                # 空中攻撃を開始する
                self.vy = 3
                self.state = State.AERIAL_ATTACK
        elif self.state == State.AERIAL_ATTACK:
            # 特に何もしない
            pass
        elif self.state == State.RECOVERY:
            if self.recovery_frame > 0:
                # 硬直中
                self.recovery_frame -= 1
            else:
                # 硬直終了
                self.state = State.STANDING
        x, y = self.player
        if pyxel.btn(pyxel.KEY_LEFT):
            x = max(x - 1, 0)
        if pyxel.btn(pyxel.KEY_RIGHT):
            x = min(x + 1, 144)
        
        # 速度を更新
        y = 0.5 * self.gravity * self.time * self.time \
            - self.v0 * self.time + GROUND_Y
        
        # ニャンコを地面に着地させる
        if y > GROUND_Y - 16:
            y = GROUND_Y - 16
            if self.state == State.AERIAL_ATTACK:
                self.state = State.RECOVERY
                self.recovery_frame = 20 # 20フレーム間硬直する
            elif self.state == State.JUMPING:
                # 通常の着地
                self.state = State.STANDING
        self.player = (x, y)
        self.time += 1


    def update(self):
        # 常時　終了ボタン
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        # キャラ操作
        self.input_character_control_key()

        # タイトル画面操作
        if self.game_mode == GameMode.TITLE:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.game_mode = GameMode.PLAY


    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        
        if self.game_mode == GameMode.TITLE:
            title = 'Zombie Island'
            w = len(title) * 6 / 2
            self.draw_text_mid((pyxel.width / 2) - w, 30, title, pyxel.COLOR_RED)
            msg = 'enter key press start'
            w = len(msg) * 6 / 2
            self.draw_text_mid((pyxel.width / 2) - w, 70, msg, pyxel.COLOR_RED)

        elif self.game_mode == GameMode.PLAY:
            # 画面情報描画
            pyxel.text(2, 2, f'SCORE:{self.score:0000}', pyxel.COLOR_WHITE)
            lf = 'O' * self.life + '-' * (5 - self.life)
            pyxel.text(2, 10, f'Life:{lf}', pyxel.COLOR_WHITE)

            # 地面
            pyxel.rect(GROUND_Y, pyxel.width, pyxel.height, 10,4)
            
            # Player
            x, y = self.player
            if self.state == State.RECOVERY:
                if self.recovery_frame % 2 == 0:
                    y += self.recovery_frame / 4
            pyxel.blt(x, y, PLAYER_IMG, 0, 0, 16, 16, colkey=13)


App()