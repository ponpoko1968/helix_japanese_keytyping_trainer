import curses
import curses.ascii
import locale
import logging
import logging.handlers

logger = logging.getLogger('MyLogger')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler("filename.log"))

locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
code = locale.getpreferredencoding()


char_set = [

    [[['な','て','せ','そ'], ['ぺ','け','よ','ー'], ['ぱ','げ','で','ぜ','ぞ']],[['・','お','の','に',''],['ひ','き','つ',],['び','ぎ','づ']]],

    [[['こ','た','か','る','は'], ['め','や','も','さ','ぅ'], ['ご','だ','が','ざ','ば']],[['ー','ん','い','し','と'],['む','れ','く','り','わ','ね'],['ぃ','ぁ','ぐ','じ','ど','ぴ']]],

    [[['ゆ','ほ','ま','ろ'], ['ゅ','ゃ','ふ','ょ','ぉ'], ['ぽ','ぼ','ぶ','ぷ','ゎ']],[['っ','う','す','ら','へ'],['み','あ','え','ち','ぬ'],['ぇ','う゛','ず','ぢ','べ']]]

]

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
        self.win.addch(1,left_margin+0,"こ",curses.A_REVERSE)
        pos = 0
        curses.noecho()
        while True:
            ch = self.win.get_wch(8, left_margin + pos)
            if isinstance(ch,int):
                continue
            if ch == curses.ascii.BS:
                continue
            if ord(ch) == curses.ascii.BEL:
                break
            # if curses.ascii.isascii(ch):
            #     continue
            self.win.addch(8, left_margin + pos, ch)
            logger.debug(ch)
            #self.win.addstr(8, left_margin + pos, str(ch).encode('utf-8'))
            #self.win.border(8, left_margin + pos, ch)
            pos += 2
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

