"""Main code."""
from collections import deque
from pprint import pprint
import logging

import click
from ruamel.yaml import YAML
from ruamel.yaml.scanner import ScannerError

from .metasettings import Settings, MetaData
from .exceptions import YAMLParseError
from .slide import Slide
from .widget import generate_widgets
from .screen import Screen
from .utils import count_widgets_in_stack

yaml = YAML()


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
    try:
        pres_dict = yaml.load(filename.read())
        LOGGER.debug("Loaded YAML")
    except ScannerError as exc:
        yp = YAMLParseError(f'Could not load presentation: {filename.name}.')
        yp.show()
        print(exc)
        quit(yp.exit_code)

    # --- lint and parse yaml ----
    metadata = MetaData(**pres_dict['metadata'])
    LOGGER.debug("Loaded metadata")
    settings = Settings(**pres_dict['settings'])
    LOGGER.debug("Loaded settings")
    slides = []
    widgets = deque()

    # load each slide into a slide list for later processing.
    # this relies on 3.7's ordered dicts by default.
    for s_name, s_data in \
        {k: v for k, v in pres_dict.items() if k not in ['metadata', 'settings']}.items():
        slides.append(Slide(s_name, s_data, settings, metadata))
    LOGGER.debug("Created slide list")

    # generate all widgets from the slide using the slide and front-matter as input.
    # append the widgets in order to the widgets list
    for slide_num, slide in enumerate(slides):
        widgets.extend(generate_widgets(slide, slide_num, len(slides)))
    LOGGER.debug("Created widget list")


    # --- run presentation loop ---
    # widget could be a whole slide, or pieces of it (e.g. bullets) we assume the
    # parsing parses into widgets, not slides for easier rendering logic.

    backgound_widgets = deque()
    backgound_widgets.append(widgets[0])
    #    see https://github.com/kneufeld/consolemd
    #   or https: // github.com/cpascoe95/vmd
    #   or https://github.com/axiros/terminal_markdown_viewer

    with Screen(margin=1) as screen:
        while True:
            current_widget = count_widgets_in_stack(backgound_widgets) - 1
            widget = widgets[current_widget]
            LOGGER.debug(f'current widget = {current_widget}')

            ### IF we have a background, draw it and the first foreground together.
            if widget.type_ == 'background':
                LOGGER.debug(f'BG render: W{current_widget}')
                #backgound_widgets.append(widget)  # push onto stack.
                screen.render(widget)
                # every background *MUST* be followed by a foreground so this should work.
                backgound_widgets[-1].foreground_widgets.append(widgets[current_widget+1])
                # if current_widget < len(widgets):
                #     current_widget += 1
                continue
            else: # it's a foreground widget so..
                # then render it.
                LOGGER.debug(f'FG render: W{current_widget}')
                screen.render(widget)
                screen.print()

            ### Now check for keys...
            keypressed = screen.wait_for_keyboard_entry()
            if keypressed in ['KEY_RIGHT', 'KEY_DOWN',' ', 'n']:
                # append the next widget onto the appropriate stack
                try:
                    if widgets[current_widget + 1].type_ == 'background':
                        backgound_widgets.append(widgets[current_widget + 1])
                    else:
                        backgound_widgets[-1].foreground_widgets.append(widgets[current_widget + 1])
                # if current_widget < len(widgets) - 1:
                #     current_widget += 1
                except: # we hit the end of the deck, so do nothing.
                    continue

            if keypressed in ['KEY_LEFT', 'KEY_UP']:
                # move backward... a little more complicated...




                # first handle the end cases
                if current_widget <= 0:
                    current_widget = 0
                    continue  # we are at the first slide
                if current_widget == len(widgets) - 1:
                    continue  # we are at the last slide
                # how handle the middle case....
                # if the length of the latest background widget's children stack
                # is one, then the we need to go back to last background slide and redraw
                # from there
                LOGGER.debug(f'BACK pressed.')
                LOGGER.debug(f'BG Stack {backgound_widgets}.')
                LOGGER.debug(f'Current FG stack {backgound_widgets[-1].foreground_widgets}')
                if len(backgound_widgets[-1].foreground_widgets) == 1:
                    backgound_widgets[-1].foreground_widgets = deque() # empty it first
                    backgound_widgets.pop()  # get rid of the latest background
                    screen.clear()
                    screen.render(backgound_widgets[-1])
                    for w in backgound_widgets[-1].foreground_widgets:
                        screen.render(w)
                        current_widget -= 1
                else:  # we just need to redraw from the current background widget
                    # up to but _excluding_ the current foreground widget.
                    backgound_widgets[-1].foreground_widgets.pop()
                    screen.clear()
                    screen.render(backgound_widgets[-1])
                    for w in backgound_widgets[-1].foreground_widgets:
                        screen.render(w)
                        current_widget -= 1
                screen.print()
                continue
            # if key == 'b'
            #     blank screen
            if keypressed.lower() == 'q':
                break
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
