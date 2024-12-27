import pyxel

'''
先手は必ず黒から
縦横斜めに5目同じ色を並べたら勝ち
禁じ手は未実装

画面左上に現在の手番表示
勝ち負けが決まるとリセットするまで盤面操作不可

操作
マウスクリック：一手打つ
Rキー:リセット
Uキー:1手戻す
'''

WINDOW_HEIGHT = 256
WINDOW_WIDTH = 256
TITLE = 'gomoku'
FPS = 60
CELL_SIZE = 10
CELL_CNT = 20

MARGIN = 30
WIN_NUM = 5

OUT_LINE = CELL_SIZE * CELL_CNT + MARGIN
IN_LINE = CELL_SIZE * (CELL_CNT - 1) + MARGIN
OFFSET = MARGIN + (CELL_SIZE / 2) + 1
OUT_DY = CELL_CNT * CELL_SIZE + MARGIN
OUT_DX = CELL_CNT * CELL_SIZE + MARGIN


class App:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS, display_scale=1)
        self.init()
        pyxel.run(self.update, self.draw)

    def init(self):
        '''
        内部変数初期化
        '''
        pyxel.mouse(True)
        self.umplus10 = pyxel.Font("assets/umplus_j10r.bdf")
        self.player_map = [[0 for _ in range(CELL_CNT)]
                           for _ in range(CELL_CNT)]
        self.turn = pyxel.COLOR_BLACK + 1
        self.winner = 0
        self.direction = 0
        self.history = []
        self.future = []

    def update(self):
        '''
        データ更新
        '''
        if pyxel.btnp(pyxel.KEY_R):
            self.Reset()
            return

        if self.winner != 0:
            return

        # 打つ
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            x = int((pyxel.mouse_x - MARGIN - 5) / CELL_SIZE)
            y = int((pyxel.mouse_y - MARGIN - 5) / CELL_SIZE)
            # 範囲外や同じ場所のクリックは処理パス
            if CELL_CNT - 1 <= x or x < 0:
                return
            if CELL_CNT - 1 <= y or y < 0:
                return
            if self.player_map[y][x] != 0:
                return
            # 石セット
            self.player_map[y][x] = self.turn
            self.history.append((x, y))
            # 判定
            self.winner, self.direction = self.Judgement(x, y, self.turn)
            if self.winner != 0:
                return
            self.TurnChange()
            if 0 < len(self.future):
                self.future.clear()

        # Undo 戻す
        elif pyxel.btnp(pyxel.KEY_U):
            if 0 < len(self.history):
                x, y = self.history.pop()
                self.player_map[y][x] = 0
                self.future.append((x, y))
                self.TurnChange()

        # Redo やり直し
        elif pyxel.btnp(pyxel.KEY_Y):
            if 0 < len(self.future):
                x, y = self.future.pop()
                self.player_map[y][x] = self.turn
                self.history.append((x, y))
                self.TurnChange()

    def Reset(self):
        '''
        盤面リセット
        '''
        for r in range(CELL_CNT):
            for c in range(CELL_CNT):
                self.player_map[r][c] = 0
        self.winner = 0
        self.history.clear()
        self.future.clear()
        self.turn = pyxel.COLOR_BLACK + 1

    def TurnChange(self):
        '''
        手番交代
        '''
        if self.turn == pyxel.COLOR_BLACK + 1:
            self.turn = pyxel.COLOR_WHITE + 1
        else:
            self.turn = pyxel.COLOR_BLACK + 1

    def SameCount(self, x, y, xa, ya, t):
        '''
        連なりカウント
        '''
        cnt = 0
        for i in range(1, WIN_NUM):
            c = x + (i * xa)
            r = y + (i * ya)
            if 0 <= r and 0 <= c \
                    and r < CELL_CNT and c < CELL_CNT:
                if self.player_map[r][c] == t:
                    cnt += 1
                else:
                    break
        return cnt

    def Judgement(self, x, y, t):
        '''
        ５つ並んだか？
        '''
        # 横捜査
        cnt_a = 0
        cnt_b = 0
        cnt_a = self.SameCount(x, y, 1, 0, t)
        cnt_b = self.SameCount(x, y, -1, 0, t)
        if WIN_NUM <= cnt_a + cnt_b + 1:
            return t, 1

        # 縦捜査
        cnt_a = 0
        cnt_b = 0
        cnt_a = self.SameCount(x, y, 0, 1, t)
        cnt_b = self.SameCount(x, y, 0, -1, t)
        if WIN_NUM <= cnt_a + cnt_b + 1:
            return t, 2

        # 斜め右上、左下
        cnt_a = 0
        cnt_b = 0
        cnt_a = self.SameCount(x, y, 1, -1, t)
        cnt_b = self.SameCount(x, y, -1, 1, t)
        if WIN_NUM <= cnt_a + cnt_b + 1:
            return t, 3

        # 斜め右下、左上
        cnt_a = 0
        cnt_b = 0
        cnt_a = self.SameCount(x, y, -1, -1, t)
        cnt_b = self.SameCount(x, y, 1, 1, t)
        if WIN_NUM <= cnt_a + cnt_b + 1:
            return t, 4
        return 0, 0

    def draw(self):
        '''
        描画更新
        '''
        pyxel.cls(pyxel.COLOR_GRAY)
        self.Info()
        self.Line()
        self.Stone()
        if self.winner != 0:
            self.WinnerDraw()

    def Info(self):
        '''
        盤面の情報
        '''
        if self.winner == 0:
            pyxel.text(5, 5, '手番', pyxel.COLOR_BLACK, self.umplus10)
        else:
            pyxel.text(5, 5, 'Win', pyxel.COLOR_BLACK, self.umplus10)
        pyxel.elli(30, 5, 10, 10, self.turn - 1)

    def Line(self):
        '''
        罫線描画
        '''
        line_color = pyxel.COLOR_BLACK
        for r in range(CELL_CNT):
            dy = r * CELL_SIZE + MARGIN
            if r == 0:
                pyxel.line(MARGIN, dy, OUT_LINE, dy, line_color)
            else:
                pyxel.line(MARGIN + CELL_SIZE, dy,
                           IN_LINE, dy, line_color)
            for c in range(CELL_CNT):
                dx = c * CELL_SIZE + MARGIN
                if c == 0:
                    pyxel.line(dx, MARGIN, dx, OUT_LINE, line_color)
                else:
                    pyxel.line(dx, MARGIN + CELL_SIZE, dx,
                               IN_LINE, line_color)
                # 点の描画
                if (r == 3 and c == 3) or (r == 3 and c == 9) \
                        or (r == 3 and c == 15) or (r == 9 and c == 3) \
                        or (r == 9 and c == 9) or (r == 9 and c == 15) \
                        or (r == 15 and c == 3) or (r == 15 and c == 9) \
                        or (r == 15 and c == 15):
                    pyxel.elli(c * CELL_SIZE + OFFSET + 2,
                               r * CELL_SIZE + OFFSET + 2, 4, 4, line_color)
        # 最後の線
        pyxel.line(MARGIN, OUT_DY, OUT_LINE, OUT_DY, line_color)
        pyxel.line(OUT_DX, MARGIN, OUT_DX, OUT_LINE, line_color)

    def Stone(self):
        '''
        置いている石を描画
        '''
        x = int((pyxel.mouse_x - MARGIN - 5) / CELL_SIZE)
        y = int((pyxel.mouse_y - MARGIN - 5) / CELL_SIZE)
        r = -1
        for row in self.player_map:
            r += 1
            for c in range(len(row)):
                if 0 < row[c]:
                    pyxel.elli(c * CELL_SIZE + OFFSET,
                               r * CELL_SIZE + OFFSET,
                               8, 8, row[c] - 1)
                # プレイヤー配置位置に丸を描画
                if CELL_CNT - 1 <= x:
                    continue
                if CELL_CNT - 1 <= y:
                    continue
                if x == c and y == r:
                    pyxel.ellib(c * CELL_SIZE + OFFSET,
                                r * CELL_SIZE + OFFSET,
                                9, 9, pyxel.COLOR_RED)

    def SameDraw(self, x, y, xa, ya, t):
        '''
        連なりに枠線描画
        '''
        for i in range(1, WIN_NUM):
            c = x + (i * xa)
            r = y + (i * ya)
            if 0 <= r and 0 <= c \
                    and r < CELL_CNT and c < CELL_CNT:
                if self.player_map[r][c] == t:
                    pyxel.ellib(c * CELL_SIZE + OFFSET,
                                r * CELL_SIZE + OFFSET,
                                9, 9, pyxel.COLOR_YELLOW)
                else:
                    break
        return 

    def WinnerDraw(self):
        '''
        勝者に枠線描画
        '''
        x, y = self.history[-1]
        d = self.direction
        w = self.winner
        
        if d == 1:
            self.SameDraw(x, y, 1, 0, w)
            self.SameDraw(x, y, -1, 0, w)
        elif d == 2:
            self.SameDraw(x, y, 0, 1, w)
            self.SameDraw(x, y, 0, -1, w)
        elif d == 3:
            self.SameDraw(x, y, 1, -1, w)
            self.SameDraw(x, y, -1, 1, w)
        elif d == 4:
            self.SameDraw(x, y, -1, -1, w)
            self.SameDraw(x, y, 1, 1, w)
        pyxel.ellib(x * CELL_SIZE + OFFSET,
                    y * CELL_SIZE + OFFSET,
                    9, 9, pyxel.COLOR_YELLOW)


App()
