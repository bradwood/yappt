"""Create Presentation objects from YAML input"""
import logging
from collections import deque
from datetime import date
from typing import List, Tuple

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError

from .exceptions import MetaDataError, SettingsError, YAMLParseError
from .metasettings import MetaData, Settings
from .slide import Slide
from .widget import generate_widgets_from_slide

yaml = YAML()

LOGGER = logging.getLogger(__name__)


def process_yaml(filename) -> Tuple[MetaData, Settings, List[Slide]]:
    """Generate settings, metadata and Slides from input."""
    try:
        filename.seek(0)  # incase we are reloading the file.
        pres_dict = yaml.load(filename.read())
        LOGGER.debug("Loaded YAML")
        LOGGER.debug(pres_dict)
    except (ScannerError, ParserError) as exc:
        yp = YAMLParseError(f'Could not load presentation: {filename.name}.')
        yp.show()
        print(exc)
        quit(yp.exit_code)

    metadata = MetaData(pres_dict,
                        _key='metadata',
                        _exception=MetaDataError,
                        _elem='YAML file',
                        _keys_from=['title', 'author', 'date'],
                        _type_list=[str, str, date],
                        )

    LOGGER.debug("Loaded metadata")

    settings = Settings(pres_dict,
                        _key='settings',
                        _exception=SettingsError,
                        _elem='YAML file',
                        _keys_from=['pagenum', 'titlebar', 'authorfooter',
                                    'date', 'slidetitle', 'incremental',
                                    'h_margin', 'v_margin'],
                        _type_list=[bool, bool, bool,
                                    bool, bool, bool, int, int],
                        )

    LOGGER.debug("Loaded settings")

    slides = []
    # load each slide into a slide list for later processing.
    # this relies on 3.7's ordered dicts by default.

    for s_name, s_data in \
            {k: v for k, v in pres_dict.items() if k
             not in ['metadata', 'settings']}.items():
        slides.append(Slide(s_name, s_data, settings, metadata))

    LOGGER.debug("Created slide list")

    return metadata, settings, slides

def generate_all_widgets(slides):
    """Generate a deque of widgets from a list of slides"""
    widgets = deque()

    for slide_num, slide in enumerate(slides):
        widgets.extend(generate_widgets_from_slide(
            slide, slide_num, len(slides)))
    LOGGER.debug("Created widget list")

    return widgets


def draw_widget(cur_widget_idx, widgets, background_widgets, screen):
    """Draw the  wdiget on the screen."""
    # IF we have a background, draw it and the first foreground together.
    widget = widgets[cur_widget_idx]

    if widget.type_ == 'background':
        # draw the background
        screen.render(widget)
        # every background *MUST* be followed by a foreground so this is okay
        # append the foreground which follows onto this background.
        background_widgets[-1].foreground_widgets.append(
            widgets[cur_widget_idx + 1])
        # now we've done that, we increment current widget by one.
        cur_widget_idx += 1
        # assign the current widget on this basis.
        widget = widgets[cur_widget_idx]
    # else:  # it's a foreground widget so just draw it.
    screen.render(widget)

