import pyxel as px
import time

# ウインドウ設定
WINDOW_HEIGHT = 128
WINDOW_WIDTH = 128
TITLE = 'MainWindow'
FPS = 60
DT = 1 / (FPS / 2)


class ObjectBase:
    '''
    いろんなオブジェクトのペース
    '''
    def __init__(self, x: float, y: float,
                 w: float, h: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class Player(ObjectBase):
    def __init__(self, x, y):
        super().__init__(x, y, 10, 10)
        self.boost = 100
        self.boost_t = 0
        self.vel = 0

    def update(self):

        if px.btn(px.KEY_SPACE):
            if self.boost <= 0:
                self.vel += 9.8 * DT
                self.y += self.vel * DT
            else:
                self.y -= (self.boost_t * self.boost_t) / 5000
                self.boost = max(0, self.boost - 1)
                self.boost_t = min(100, self.boost_t + 1)
                self.vel = 0
        else:
            self.vel += 9.8 * DT
            self.y += self.vel * DT
            self.boost = min(100, self.boost + 1)
            self.boost_t = 0

        if px.btn(px.KEY_RIGHT):
            self.x += 1
        if px.btn(px.KEY_LEFT):
            self.x -= 1
        
        if px.height < self.y + self.h:
            self.y = px.height - self.h
            

    def draw(self):
        px.tri(self.x - self.w / 2, self.y + self.h,
               self.x, self.y,
               self.x + self.w / 2, self.y + self.h,
               px.COLOR_WHITE)
        
        offset = px.height * self.boost / 100
        px.rect(px.width - 5, px.height - offset, 5,
                   offset,
                   px.COLOR_WHITE)


class Wall(ObjectBase):
    def __init__(self, h):
        x = px.width
        y = px.height - h
        super().__init__(x, y, 5, h)

    def update(self):
        self.x -= 1

    def draw(self):
        px.rect(self.x, self.y, self.w, self.h, px.COLOR_WHITE)


class App:
    def __init__(self):
        px.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS, display_scale=2)
        px.mouse(False)
        px.rseed(int(time.time()))
        self.ReadResources()
        self.DefineVariables()
        px.run(self.update, self.draw)

    def ReadResources(self):
        '''
        リソースファイルの読み込み
        '''
        # px.images[0].load(0, 0, 'assets/Pallet.png', incl_colors=True)
        # self.fnt_jp_10 = px.Font('assets/umplus_j10r.bdf')
        pass

    def DefineVariables(self):
        '''
        内部変数初期化
        '''
        self.player = Player(0, 0)
        self.walls = []
        self.interval = 120

    def update(self):
        '''
        データ更新
        '''
        self.player.update()
        self.interval = max(0, self.interval - 1)
        if self.interval <= 0:
            offset = px.rndi(-30, 30)
            self.walls.append(Wall(px.height / 2 + offset))
            self.interval = 120

        if 0 < len(self.walls):
            w: Wall
            for w in self.walls:
                w.update()

        tmp = []
        while self.walls:
            w = self.walls.pop()
            if 0 < w.x + w.w:
                tmp.append(w)
        while tmp:
            self.walls.append(tmp.pop())

    def draw(self):
        '''
        描画更新
        '''
        px.cls(px.COLOR_BLACK)
        self.player.draw()

        if 0 < len(self.walls):
            w: Wall
            for w in self.walls:
                w.draw()


App()
