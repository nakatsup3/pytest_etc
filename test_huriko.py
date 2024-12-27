import pyxel

# ウインドウ設定
WINDOW_HEIGHT = 128
WINDOW_WIDTH = 128
TITLE = 'MainWindow'
FPS = 60


class App:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS)
        pyxel.mouse(False)
        self.init()
        pyxel.run(self.update, self.draw)

    def init(self):
        '''
        ゲーム内部変数初期化
        '''
        # パラメータと定数
        self.g = 9.8
        # 振り子の長さ
        self.R = 50.0
        # 振り子の質量
        self.m = 1.0
        #時刻の初期値
        # self.t=0
        # 位置の初期値
        self.x = 49.0
        self.y = 0.0

        # 速度の初期値
        self.v_x = 0.0
        self.v_y = 0.0
        # 加速度の初期値
        self.a_x = 0.0
        self.a_y = 0.0
        
        self.offset = pyxel.width / 2

    def update(self):
        '''
        データ更新
        '''
        #微小時間
        dt = 0.1
        
        # while(self.t<10):
        # 束縛条件
        y = -(self.R ** 2 - self.x ** 2) ** 0.5
        # 張力の大きさ
        t = self.m * self.R * (self.v_x ** 2
                               + self.v_y ** 2
                               + y * self.a_y) / (self.x ** 2)
        # 張力の大きさの上限
        if 10.0 < t:
            t = 10.0
        # 運動方程式
        self.a_x = -t * self.x / (self.m * self.R)
        self.a_y = -self.g - t * y / (self.m * self.R)

        # 速度の更新
        self.v_x = self.v_x + self.a_x * dt
        self.v_y = self.v_y + self.a_y * dt
        # 位置の更新
        self.x = (self.x + self.v_x * dt)
        self.y = (y + self.v_y * dt) * -1.0

    def draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_BLACK)
        pyxel.elli(self.x + self.offset, self.y, 10, 10, pyxel.COLOR_WHITE)

App()
