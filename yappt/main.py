"""Main code."""
from collections import deque, namedtuple
from pprint import pprint

import click
import yaml

from .metasettings import Settings, MetaData
from .exceptions import YAMLParseError, SettingsError

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
    # TODO: improve errorhandling on this - replace namedtuples with real classes/dataclasses
    # TODO: try/except these and throw useful error if they don't parse.
    metadata = MetaData(**pres_dict['metadata'])
    settings = Settings(**pres_dict['settings'])

    parts = deque()

    # relies on 3.7's ordered dicts by default.
    for s_name, s_data in \
        {k: v for k, v in pres_dict.items() if k not in ['meta', 'settings']}.items():

        pass


        # slide = Slide(s_name, s_data)

        #         generate all parts from the slide using the slide and front-matter as input.
        #         append the parts in order to the parts list
        # parts.extend(create_parts_from_slide(slide, meta, settings))


    # --- run presentation loop ---
    # part could be a whole slide, or pieces of it (e.g. bullets) we assume the
    # parsing parses into parts, not slides for easier rendering logic.

    current_part = 0
    # while True:
    #     pass
        # print part
        # wait for input(keyboard, or screen resize, or filechange)
        # if keypressed:
        #     if key in [n, <space > , <enter > , <right > , <down > ]:
        #         current_part += 1  # check for last
        #         continue
        #     if key in [p, , < left > , < up > ]:
        #         current_part -= 1 # check for first
        #         continue
        #     if key == 'b'
        #         blank screen
        #     if key == 'q'
        #         quit
        #     if key == 'r'
        #         reload file
        #         continue
        #     if key is a positive integer:
        #         current_part = first part of slide which is equal to key

    # --- debug ----

    if debug:
        # print(pres)
        pprint(metadata)
        pprint(settings)
