"""Screen object for partitioning screen and rendering widgets."""

import curses
from .widget import Widget
from .utils import render_header_footer
import logging
logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, filename='yappt.log',
                    format=logformat)  # datefmt="%Y-%m-%d %H:%M:%S"

LOGGER = logging.getLogger(__name__)


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
                                         margin + (row_height) * row_counter,  # begin_y
                                         margin + (cell_width) * cell_counter)  # begin_x
                sub_windows.append(cell_win)
    return sub_windows


class Screen:
    """Context manager for writing to the screen"""

    def __init__(self, *, margin: int):
        self.stdscr = curses.initscr()
        self.margin = margin
        # this defines self.window amongst other things.
        self.calibrate()

    def __enter__(self):
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.clear()
        try:
            curses.start_color()
        except:
            pass
        return self

    def __exit__(self, typ, val, tb):
        self.stdscr.keypad(False)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def render(self, widget: Widget):
        try:
            if widget.type_ == 'background':
                # This is written to the main, fullsize window
                assert widget.body is None
                assert widget.active_cells is None
                assert isinstance(widget.header, tuple)
                assert isinstance(widget.footer, tuple)

                self.stdscr.clear()
                render_header_footer(self.stdscr, 0, widget.header) # header
                render_header_footer(self.stdscr, self.scr_height - 1, widget.footer) # footer
                #print("rendered background")

            if widget.type_ == 'foreground':
                assert isinstance(widget.body, list)
                assert isinstance(widget.active_cells, tuple)

                # This is written to the inner, margined window
                # generate a list of sub-windows to write each piece of content into.
                sub_windows = create_windows_from_cells(widget.active_cells, self.window, self.margin)
                assert len(sub_windows) == len(widget.body)
                for sub_win, content  in zip(sub_windows, widget.body):
                    # sub_win.box()
                    if content:
                        sub_win.addstr(0,  # y
                                       0,  # x
                                       content,  # str
                                       #att
                                       )

                    sub_win.noutrefresh()
                #print("rendered foreground")

            self.stdscr.noutrefresh()  # mark for refresh.
        except curses.error:
            pass # don't crash on resizes, even if they're stupid.


    def wait_for_keyboard_entry(self):
        ch = self.stdscr.getch()
        LOGGER.debug(f'Char pressed = {ch}')
        return ch

    def clear(self):
        self.stdscr.clear()

    def print(self):
        curses.doupdate()

    def calibrate(self):
        self.scr_height, self.scr_width = self.stdscr.getmaxyx()
        self.window = curses.newwin(self.scr_height - 2 * self.margin,  # height
                                    self.scr_width - 2*self.margin,  # width
                                    self.margin,  # begin_y
                                    self.margin)  # begin_x
        self.win_height, self.win_width = self.window.getmaxyx()
