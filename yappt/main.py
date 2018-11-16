"""Main code."""
from collections import deque
from pprint import pprint
import logging
import curses

import click

from .presentation import process_yaml, generate_all_widgets, draw_widget
from .screen import Screen
from .utils import count_widgets_in_stack
from .color_swatch import print_color_swatch

logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, filename='yappt.log',
                    format=logformat)  # datefmt="%Y-%m-%d %H:%M:%S"

LOGGER = logging.getLogger(__name__)

def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))

@click.command()
@click.option('--colors', '-c', 'colors', default=False, flag_value=True, help='Print color palette and exit.')
@click.option('--debug', '-d', 'debug', default=False, flag_value=True, help='Print debug output.')
@click.option('--show', '-s', 'filename', type=click.File('r'), help='Display a presentation.')
def main(filename, debug, colors):
    """Yet Another PowerPoint Tool / YAPPT Ain't PowerPoint."""

    if not filename and not colors:
        print_help_msg(main)
        quit(0)

    if colors:
        print_color_swatch()
        quit(0)

    # --- load ----
    metadata, settings, slides = process_yaml(filename)

    # generate all widgets from the slides

    widgets = generate_all_widgets(slides)

    # --- run presentation loop ---
    # Due to the need to redraw decrementally when moving back through the deck
    # this section is a bit complicated. It relies on a 2-stack arrangment.
    # The background_widget's stack only holds a stack of these widgets that are
    # responsible for drawing the header/footer/ etc of every _slide_.
    # Then, *within* each background widget is another stack holding the foreground
    # widgets (slide sections) that are rendered on top of that background slide.
    #
    # We push and pop as we go back and forth. and then reply on count_widgets_in_stack()
    # to maintain our reference to the current widget in the deque.

    background_widgets = deque()
    background_widgets.append(widgets[0])

    with Screen(v_margin=settings.v_margin, h_margin=settings.h_margin) as screen:
        while True:
            # get the current index but counting the total on the stack
            cur_widget_idx = count_widgets_in_stack(background_widgets) - 1
            # draw the current widget to the buffer
            draw_widget(cur_widget_idx, widgets, background_widgets, screen)
            #update the screen
            screen.print()
            # reset the widget indes as the draw above might pushed to stack
            cur_widget_idx = count_widgets_in_stack(background_widgets) - 1

            ### Now check for keys...
            key = screen.wait_for_keyboard_entry()

            if key in [ord(' '), curses.KEY_ENTER, 10, curses.KEY_DOWN, curses.KEY_RIGHT, ord('n'), ord('N')]:
                ### NEXT SLIDE/WIDGET
                LOGGER.debug("Forward pressed. Moving forward 1 slide/widget...")
                # append the next widget onto the appropriate stack
                # but only if we're not at the end of the deck.
                if cur_widget_idx + 1 <= len(widgets) - 1:
                    if widgets[cur_widget_idx + 1].type_ == 'background':
                        background_widgets.append(widgets[cur_widget_idx + 1])
                    else:
                        background_widgets[-1].foreground_widgets.append(widgets[cur_widget_idx + 1])
                continue

            if key in [curses.KEY_UP, curses.KEY_LEFT, ord('p'), ord('P')]:
                ### PREVIOUS SLIDE/WIDGET
                LOGGER.debug("Back pressed. Moving back 1 slide/widget...")
                # move backward... a little more complicated...
                # handle the edge case first.
                if cur_widget_idx < 2:
                    continue  # we're at the beginning of the deck

                # if the length of the latest background widget's children stack
                # is one, then the we need to go back to previous background
                # widget and redraw from there
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
                else:  # we just need to redraw from the current background widget
                    # up to but _excluding_ the current foreground widget.
                    background_widgets[-1].foreground_widgets.pop()
                    screen.clear()
                    screen.render(background_widgets[-1])
                    for w in background_widgets[-1].foreground_widgets:
                        screen.render(w)
                screen.print()
                continue

            if key == ord('q') or key == ord('Q'):
                ### QUIT
                LOGGER.debug("Q pressed. Quitting...")
                quit(0)


            if key == ord('r') or key == ord('R'):
                ### RELOAD YAML FILE
                LOGGER.debug("R pressed. Reloading file...")
                # save off the previous silde num to we can count to it.
                prev_slide_num = widgets[cur_widget_idx].slide_num
                # reload the file.
                metadata, settings, slides = process_yaml(filename)
                # generate the widgets from the slides
                widgets = generate_all_widgets(slides)
                # reset the stack
                background_widgets = deque()
                # and load the first widget
                background_widgets.append(widgets[0])

                # reset the current widget to the newly loaded widget list
                cur_widget_idx = count_widgets_in_stack(background_widgets) - 1
                # now, we keep drawing to the screen until
                # we get to the previous slide we were on.
                while widgets[cur_widget_idx].slide_num < prev_slide_num:
                    # rescount the current widget index at the top of the loop
                    cur_widget_idx = count_widgets_in_stack(background_widgets) - 1
                    # draw the widget, noting that this might draw more than 1 widget.
                    draw_widget(cur_widget_idx, widgets, background_widgets, screen)
                    # get the correct widget index after the draw
                    cur_widget_idx = count_widgets_in_stack(background_widgets) - 1
                    if cur_widget_idx + 1 <= len(widgets) - 1:
                        if widgets[cur_widget_idx + 1].type_ == 'background':
                            background_widgets.append(widgets[cur_widget_idx + 1])
                        # else:
                        #     background_widgets[-1].foreground_widgets.append(widgets[cur_widget_idx + 1])
                 # then we write the screen
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

    # --- debug ----

    if debug:
        # print(pres)
        print('====DEBUG====')
        print('----METADATA----')
        pprint(metadata)
        print('----SETTINGS----')
        pprint(settings)
        print('----SLIDES----')
        pprint(slides)
        print('----WIDGETS----')
        pprint(widgets)
