"""Misc util functions."""
import logging
logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, filename='yappt.log',
                    format=logformat)  # datefmt="%Y-%m-%d %H:%M:%S"

LOGGER = logging.getLogger(__name__)


def count_widgets_in_stack(bg_stack) -> int:
    LOGGER.debug(f" passed stack = {bg_stack}")
    if not bg_stack :
        return 0

    counter = 0
    for bgw in bg_stack:
        counter += 1  # count the background one
        if bgw.foreground_widgets:
            LOGGER.debug(f' nested stack = {bgw.foreground_widgets}')
            counter = counter + len(bgw.foreground_widgets)
    LOGGER.debug(f'bg_stack_widgets = {counter}')

    return counter
