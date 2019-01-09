"""Main code."""
import curses
import logging
from collections import deque

import click

from .presentation import draw_widget, generate_all_widgets, process_yaml
from .screen import Screen
from .utils import count_widgets_in_stack, print_color_swatch, print_figfonts

logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, filename='yappt.log',
                    format=logformat)  # datefmt="%Y-%m-%d %H:%M:%S"

LOGGER = logging.getLogger(__name__)


@click.group()
def main():
    """Yet Another PowerPoint Tool / YAPPT Ain't PowerPoint."""

@main.command()
def figlet():
    """Print figlet font examples."""
    print_figfonts()
    quit(0)


@main.command()
def colors():
    """Print color swatch."""
    print_color_swatch()
    quit(0)


@main.command()
@click.argument('filename', type=click.File('r'))
def show(filename):
    """Present the slide show."""
    # --- load ----
    metadata, settings, slides = process_yaml(filename)

    # generate all widgets from the slides
    widgets = generate_all_widgets(slides)

    # --- run presentation loop ---

    # Due to the need to redraw decrementally when moving back through the deck
    # this section is a bit complicated. It relies on a 2-stack arrangment.
    # The background_widget's stack only holds a stack of these widgets that
    # are responsible for drawing the header/footer/ etc of every _slide_.
    # Then, *within* each background widget is another stack holding the
    # foreground widgets (slide sections) that are rendered on top of that
    # background slide.
    #
    # We push and pop as we go back and forth. and then reply on
    # count_widgets_in_stack() to maintain our reference to the current widget
    # in the deque.

    background_widgets = deque()
    background_widgets.append(widgets[0])

    with Screen(v_margin=settings.v_margin,
                h_margin=settings.h_margin) as screen:

        while True:
            # get the current index but counting the total on the stack
            cur_widget_idx = count_widgets_in_stack(background_widgets) - 1
            # draw the current widget to the buffer
            draw_widget(cur_widget_idx, widgets, background_widgets, screen)
            # update the screen
            screen.print()
            # reset the widget indes as the draw above might pushed to stack
            cur_widget_idx = count_widgets_in_stack(background_widgets) - 1

            # Now check for keys...
            key = screen.wait_for_keyboard_entry()

            if key in [ord(' '),
                       curses.KEY_ENTER,
                       10,
                       curses.KEY_DOWN,
                       curses.KEY_RIGHT,
                       ord('n'),
                       ord('N'),
                       ord('j'),
                       ord('l')]:
                # NEXT SLIDE/WIDGET
                LOGGER.debug("Fwd pressed. Moving forward 1 slide/widget...")
                # append the next widget onto the appropriate stack
                # but only if we're not at the end of the deck.

                if cur_widget_idx + 1 <= len(widgets) - 1:
                    if widgets[cur_widget_idx + 1].type_ == 'background':
                        background_widgets.append(widgets[cur_widget_idx + 1])
                    else:
                        background_widgets[-1].foreground_widgets\
                            .append(widgets[cur_widget_idx + 1])

                continue

            if key in [curses.KEY_UP,
                       curses.KEY_LEFT,
                       ord('p'),
                       ord('P'),
                       ord('h'),
                       ord('k')]:
                # PREVIOUS SLIDE/WIDGET
                LOGGER.debug("Back pressed. Moving back 1 slide/widget...")

                # move backward... a little more complicated...
                # handle the edge case first.

                if cur_widget_idx < 2:
                    continue  # we're at the beginning of the deck

                # if the length of the latest background widget's children
                # stack is one, then the we need to go back to previous
                # background widget and redraw from there

                if len(background_widgets[-1].foreground_widgets) == 1:
                    # empty this background's widget's list of rendered
                    # foregrounds first, as this is by reference.
                    background_widgets[-1].foreground_widgets = deque()
                    # now get rid of the latest background
                    background_widgets.pop()
                    screen.clear()
                    screen.render(background_widgets[-1])

                    for w in background_widgets[-1].foreground_widgets:
                        screen.render(w)
                else:
                    # we just need to redraw from the current background widget
                    # up to but _excluding_ the current foreground widget.
                    background_widgets[-1].foreground_widgets.pop()
                    screen.clear()
                    screen.render(background_widgets[-1])

                    for w in background_widgets[-1].foreground_widgets:
                        screen.render(w)
                screen.print()

                continue

            if key == ord('q') or key == ord('Q'):
                # QUIT
                LOGGER.debug("Q pressed. Quitting...")
                quit(0)

            if key == ord('r') or key == ord('R'):
                # RELOAD YAML FILE
                LOGGER.debug("R pressed. Reloading file...")
                # save off the previous silde num to we can count to it.
                prev_slide_num = widgets[cur_widget_idx].slide_num
                # reload the file.
                metadata, settings, slides = process_yaml(filename)
                # re-initialise the screen
                screen.h_margin = settings.h_margin
                screen.v_margin = settings.v_margin
                screen.calibrate()
                # generate the widgets from the slides
                widgets = generate_all_widgets(slides)
                # reset the stack
                background_widgets = deque()

                for widget in widgets:
                    if widget.type_ == 'background':
                        background_widgets.append(widget)
                    else:
                        background_widgets[-1].foreground_widgets\
                            .append(widget)

                    if background_widgets[-1].slide_num == prev_slide_num:
                        break

                screen.print()

                continue

            if key == curses.KEY_RESIZE:
                # REDRAW
                # window got resized, so re-draw
                LOGGER.debug("Terminal size changed. Refreshing screen...")
                screen.calibrate()
                screen.render(background_widgets[-1])

                for w in background_widgets[-1].foreground_widgets:
                    screen.render(w)
                screen.print()

