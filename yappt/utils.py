"""Misc util functions."""
import curses
import logging
from pyfiglet import Figlet

logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, filename='yappt.log',
                    format=logformat)  # datefmt="%Y-%m-%d %H:%M:%S"

LOGGER = logging.getLogger(__name__)


def count_widgets_in_stack(bg_stack) -> int:
    LOGGER.debug(f" passed stack = {bg_stack}")
    if not bg_stack :
        return 0

    counter = 0
    for bgw in bg_stack:
        counter += 1  # count the background one
        if bgw.foreground_widgets:
            LOGGER.debug(f' nested stack = {bgw.foreground_widgets}')
            counter = counter + len(bgw.foreground_widgets)
    LOGGER.debug(f'bg_stack_widgets = {counter}')

    return counter

def print_color_swatch():

    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    maxy, maxx = stdscr.getmaxyx()
    maxx = maxx - maxx % 5
    x = 0
    y = 1
    try:
        for i in range(0, curses.COLORS):
            stdscr.addstr(y, x, '{0:5}'.format(i), curses.color_pair(i))
            x = (x + 5) % maxx
            if x == 0:
                y += 1
    except curses.error:
        pass
    stdscr.noutrefresh()
    curses.doupdate()
    stdscr.getch()
    curses.nocbreak()
    curses.endwin()

def print_figfonts():
    stdscr = curses.initscr()
    _, width = stdscr.getmaxyx()
    curses.endwin()

    f = Figlet(width=width)
    for font in f.getFonts():
        f.setFont(font=font)
        print(f'{font}:')
        print(f.renderText(font))
