"""Main code."""
from collections import deque
from pprint import pprint

import click
import yaml

from .metasettings import Settings, MetaData
from .exceptions import YAMLParseError
from .slide import Slide
from .widget import generate_widgets

@click.command()
@click.argument('filename', type=click.File('r'))
@click.option('--debug', 'debug', default=False, flag_value=True, help='Print debug output.')
def main(filename, debug):
    """Yet Another PowerPoint Tool."""
    # --- load ----
    try:
        pres_dict = yaml.load(filename.read())
    except yaml.YAMLError as exc:
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark  # pylint: disable=no-member
            yp = YAMLParseError(f'Line {mark.line}. Could not load presentation: {filename.name}.')
            yp.show()
            quit(yp.exit_code)

    # --- lint and parse yaml ----
    metadata = MetaData(**pres_dict['metadata'])
    settings = Settings(**pres_dict['settings'])
    slides = []
    widgets = deque()

    # load each slide into a slide list for later processing.
    # this relies on 3.7's ordered dicts by default.
    for s_name, s_data in \
        {k: v for k, v in pres_dict.items() if k not in ['metadata', 'settings']}.items():
        slides.append(Slide(s_name, s_data, settings, metadata))

    # generate all widgets from the slide using the slide and front-matter as input.
    # append the widgets in order to the widgets list
    for slide_num, slide in enumerate(slides):
        widgets.extend(generate_widgets(slide, slide_num, len(slides)))


    # --- run presentation loop ---
    # widget could be a whole slide, or pieces of it (e.g. bullets) we assume the
    # parsing parses into widgets, not slides for easier rendering logic.

    current_widget = 0
    # while True:
    #    see https://github.com/kneufeld/consolemd
    #   or https: // github.com/cpascoe95/vmd
    #   or https://github.com/axiros/terminal_markdown_viewer
        # if not widget.wait_for_keypress:
        #     print widget
        #     current_widget += 1
        #     continue
        # else:
        #     print widget
        #     show widget
        # wait for input(keyboard, or screen resize, or filechange)
        # if keypressed:
        #     if key in [n, <space > , <enter > , <right > , <down > ]:
        #         current_widget += 1  # check for last
        #         continue
        #     if key in [p, , < left > , < up > ]:
        #         current_widget -= 1 # check for first
        #         continue
        #     if key == 'b'
        #         blank screen
        #     if key == 'q'
        #         quit
        #     if key == 'r'
        #         reload file
        #         continue
        #     if key is a positive integer:
        #         current_widget = first widget of slide which is equal to key

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
