import curses
from mistletoe import Document
from yappt.curses_renderer import CursesRenderer

md = """one
**text to be strong** and not strong
# Heading1😎

* ~~Fruit~~ items
  * **Apple** curd
  * Orange **red**
    * Banana
    * Banana
      * Banana

1. *Dairy*
    1. Milk _cream_ and ~~blah~~
    2. Cheese
        1. Cheese
2. Blah

> this
> > deeper layer
> > > even deeper layer

## Heading2 _underlined_ thing
Here is some content under this header.

### Heading3 **bold** thing
Here is some content `inline code` this header <http://google.com/> autolink, as does <brad@bradleywood.com>.
Here is some ~~strike_through~~ stuff and this is regular link: [here](http://here.com)

```python
for blah in blah:
    print(blah)
    print(blah)
    print(blah)
    print(blah)
    print(blah)
    print(blah)
    print(blah)
    print(blah)
    print(blah)
```

gdf

    for blah in blah:
        print(blah)
"""


def main(stdscr):
    h, w = stdscr.getmaxyx()
    w = curses.newwin(h, w, 0, 0)
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)


    with CursesRenderer(curses_win=w) as renderer:
        rendered = renderer.render(Document(md))


    # stdscr.addstr(10, 10,'hello', curses.A_LEFT)
    # stdscr.addstr(11, 10, 'hello', curses.A_RIGHT)
    # stdscr.addstr(12, 10, 'hello', curses.A_TOP)
    # stdscr.addstr(13, 10, 'hello', curses.A_UNDERLINE)
    # stdscr.addstr(14, 10, 'hello', curses.A_STANDOUT)
    # stdscr.addstr(15, 10, 'hello', curses.A_HORIZONTAL)
    # stdscr.addstr(16, 10, 'hello', curses.A_VERTICAL)
    # stdscr.addstr(17, 10, 'hello', curses.A_BLINK)
    # stdscr.addstr(18, 10, 'hello', curses.A_BOLD)
    # stdscr.addstr(19, 10, 'hello', curses.A_DIM)
    # stdscr.addstr(20, 10, 'hello', curses.A_INVIS)

    w.noutrefresh()
    curses.doupdate()



curses.wrapper(main)
