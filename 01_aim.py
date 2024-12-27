import pyxel
from math import sqrt

# ウインドウ設定
WINDOW_HEIGHT = 160
WINDOW_WIDTH = 160
TITLE = 'AIM Practice'
FPS = 60

MAX = 10
DEFAULT_INTERVAL = 40

TITLE_MODE = 0
COUNT_DOWN = 1
PLAY_GAME = 2
END = 3


class Target:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 0
        self.add = (1 / FPS) * 10
        self.end = False

    def update(self) -> int:
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            xl = abs(self.x - pyxel.mouse_x)
            a = xl * xl
            yl = abs(self.y - pyxel.mouse_y)
            b = yl * yl
            c = sqrt(a + b)
            if c < self.r:
                self.end = True
                return 1
        if self.end:
            return 0

        self.r += self.add
        if MAX <= self.r:
            self.add = (1 / FPS) * -10
        if self.r <= 0:
            self.end = True
        return 0

    def draw(self):
        pyxel.circ(self.x, self.y, self.r, pyxel.COLOR_WHITE)


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
        self.fnt_jp_10 = pyxel.Font("assets/umplus_j10r.bdf")
        self.targets = []
        self.interval = DEFAULT_INTERVAL    # ターゲット追加インターバル
        self.score = 0              # ゲームスコア
        self.hi_score = 0           # ハイスコア
        self.state = 0              # 状態
        self.count = 0              # タイムカウント
        self.is_update = False      # ハイスコア更新有無
        self.hit_count = 0          # インターバル変更ヒット数カウント

    def update(self):
        '''
        データ更新
        '''
        if self.state == TITLE_MODE:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                # 変数初期化
                self.interval = DEFAULT_INTERVAL
                self.targets.clear()
                self.count = 4  # 次の開始カウントダウン用
                self.score = 0
                self.is_update = False
                self.hit_count = 0
                self.state = COUNT_DOWN

        elif self.state == COUNT_DOWN:
            if pyxel.frame_count % 60 == 0:
                self.count -= 1
            # Start を表記させて次へ移行
            if self.count <= -1:
                self.count = 61     # ゲームプレイ時間
                self.state = PLAY_GAME

        elif self.state == PLAY_GAME:
            self.CountDown()
            self.AddTarget()
            self.UpdateTarget()
            self.RemoveTarget()
            self.PaseUp()
            self.TimeUp()

        elif self.state == END:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.state = TITLE_MODE

    def CountDown(self):
        # ゲーム時間カウント   
        if pyxel.frame_count % 60 == 0:
            self.count -= 1

    def AddTarget(self):
        # ターゲット追加
        if pyxel.frame_count % self.interval == 0:
            x = pyxel.rndi(10, pyxel.width - 10)
            y = pyxel.rndi(20, pyxel.height - 10)
            self.targets.append(Target(x, y))

    def UpdateTarget(self):
        # ターゲットの更新とポイント確認
        point = 0
        for t in self.targets:
            point += t.update()
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and point == 0:
            self.score = max(0, self.score - 1)
            self.hit_count = 0
        else:
            if 0 < point:
                self.hit_count += 1
            self.score += point

    def RemoveTarget(self):
        # ターゲット除外
        tmp = []
        while self.targets:
            t = self.targets.pop()
            if t.end is False:
                tmp.append(t)
        while tmp:
            self.targets.append(tmp.pop())

    def PaseUp(self):
        # ペースアップ
        if 10 <= self.hit_count:
            self.interval = max(10, self.interval - 5)
            self.hit_count = 0

    def TimeUp(self):
        # タイムアップ表記
        if self.count <= -3:
            if self.hi_score < self.score:
                self.hi_score = self.score
                self.is_update = True
            self.state = END

    def draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_BLACK)

        if self.state == TITLE_MODE:
            self.DrawText('AIM Practice', y = pyxel.height / 2)

        elif self.state == COUNT_DOWN:
            txt = ''
            if 0 < self.count < 4:
                txt = f'{self.count}'
            if 0 == self.count:
                txt = 'start'
            self.DrawText(txt, y = pyxel.height / 2)

        elif self.state == PLAY_GAME:
            if 0 <= self.count < 61:
                for t in self.targets:
                    t.draw()
                self.DrawText(f'SCORE:{self.score:04}', x = 1, y = 1)
                cnt = f'time:{self.count:02}'
                pos = pyxel.width - self.fnt_jp_10.text_width(cnt)
                self.DrawText(f'time:{self.count:02}', x = pos, y = 1)

            elif self.count < 0:
                self.DrawText('Time up', y = pyxel.height / 2)

        elif self.state == END:
            dy = pyxel.height / 2
            self.DrawText(f'SCORE:{self.score:04}', y = dy)
            c = pyxel.COLOR_WHITE
            if self.is_update:
                c = pyxel.frame_count % 16
            self.DrawText(f'HI SCORE:{self.score:04}', y=dy + 12, col=c)

    def DrawText(self, s, x = None, y = 0,
                   col = pyxel.COLOR_WHITE, bcol = pyxel.COLOR_GRAY):
        '''
        アウトラインをつけたテキスト画面上に描画する
        '''
        if x is None:
            x = pyxel.width / 2 - self.fnt_jp_10.text_width(s) / 2
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx != 0 or dy != 0:
                    pyxel.text(x + dx, y + dy, s, bcol,
                               self.fnt_jp_10)
        pyxel.text(x, y, s, col, self.fnt_jp_10)


App()
