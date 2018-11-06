"""Misc util functions."""
from typing import Tuple
import curses
import logging
logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, filename='yappt.log',
                    format=logformat)  # datefmt="%Y-%m-%d %H:%M:%S"

LOGGER = logging.getLogger(__name__)


def explode_layout_string(layout: str) -> Tuple:
    # here we explode the string into a tuple of tuples like so:
    # '1-2-3-2-1' -> ((0),(0,0),(0,0,0),(0,0),(0)) where 0 is actually `False`
    assert isinstance(layout, str)
    layout_flat = tuple(map(int, layout.split('-')))

    layout_nested: list = []
    for item in layout_flat:
        layout_nested.append(tuple([False for _ in range(item)]))

    return tuple(layout_nested)

def create_active_cells(layout: Tuple, actives: Tuple):
    # here we take the exploded tuple of tuple layout field and turn those cells which are active to True:
    # so  ((0),(0,0),(0,0,0),(0,0),(0)) -> ((0),(0,0),(1,0,1),(0,0),(0)) give the actives of (3,5)

    counter = 0
    active_cells = []
    for row in layout:
        current_row = []
        for _ in row:
            if counter in actives:
                current_row.append(True)
            else:
                current_row.append(False)
            counter += 1
        row_tup = tuple(current_row)
        active_cells.append(row_tup)
    return tuple(active_cells)

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


def create_windows_from_cells(active_cells, parent_win, margin):
    """Return a list of sub-windows with the appropriate dimensions and locations."""
    sub_windows = []
    num_rows = len(active_cells)
    parent_height, parent_width = parent_win.getmaxyx()
    row_height = parent_height // num_rows
    for row_counter, row in enumerate(active_cells):
        for cell_counter, cell in enumerate(row):
            cell_width = parent_width // len(row)
            if cell:
                cell_win = curses.newwin(row_height,  # height
                                         cell_width,  # width
                                         margin + row_height*row_counter,  # begin_y
                                         margin + cell_width*cell_counter)  # begin_x
                sub_windows.append(cell_win)
    return sub_windows

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
