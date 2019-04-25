
import curses
import curses.ascii
import locale


locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')

scr = curses.initscr()
scr.clear()
curses.noecho()
x = []

while True:
    ch = scr.getch()
    if ch == curses.ascii.BEL:
        break
    if curses.ascii.isascii(ch):
        continue
    if ch == curses.ascii.BS:
        continue
    x.append(ch)
    scr.refresh()
# here implement simple code to wait for user input to quit

for c in x:
    print(c)
