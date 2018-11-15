import curses


def print_color_swatch():

    def print_stuff(stdscr):
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
    curses.wrapper(print_stuff)
