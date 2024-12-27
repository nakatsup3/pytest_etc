import pyxel
import random
from enum import Enum

# ウインドウ設定
WINDOW_HEIGHT = 128
WINDOW_WIDTH = 128
TITLE = 'MainWindow'
FPS = 60

# ゲーム定数
CARD_HEIGHT = 8
CARD_WIDTH = 5
DEFAULT_FONT_SIZE = 6


class State(Enum):
    Drow = 0
    Ready = 1
    Select = 2
    Check = 3


class Player:
    def __init__(self):
        self.deck = []
        g = [1] * 10
        c = [2] * 10
        p = [3] * 10
        self.deck = self.RandomSet(g, c, p)
        self.cards = []
        self.life = 5

    def RandomSet(self, g, c, p):
        '''
        シャッフル
        '''
        random.seed()
        ary = g + c + p
        rand_ary = []
        for item in ary:
            rand_ary.append({'key': item,
                             'value': random.randrange(255)})
        sort_ary = sorted(rand_ary, key=lambda x: x['value'])
        return [d.get('key') for d in sort_ary]


class App:
    DROW_WAIT = 30

    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS)
        self.init()
        pyxel.run(self.update, self.draw)

    def init(self):
        '''
        ゲーム内部変数初期化
        '''
        pyxel.mouse(True)
        self.fnt_jp_10 = pyxel.Font("assets/umplus_j10r.bdf")

        self.p1 = Player()
        self.p2 = Player()
        self.game_state = State.Drow
        self.wait = self.DROW_WAIT
        self.msg_draw = '手札を補充します'
        self.click_point = (0, 0)
        self.card_selected = -1
        self.p2_view = False
        
        self.p2_x_offset = 0

    def update(self):
        '''
        更新
        '''
        if self.game_state == State.Drow:
            if self.wait <= 0:
                p1_ok = self.CardDrow(self.p1)
                p2_ok = self.CardDrow(self.p2)
                if p1_ok and p2_ok:
                    self.game_state = State.Ready
                else:
                    self.wait = self.DROW_WAIT
            self.wait -= 1

        elif self.game_state == State.Ready:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.click_point = (pyxel.mouse_x, pyxel.mouse_y)
            if pyxel.btnp(pyxel.KEY_C):
                self.p2_view = not self.p2_view
            self.CheckSelected()
            if 0 <= self.card_selected:
                self.game_state = State.Select

        elif self.game_state == State.Select:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.click_point = (pyxel.mouse_x, pyxel.mouse_y)
            self.CheckSelected()
            if self.card_selected < 0:
                self.game_state = State.Ready
                
        elif self.game_state == State.Check:
            if self.p2_x_offset < 3.5:
                self.p2_x_offset += 0.2
            else:
                self.p2_x_offset = 3.53553439842981

    def draw(self):
        '''
        描画
        '''
        pyxel.cls(pyxel.COLOR_BLACK)

        # 画面内の各描画
        self.DrawCommon()

        # 状況ごとの描画
        if self.game_state == State.Drow:
            self.DrawMsgCenter(pyxel.height - 20, self.msg_draw)
        if self.game_state == State.Ready:
            self.DrawMsgCenter(pyxel.height - 20, 'カード選択')
            self.DrawSelectedCard()
        if self.game_state == State.Select:
            self.DrawSelectedCard()
            self.DrawMsgCenter(pyxel.height - 20, '勝負する？')
            self.Choices()
        if self.game_state == State.Check:
            self.DrawSelectedCard()

        # Debug 描画
        self.DrawMsgCenter(0, self.game_state.name, pyxel.COLOR_WHITE)
        pos = f'{pyxel.mouse_x},{pyxel.mouse_y}'
        self.DrawMsgCenter(10, pos, pyxel.COLOR_WHITE)

    def CheckSelected(self):
        '''
        更新 クリック判定
        '''
        mcx, mcy = self.click_point
        # yes, no 選択肢
        if pyxel.height - 26 < mcy:
            str_width = DEFAULT_FONT_SIZE * 3
            left = pyxel.width - str_width - 2
            top = pyxel.height - 24
            if left < mcx < left + str_width and top < mcy < top + 4:
                self.game_state = State.Check
                self.p2_x_offset = -3.53553439842981
            return

        # カード選択
        c = -1
        self.card_selected = -1
        for _ in self.p1.cards:
            c += 1
            left = c * (CARD_WIDTH + 1) + 3
            if left < mcx < left + CARD_WIDTH \
                    and 3 < mcy < CARD_HEIGHT + 3:
                self.card_selected = c
                break

    def DrawSelectedCard(self):
        '''
        描画 選択したカードの拡大描画
        '''
        self.DrawMsgCenter(pyxel.height / 2, 'VS', pyxel.COLOR_WHITE)
        w = CARD_WIDTH * 5
        p2_left = pyxel.width / 2 - (25 + w)
        offset = 0
        if self.game_state == State.Check:
            offset = -1 * (self.p2_x_offset * self.p2_x_offset) + 12.5

        pyxel.rect(pyxel.width / 2 + p2_left + offset, 37,
                   w - (offset * 2), CARD_HEIGHT * 5, pyxel.COLOR_PURPLE)
        if 0 <= self.card_selected < len(self.p1.cards):
            crd = self.p1.cards[self.card_selected]
            clr = self.CardNumToColor(crd)
            pyxel.rect(25, 37, w, CARD_HEIGHT * 5, clr)

    def DrawCommon(self):
        '''
        描画 装飾
        '''
        # カード
        self.DrawCards(self.p1, True, 3)
        card_ary_width = (CARD_WIDTH + 1) * 5
        com_offset = pyxel.width - 3 - card_ary_width
        self.DrawCards(self.p1, False, com_offset)

        # ライフゲージ
        pyxel.tri(1, 11 + CARD_HEIGHT,
                  card_ary_width + 3, 11 + CARD_HEIGHT,
                  card_ary_width + 3, 17 + CARD_HEIGHT,
                  pyxel.COLOR_LIGHT_BLUE)
        pyxel.tri(com_offset - 2, 17 + CARD_HEIGHT,
                  com_offset - 2, 11 + CARD_HEIGHT,
                  com_offset + card_ary_width, 11 + CARD_HEIGHT,
                  pyxel.COLOR_LIGHT_BLUE)
        str_player = 'player'
        left = (card_ary_width + 3) - len(str_player) * 4
        pyxel.text(left, 5 + CARD_HEIGHT, str_player, pyxel.COLOR_WHITE)
        pyxel.text(com_offset - 2, 5 + CARD_HEIGHT, 'com', pyxel.COLOR_WHITE)

        self.DrawLife(self.p1, True, card_ary_width - (5 * 5) - 1)
        self.DrawLife(self.p2, False, com_offset - 1)

        # メッセージボックス
        self.MsgBox()

    def DrawLife(self, p, is_p1, offset):
        '''
        描画 体力
        '''
        for i in range(5):
            if is_p1:
                damage = 5 - p.life
                for i in range(5):
                    if i < damage:
                        pyxel.ellib(i * 6 + offset, 12 + CARD_HEIGHT,
                                    5, 5, pyxel.COLOR_PINK)
                    else:
                        pyxel.elli(i * 6 + offset, 12 + CARD_HEIGHT,
                                   5, 5, pyxel.COLOR_PINK)
            else:
                if i < p.life:
                    pyxel.elli(i * 6 + offset, 12 + CARD_HEIGHT,
                               5, 5, pyxel.COLOR_PINK)
                else:
                    pyxel.ellib(i * 6 + offset, 12 + CARD_HEIGHT,
                                5, 5, pyxel.COLOR_PINK)

    def DrawMsgCenter(self, y_offset: float, msg: str, col: int = None):
        '''
        描画 中央ぞろえでテキストを描画。高さは任意。
        '''
        offset = self.fnt_jp_10.text_width(msg) / 2
        if col is None:
            col = pyxel.COLOR_BLACK
        x = pyxel.width / 2 - offset
        pyxel.text(x, y_offset, msg, col=col, font=self.fnt_jp_10)

    def CardDrow(self, p):
        '''
        更新 手札ドロー
        '''
        if len(p.cards) < 5:
            if 0 < len(p.deck):
                p.cards.append(p.deck.pop(0))
            else:
                return True
        else:
            return True
        return False

    def CardNumToColor(self, crd):
        '''
        描画 色選択
        '''
        col = pyxel.COLOR_PURPLE
        if crd == 0:
            col == pyxel.COLOR_GRAY
        elif crd == 1:
            col = pyxel.COLOR_RED
        elif crd == 2:
            col = pyxel.COLOR_CYAN
        elif crd == 3:
            col = pyxel.COLOR_YELLOW
        return col

    def DrawCards(self, p, is_p1, offset):
        '''
        描画 手札描画
        '''
        card_ary_width = (CARD_WIDTH + 1) * 5
        pyxel.rect(offset - 2, 2,
                   card_ary_width + 3, 2 + CARD_HEIGHT,
                   pyxel.COLOR_WHITE)
        c = -1

        for crd in p.cards:
            c += 1
            if is_p1 or self.p2_view:
                col = self.CardNumToColor(crd)
            else:
                col = pyxel.COLOR_PURPLE

            left = c * (CARD_WIDTH + 1) + offset
            if self.card_selected == c and is_p1:
                pyxel.rectb(left, 3, CARD_WIDTH, CARD_HEIGHT, col)
            else:
                pyxel.rect(left, 3, CARD_WIDTH, CARD_HEIGHT, col)
            if is_p1 is False:
                continue

            # マウスカーソル追従描画
            mx = pyxel.mouse_x
            my = pyxel.mouse_y
            if left < mx < left + CARD_WIDTH and 3 < my < CARD_HEIGHT + 3:
                pyxel.rectb(left - 1, 2,
                            CARD_WIDTH + 2, CARD_HEIGHT + 2,
                            pyxel.COLOR_LIME)

    def MsgBox(self):
        '''
        描画 メッセージボックス
        '''
        pyxel.rect(5, pyxel.height - 26,
                   pyxel.width - 10, 21, pyxel.COLOR_WHITE)
        pyxel.rectb(5, pyxel.height - 26,
                    pyxel.width - 10, 21, pyxel.COLOR_GRAY)

    def Choices(self):
        '''
        描画 選択肢
        '''
        str_width = DEFAULT_FONT_SIZE * 3
        left = pyxel.width - str_width - 2
        top = pyxel.height - 24
        mx = pyxel.mouse_x
        my = pyxel.mouse_y
        
        if left < mx < left + str_width and top < my < top + 4:
            pyxel.text(left, top, 'yes', pyxel.COLOR_RED)
        else:
            pyxel.text(left, top, 'yes', pyxel.COLOR_BLACK)
        
        top += 7
        if left < mx < left + str_width and top < my < top + 4:
            pyxel.text(left, top, 'No', pyxel.COLOR_RED)
        else:
            pyxel.text(left, top, 'No', pyxel.COLOR_BLACK)

App()
