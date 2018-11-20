"""Screen object for partitioning screen and rendering widgets."""

import collections
import curses
import logging

from .renderers import render_content, render_header_footer
from .widget import Widget

logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, filename='yappt.log',
                    format=logformat)  # datefmt="%Y-%m-%d %H:%M:%S"

LOGGER = logging.getLogger(__name__)


def create_windows_from_cells(widget, parent_win, v_margin, h_margin):
    """Return a list of sub-windows with the appropriate dimensions and locations."""
    active_cells = widget.active_cells
    sub_windows = []
    num_rows = len(active_cells)
    #v_ and h_ margin already applied at this point, so it's not the whole sreen
    parent_height, parent_width = parent_win.getmaxyx()
    row_height = parent_height // num_rows
    index = 0
    for row_counter, row in enumerate(active_cells):
        for cell_counter, cell in enumerate(row):
            cell_width = parent_width // len(row)
            if cell:
                LOGGER.debug(f'index = {index}')
                LOGGER.debug(f'widget.body.formats = {widget.body.formats}')
                h = row_height - widget.body.formats[index].t_margin - widget.body.formats[index].b_margin
                w = cell_width - widget.body.formats[index].l_margin - widget.body.formats[index].r_margin
                y = v_margin + row_height * row_counter + widget.body.formats[index].t_margin
                x = h_margin + cell_width * cell_counter + widget.body.formats[index].l_margin
                LOGGER.debug(f'subwin: h={h}, w={w}, y={y}, x={x}')
                # if it's the last row then use up all remaining space on the screen.
                # this uses up any fractional remainers that might have added to extra
                # lines in previous rows.
                if row_counter == len(active_cells) - 1:
                    h = (parent_height - row_height * (len(active_cells)-1)) - widget.body.formats[index].t_margin - widget.body.formats[index].b_margin
                cell_win = curses.newwin(h, w, y, x)
                sub_windows.append(cell_win)

            if not widget.settings.incremental:
                index += 1
    return sub_windows


class Screen:
    """Context manager for writing to the screen."""

    def __init__(self, *, v_margin: int, h_margin:int):
        self.stdscr = curses.initscr()

        self.v_margin = v_margin
        self.h_margin = h_margin
        # this defines self.window amongst other things.
        self.calibrate()

    def __enter__(self):
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.clear()
        curses.curs_set(0)
        try:
            curses.start_color()
            curses.use_default_colors()

            for i in range(0, curses.COLORS):
                curses.init_pair(i + 1, i, -1)
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
                assert isinstance(widget.body, collections.abc.Iterable)
                assert isinstance(widget.active_cells, tuple)

                # This is written to the inner, margined window
                # generate a list of sub-windows to write each piece of content into.
                sub_windows = create_windows_from_cells(widget, self.window, self.v_margin, self.h_margin)
                assert len(sub_windows) == len(widget.body.cells)
                for sub_win, (body, form) in zip(sub_windows, widget.body):
                    sub_win_height, sub_win_width = sub_win.getmaxyx()
                    if body:
                        line_num = 0
                        for line, parsed_line in render_content(body,
                                                                format_=form,
                                                                height=sub_win_height,
                                                                width=sub_win_width,
                                                                ):
                            LOGGER.debug(f'{line_num} {line}')


                            sub_win.addstr(line_num, # y
                                           0, # x
                                           line,
                                           curses.color_pair(form.color)
                                           )
                            sub_win.noutrefresh()
                            line_num += 1


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
        self.window = curses.newwin(self.scr_height - 2 * self.v_margin,  # height
                                    self.scr_width - 2 * self.h_margin,  # width
                                    1 + self.v_margin ,  # begin_y
                                    self.h_margin)  # begin_x
        self.win_height, self.win_width = self.window.getmaxyx()
