"""Misc util functions."""
from typing import Tuple
import logging
logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, filename='yappt.log',
                    format=logformat)  # datefmt="%Y-%m-%d %H:%M:%S"

LOGGER = logging.getLogger(__name__)


def render_header_footer(win, row_num: int, headfoot: tuple):
    """Prints a left, centre and right aligned item to an ncurses window at the row passed."""
    _, winwidth = win.getmaxyx()
    left, centre, right = headfoot

    if left:
        win.addstr(row_num,  # y
                   0,  # x (left-aligned)
                   left,
                   # attr
                   )
    if centre:
        win.addstr(row_num,  # y
                   winwidth // 2 - len(centre) // 2,  # x (centre-aligned)
                   centre,
                   # attr
                   )
    if right:
        win.addstr(row_num,  # y
                   winwidth - len(right) - 1,  # x (right-aligned)
                   right,
                   # attr
                   )


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
