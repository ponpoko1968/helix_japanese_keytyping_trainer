import argparse
import curses
import curses.ascii
import locale
import logging
import logging.handlers
from collections import namedtuple
import random

CharInfo = namedtuple('CharInfo', ('row', 'left_right', 'shift', 'col'))

logger = logging.getLogger('MyLogger')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler("filename.log"))

locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')


char_set = [
    # 上段
    [[['。', 'な', 'て', 'せ', 'そ'], ['ぺ', 'け', 'よ', 'ー', '　'], ['ぱ', 'げ', 'で', 'ぜ', 'ぞ']],  # 左
     [['・', 'お', 'の', 'に', '　'], ['　', 'び', 'ぎ', 'づ', '　'], ['　', 'ひ', 'き', 'つ', '　']]],  # 右
    # 中段
    [[['こ', 'た', 'か', 'る', 'は'],  # 左
      ['め', 'や', 'も', 'さ', 'ぅ'],
      ['ご', 'だ', 'が', 'ざ', 'ば']],
     [['ー', 'ん', 'い', 'し', 'と', '　'],  # 右
      ['ぃ', 'ぁ', 'ぐ', 'じ', 'ど', 'ぴ'],
      ['む', 'れ', 'く', 'り', 'わ', 'ね']]],
    # 下段
    [[['ゆ', 'ほ', 'ま', 'ろ', '〜'], ['ゅ', 'ゃ', 'ふ', 'ょ', 'ぉ'], ['ぽ', 'ぼ', 'ぶ', 'ぷ', 'ゎ']],
     [['っ', 'う', 'す', 'ら', 'へ'], ['ぇ', 'ヴ', 'ず', 'ぢ', 'べ'], ['み', 'あ', 'え', 'ち', 'ぬ']]]
]

char_map=dict()

for (row_idx, _row) in enumerate(char_set):
    for (left_right_idx, left_right) in enumerate(_row):
        for (shift_idx, shift) in enumerate(left_right):
            for(col_idx, _col) in enumerate(shift):
                char_map[_col] = CharInfo(row=row_idx, left_right=left_right_idx, shift=shift_idx, col=col_idx)


QUESTION_ROW = 12
ANSWER_ROW = 13


def rectangle(win, uly, ulx, lry, lrx):
    """Draw a rectangle with corners at the provided upper-left
    and lower-right coordinates.
    """
    win.vline(uly+1, ulx, curses.ACS_VLINE, lry - uly - 1)
    win.hline(uly, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
    win.hline(lry, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
    win.vline(uly+1, lrx, curses.ACS_VLINE, lry - uly - 1)
    win.addch(uly, ulx, curses.ACS_ULCORNER)
    win.addch(uly, lrx, curses.ACS_URCORNER)
    win.addch(lry, lrx, curses.ACS_LRCORNER)
    win.addch(lry, ulx, curses.ACS_LLCORNER)

KEY_WIDTH = 4
KEY_HEIGHT = 3

KEY_N_COL = 5
KEY_N_ROW = 4

KBD_CENTER_WIDTH = 3

KBD_WIDTH = KEY_WIDTH*KEY_N_COL + KBD_CENTER_WIDTH + KEY_WIDTH*KEY_N_COL + 1
KBD_HEIGHT = KEY_HEIGHT*KEY_N_ROW


class Trainer:

    def __init__(self, win, args):
        self.win = win
        self.args = args
        (_, width) = self.win.getmaxyx()
        self.kbd_win = curses.newwin(KBD_HEIGHT, KBD_WIDTH+KEY_WIDTH+1, 0, int(width/2)-int(KBD_WIDTH/2))
        self.candidates = self.build_candidate()

    def build_candidate(self):
        hands = []
        if self.args.hands == 'both':
            hands = [0,1]
        elif self.args.hands == 'left':
            hands = [0]
        else:
            hands = [1]

        if self.args.all_chars:
            hands = [0,1]
            self.args.normal_shift = True
            self.args.cross_shift = True

        steps = [self.args.upper, self.args.middle, self.args.lower]
        candidates = ""
        for h in hands:
            for i in range(0, len(steps)):
                if steps[i]:
                    candidates = candidates + "".join([c for c in char_set[i][h][0] if c != '　'])
                    if self.args.normal_shift:
                        candidates = candidates + "".join([c for c in char_set[i][h][1] if c != '　'])
                    if self.args.cross_shift:
                        candidates = candidates + "".join([c for c in char_set[i][h][2] if c != '　'] )
        return candidates

    def draw_keyboard(self, target_char):
        shift_state = 0
        if target_char in char_map:
            info = char_map[target_char]
            shift_state = info.shift
        # 左
        for col in range(0, KEY_N_COL):
            for row in range(0, KEY_N_ROW-1):
                (y_1, x_1) = (row*KEY_HEIGHT, col*KEY_WIDTH)
                (y_2, x_2) = ((row+1)*KEY_HEIGHT, (col+1)*KEY_WIDTH)

                rectangle(self.kbd_win, y_1, x_1, y_2-1, x_2-1)

        for col in range(0, KEY_N_COL):
            for row in range(0, KEY_N_ROW-1):
                (y_1, x_1) = (row*KEY_HEIGHT+1, col*KEY_WIDTH+1)
                self.kbd_win.addch(y_1, x_1, char_set[row][0][shift_state][col])

        # 右
        for col in range(0, KEY_N_COL+1):
            for row in range(0, KEY_N_ROW-1):
                (y_1, x_1) = (row*KEY_HEIGHT, KEY_N_COL*KEY_WIDTH+KBD_CENTER_WIDTH+col*KEY_WIDTH)
                (y_2, x_2) = ((row+1)*KEY_HEIGHT, KEY_N_COL*KEY_WIDTH+KBD_CENTER_WIDTH+(col+1)*KEY_WIDTH)


                rectangle(self.kbd_win, y_1, x_1, y_2 - 1, x_2 - 1)

        # シフトキー部分の□を描画
        (l_y_1, l_x_1) = (3*KEY_HEIGHT, (KEY_N_COL-1)*KEY_WIDTH+0*KEY_WIDTH)
        (l_y_2, l_x_2) = (4*KEY_HEIGHT, (KEY_N_COL-1)*KEY_WIDTH+1*KEY_WIDTH)

        rectangle(self.kbd_win, l_y_1, l_x_1, l_y_2-1, l_x_2-1)

        (r_y_1, r_x_1) = (3*KEY_HEIGHT, KEY_N_COL*KEY_WIDTH+KBD_CENTER_WIDTH+0*KEY_WIDTH)
        (r_y_2, r_x_2) = (4*KEY_HEIGHT, KEY_N_COL*KEY_WIDTH+KBD_CENTER_WIDTH+1*KEY_WIDTH)

        rectangle(self.kbd_win, r_y_1, r_x_1, r_y_2-1, r_x_2-1)

        # シフトキーをハイライト表示
        if shift_state == 0:
            self.kbd_win.addch(l_y_1+1, l_x_1+1, '　', curses.A_NORMAL)
            self.kbd_win.addch(r_y_1+1, r_x_1+1, '　', curses.A_NORMAL)
        elif shift_state == 1:
            self.kbd_win.addch(l_y_1+1, l_x_1+1, '　', curses.A_REVERSE)
            self.kbd_win.addch(r_y_1+1, r_x_1+1, '　', curses.A_NORMAL)
        elif shift_state == 2:
            self.kbd_win.addch(r_y_1+1, r_x_1+1, '　', curses.A_REVERSE)
            self.kbd_win.addch(l_y_1+1, l_x_1+1, '　', curses.A_NORMAL)


        for row in range(0, KEY_N_ROW-1):
            col_range = range(0, KEY_N_COL+1) if row == 1 else range(0, KEY_N_COL)
            for col in col_range:
                (y, x) = (row*KEY_HEIGHT+1, KEY_N_COL*KEY_WIDTH+KBD_CENTER_WIDTH+col*KEY_WIDTH+1)
                char = char_set[row][1][shift_state][col]
                self.kbd_win.addch(y, x, char)

        if target_char in char_map:
            info = char_map[target_char]
            x = (KEY_N_COL*KEY_WIDTH+KBD_CENTER_WIDTH)*info.left_right + info.col*KEY_WIDTH + 1
            y = info.row*KEY_HEIGHT + 1
            self.kbd_win.addch( y, x, target_char, curses.A_REVERSE)


    def generate_question(self):
        (_, width) = self.win.getmaxyx()
        question = ""
        for _ in range(0, int(width/2) - 1):
            question = question + random.choice(list(self.candidates))
        return question

    def run(self):
        pos = 0
        curses.noecho()
        logger.debug(self.candidates)
        question = self.generate_question()
        for i, char in enumerate(question):
            self.win.addch(QUESTION_ROW, i*2, char)
        while True:
            if pos >= len(question):
                pos = 0
                question = self.generate_question()
                for i, char in enumerate(question):
                    self.win.addch(QUESTION_ROW, i*2, char)
                    self.win.addch(ANSWER_ROW, i*2, '　')
                continue
            now_char = question[pos]
            self.draw_keyboard(now_char)
            self.kbd_win.refresh()

            ch = self.win.get_wch(ANSWER_ROW, pos*2)

            if isinstance(ch, int):
                continue
            if ch == curses.ascii.BS:
                continue
            if ord(ch) == curses.ascii.BEL:
                break

            self.win.addch(QUESTION_ROW, pos*2, now_char)

            if now_char == ch:
                self.win.addch(ANSWER_ROW, pos*2, ch)
            else:
                curses.beep()
                self.win.addch(ANSWER_ROW, pos*2, ch, curses.A_REVERSE)

            pos += 1
            self.win.refresh()
        return 0, ''

def parse_args(parser):
    parser.add_argument('-u', '--upper', dest='upper', action='store_true',
                        default=False,
                        help='上段を追加')
    parser.add_argument('-m', '--middle', dest='middle', action='store_true',
                        default=False,
                        help='中段を追加')
    parser.add_argument('-l', '--lower', dest='lower', action='store_true',
                        default=False,
                        help='下段を追加')

    parser.add_argument('-H', '--hands', dest='hands', type=str, default='both', choices=['left', 'right', 'both'],
                        help='使用する手')
    parser.add_argument('-N', '--enable_normal_shift', dest='normal_shift', action='store_true',
                        default=False,
                        help='正シフトの音を追加')
    parser.add_argument('-X', '--enable_cross_shift', dest='cross_shift', action='store_true',
                        default=False,
                        help='クロスシフトの音を追加')
    parser.add_argument('-A', '--all-chars', dest='all_chars', action='store_true', default=False,
                        help='すべての音を追加')
    parser.add_argument('-n', '--number_words', dest='n_words', type=int, default=10,
                        help='練習する語数')
    parser.add_argument('-o', '--output_dir', dest='out_dir', type=str, default='./logs',
                        help='ログの出力先')

    return (parser, parser.parse_args())


if __name__ == '__main__':
    def winmain(stdscr, args):
        '''
        aa
        '''
        (height, width) = stdscr.getmaxyx()
        logger.debug("height,width")
        logger.debug((height, width))

        if height < ANSWER_ROW + 1:
            return -1, "screen height too small"

        if width < KEY_N_COL*KEY_WIDTH*2+KBD_CENTER_WIDTH:
            return -1, "screen width too small"

        stdscr.refresh()
        return Trainer(stdscr, args).run()


    def main():
        logger.debug("started")
        parser = argparse.ArgumentParser()
        parser, args = parse_args(parser)

        if (args.upper or args.middle or args.lower) == False:
            parser.print_help()
            exit(-1)


        code, msg = curses.wrapper(winmain, args)
        if code < 0:
            print(msg)
            exit(code)
    main()
