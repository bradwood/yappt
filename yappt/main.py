"""Main code."""
from collections import deque
from pprint import pprint
import logging
import curses

import click

from .presentation import process_yaml
from .slide import Slide
from .widget import generate_widgets
from .screen import Screen
from .utils import count_widgets_in_stack

logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, filename='yappt.log',
                    format=logformat)  # datefmt="%Y-%m-%d %H:%M:%S"

LOGGER = logging.getLogger(__name__)

@click.command()
@click.argument('filename', type=click.File('r'))
@click.option('--debug', 'debug', default=False, flag_value=True, help='Print debug output.')
def main(filename, debug):
    """Yet Another PowerPoint Tool."""
    # --- load ----
    metadata, settings, slides = process_yaml(filename)
    widgets = deque()
    # generate all widgets from the slide using the slide and front-matter as input.
    # append the widgets in order to the widgets list
    for slide_num, slide in enumerate(slides):
        widgets.extend(generate_widgets(slide, slide_num, len(slides)))
    LOGGER.debug("Created widget list")

    # --- run presentation loop ---
    # Due to the need to redraw decrementally when moving back through the deck
    # this section is a bit complicated. It relies on a 2-stack arrangment.
    # The background_widget's stack only holds a stack of these widgets that are
    # responsible for drawing the header/footer/ etc of every _slide_.
    # Then, *within* each background widget is another stack holding the foreground
    # widgets (slide sections) that are rendered on top of that background slide.
    #
    # We push and pop as we go back and forth. and then reply on count_widgets_in_stack()
    # to maintain our reference to the widgets deque which holds all the data.

    backgound_widgets = deque()
    backgound_widgets.append(widgets[0])
    #    see https://github.com/kneufeld/consolemd
    #   or https: // github.com/cpascoe95/vmd
    #   or https://github.com/axiros/terminal_markdown_viewer

    with Screen(v_margin=settings.v_margin, h_margin=settings.h_margin) as screen:  #TODO make margin into 4 settings
        while True:
            current_widget = count_widgets_in_stack(backgound_widgets) - 1
            widget = widgets[current_widget]

            ### IF we have a background, draw it and the first foreground together.
            if widget.type_ == 'background':
                LOGGER.debug(f'BG render: W{current_widget}')
                screen.render(widget)
                # every background *MUST* be followed by a foreground so this should work.
                backgound_widgets[-1].foreground_widgets.append(widgets[current_widget + 1])
                continue
            else: # it's a foreground widget so just draw it.
                LOGGER.debug(f'FG render: W{current_widget}')
                screen.render(widget)
                screen.print()

            ### Now check for keys...
            key = screen.wait_for_keyboard_entry()

            if key in [ord(' '), curses.KEY_ENTER, 10, curses.KEY_DOWN, curses.KEY_RIGHT, ord('n'), ord('N')]:
                # append the next widget onto the appropriate stack
                # but only if we're not at the end of the deck.
                if current_widget + 1 <= len(widgets) - 1:
                    if widgets[current_widget + 1].type_ == 'background':
                        backgound_widgets.append(widgets[current_widget + 1])
                    else:
                        backgound_widgets[-1].foreground_widgets.append(widgets[current_widget + 1])
                continue

            if key in [curses.KEY_UP, curses.KEY_LEFT, ord('p'), ord('P')]:
                # move backward... a little more complicated...
                # handle the edge case first.
                if current_widget < 2:
                    continue  # we're at the beginning of the deck

                # if the length of the latest background widget's children stack
                # is one, then the we need to go back to previous background
                # widget and redraw from there
                if len(backgound_widgets[-1].foreground_widgets) == 1:
                    # empty this background's widget's list of rendered
                    # foregrounds first, as this is by reference.
                    backgound_widgets[-1].foreground_widgets = deque()
                    # now get rid of the latest background
                    backgound_widgets.pop()
                    screen.clear()
                    screen.render(backgound_widgets[-1])
                    for w in backgound_widgets[-1].foreground_widgets:
                        screen.render(w)
                else:  # we just need to redraw from the current background widget
                    # up to but _excluding_ the current foreground widget.
                    backgound_widgets[-1].foreground_widgets.pop()
                    screen.clear()
                    screen.render(backgound_widgets[-1])
                    for w in backgound_widgets[-1].foreground_widgets:
                        screen.render(w)
                screen.print()
                continue

            if key == ord('q') or key == ord('Q'):
                break

            if key == curses.KEY_RESIZE:
                # window got resized, so re-draw
                screen.calibrate()
                screen.render(backgound_widgets[-1])
                for w in backgound_widgets[-1].foreground_widgets:
                    screen.render(w)
                screen.print()
            # if key == 'r'
            #     reload file
            #     continue
            # if key is a positive integer:
            #     current_widget = first widget of slide which is equal to key

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
