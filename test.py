import curses
import curses.ascii
import locale
import logging
import logging.handlers
from collections import namedtuple

CharInfo = namedtuple('CharInfo', ('row', 'left_right', 'shift', 'col'))

logger = logging.getLogger('MyLogger')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler("filename.log"))

locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
code = locale.getpreferredencoding()


char_set = [

    [[['。','な','て','せ','そ'], ['ぺ','け','よ','ー',' '], ['ぱ','げ','で','ぜ','ぞ']] ,[['・','お','の','に',' '],[' ','ひ','き','つ',' '],[' ', 'び','ぎ','づ',' ']]],

    [[['こ','た','か','る','は'], ['め','や','も','さ','ぅ'], ['ご','だ','が','ざ','ば']] ,[['ー','ん','い','し','と'],['む','れ','く','り','わ','ね'],['ぃ','ぁ','ぐ','じ','ど','ぴ']]],

    [[['ゆ','ほ','ま','ろ',' '], ['ゅ','ゃ','ふ','ょ','ぉ'], ['ぽ','ぼ','ぶ','ぷ','ゎ']] ,[['っ','う','す','ら','へ'],['み','あ','え','ち','ぬ'],['ぇ','う゛','ず','ぢ','べ']]]

]

char_map=dict()

for (row_idx, row) in enumerate(char_set):
    for (left_right_idx, left_right) in enumerate(row):
        for (shift_idx,shift) in enumerate(left_right):
            for(col_idx,col) in enumerate(shift):
                char_map[col] = CharInfo(row=row_idx, left_right=left_right_idx, shift=shift_idx, col=col_idx)



left_margin = 4

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

class Trainer:
    def __init__(self, win, insert_mode=False):
        self.win = win

    def draw_row(self, win, row_idx, shift):
        row = char_set[row_idx]
        (left, right) = (row[0], row[1])
        for (idx, char) in enumerate(left[shift]):
            win.addch(row_idx, left_margin+idx*2,char)

    def run(self):
        self.draw_row(self.win,1,0)
        pos = 0
        curses.noecho()
        question="たかるはこ"
        for i,ch in enumerate(question):
            self.win.addch(8, left_margin + i*2, ch)
        prev_char=None
        while True:
            if prev_char :
                prev_info=char_map[prev_char]
                self.win.addch(prev_info.row,left_margin+prev_info.col*2,prev_char, curses.A_NORMAL)
            now_char=question[pos % len(question)]
            info=char_map[now_char]
            self.win.addch(info.row,left_margin+info.col*2, now_char, curses.A_REVERSE)
            ch = self.win.get_wch(9, left_margin + pos*2)

            if isinstance(ch,int):
                continue
            if ch == curses.ascii.BS:
                continue
            if ord(ch) == curses.ascii.BEL:
                break
            prev_char=question[pos % len(question)]
            self.win.addch(info.row,left_margin+info.col*2, now_char, curses.A_REVERSE)
            self.win.addch(8, left_margin + pos*2, now_char)
            self.win.addch(8, left_margin + (pos+1)*2, question[(pos+1) % len(question)],curses.A_REVERSE)

            if now_char == ch:
                self.win.addch(9, left_margin + pos*2, ch)
            else:
                self.win.addch(9, left_margin + pos*2, ch,curses.A_REVERSE)

            logger.debug(ch)
            #self.win.addstr(8, left_margin + pos, str(ch).encode('utf-8'))
            #self.win.border(8, left_margin + pos, ch)
            pos += 1
            self.win.refresh()

if __name__ == '__main__':
    def test(stdscr):
        ncols, nlines = 24, 3
        uly, ulx = 3, 3
        #stdscr.addstr(uly-2, ulx, "Use Ctrl-G to end editing.")
        win = curses.newwin(nlines, ncols, uly, ulx)
        #rectangle(stdscr, uly-1, ulx-1, uly + nlines, ulx + ncols)
        stdscr.refresh()

        logger.debug("started")
        return Trainer(stdscr).run()

curses.wrapper(test)

