import pyxel
from math import sin
from math import cos
from math import pi as PI

NUM_STARS = 100
STAR_COLOR_HIGH = 12
STAR_COLOR_LOW = 5

class Background:
    def __init__(self):
        self.stars = []
        for i in range(NUM_STARS):
            self.stars.append(
                (
                    pyxel.rndi(0, pyxel.width - 1),
                    pyxel.rndi(0, pyxel.height - 1),
                    pyxel.rndf(1, 2.5),
                )
            )

    def update(self):
        for i, (x, y, speed) in enumerate(self.stars):
            y += speed
            if y >= pyxel.height:
                y -= pyxel.height
            self.stars[i] = (x, y, speed)

    def draw(self):
        for x, y, speed in self.stars:
            pyxel.pset(x, y, STAR_COLOR_HIGH if speed > 1.8 else STAR_COLOR_LOW)

class Player:
    def __init__(self):
        self.x = pyxel.width / 2 - 5
        self.y = pyxel.height - 10
        self.z = 0
        self.w = 10
        self.h = 5

    def update(self):
        self.z = 0
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x = max(0, self.x - 1)
            self.z = -1
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x = min(pyxel.width - 10, self.x + 1)
            self.z = 1

    def draw(self):
        pyxel.tri(self.x, self.y,
                  self.x + 5, self.y - 5,
                  self.x + 10, self.y,
                  pyxel.COLOR_RED)

class Enemy:
    def __init__(self):
        self.r = 2.5                # 半径
        self.D = int(self.r * 2)    # 直径
        self.x = pyxel.rndi(40, 100)
        self.y = pyxel.rndi(self.D, 100) * - 1
        self.w = self.D
        self.h = self.D
        # Sin波変数
        self.t = 0
        self.speed = pyxel.rndf(0.1, 0.3)
        # ふらふら振幅
        self.frfr = pyxel.rndi(0, 100)
        # x座標調整
        self.xa = pyxel.rndi(40, 100)

    def update(self):
        self.x = self.xa + sin(self.t) * self.frfr
        self.y += 2
        self.t += 0.1
        if pyxel.height < self.y:
            self.t = 0
            self.xa = pyxel.rndi(40, 100)
            self.y = pyxel.rndi(self.D, 100) * - 1
            self.speed = pyxel.rndf(0.1, 0.3)
            self.frfr = pyxel.rndi(0, 100)

    def draw(self):
        pyxel.elli(self.x, self.y, self.D, self.D,
                   pyxel.COLOR_YELLOW)

class Blead:
    def __init__(self, p: Player):
        self.w = 1
        self.h = 3
        self.x = p.x + p.w / 2 - self.w / 2
        self.y = p.y - p.h - self.h
        self.speed = 2
    
    def update(self):
        self.y -= self.speed
    
    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h,
                   pyxel.COLOR_WHITE)


class App:
    def __init__(self):
        pyxel.init(128, 256, title="Pyxel Shooter",
                   fps=60, display_scale=2)
        self.background = Background()
        self.stage_progress = 0
        self.stage_length = 60 * 60 * 3
        self.pos_y = 0
        self.player = Player()
        self.blast = []
        self.enemy = []
        for _ in range(5):
            self.enemy.append(Enemy())
        pyxel.run(self.update, self.draw)

    
    def update(self):
        self.background.update()
        self.UpdateProgress()
        self.player.update()
        self.BlastUpdate()
        for e in self.enemy:
            e.update()
        for b in self.blast:
            b.update()


    def draw(self):
        pyxel.cls(0)
        self.background.draw()
        self.DrawProgress()
        self.player.draw()
        for e in self.enemy:
            e.draw()
        for b in self.blast:
            b.draw()

    def UpdateProgress(self):
        self.stage_progress += 1
        bar = pyxel.height - 10
        prog = min(1, self.stage_progress / self.stage_length)
        self.pos_y = bar - (bar * prog)

    def BlastUpdate(self):
        tmp = []
        while self.blast:
            b = self.blast.pop()
            if 0 < b.y:
                tmp.append(b)
        while tmp:
            self.blast.append(tmp.pop())
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.blast.append(Blead(self.player))
        if 0 < len(self.blast):
            tmp = []
            while self.enemy:
                e = self.enemy.pop()
                ishit = False
                for i in range(len(self.blast)):
                    if self.isHit(e, self.blast[i]):
                        _ = self.blast.pop(i)
                        ishit = True
                        break
                if ishit == False:
                    tmp.append(e)
            while tmp:
                self.enemy.append(tmp.pop())

    def isHit(self, a, b):
        '''
        当たり判定
        '''
        l1 = a.x
        t1 = a.y
        r1 = a.x + a.w
        b1 = a.y + a.h

        l2 = b.x
        t2 = b.y
        r2 = b.x + b.w
        b2 = b.y + b.h
        if r2 > l1 and r1 > l2 \
                and b2 > t1 and b1 > t2:
            return True  # ヒット
        return False  # ヒットなし

    def DrawProgress(self):
        pyxel.rect(5, 5, 3, pyxel.height - 10, pyxel.COLOR_YELLOW)
        pyxel.elli(5, self.pos_y, 3, 3, pyxel.COLOR_RED)


App() 