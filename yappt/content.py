"""Class for managing the content part of a slide."""
import logging
import curses

from .format import Format, DEFAULT_FORMAT
from .validator_mixins import ValIsDictHasSubKeysMixIn, ValIsDictSubKeysFromMixIn
from .exceptions import FormatError

LOGGER = logging.getLogger(__name__)


class Content(ValIsDictHasSubKeysMixIn, ValIsDictSubKeysFromMixIn):
    def __init__(self, payload, *args, **kwargs):
        super().__init__(payload, *args, **kwargs) # run mixin validations
        content = payload['content']

        self.body = content['body']

        if isinstance(content['body'], list):
            self.body = content['body']
        else:
            self.body = [content['body']]  # make it a list with 1 item

        self.format_ = Format(content,
                             _key='format',
                             _exception=FormatError,
                             _elem=f"slide {kwargs['_elem']}, format section",
                             _keys_from=['justify', 'color', 'wordwrap', 'margin', 'type'],
                             _type_list=[str, int, bool, str, str]
                             )

class Body:
    """Represents the body item inside a slide content."""

    def __init__(self, body_payload, parent_format):
        # TODO add better error handling.
        self.formats = []
        self.cells = []
        if isinstance(body_payload, str):
            # vanilla body
            self.formats = [parent_format]
            self.cells = [body_payload]
        elif isinstance(body_payload, list):
            # list of stuff
            for item in body_payload:
                LOGGER.debug(item)
                try:
                    self.formats.append(create_cell_format(item, parent_format))
                except (AttributeError, TypeError):
                    self.formats.append(parent_format)

                try:
                    self.cells.append(item['cell'])
                except (AttributeError, TypeError):
                    self.cells.append(item)

        elif isinstance(body_payload, dict):

            if body_payload.get('format'):
                assert body_payload.get('cell') is not None  # TODO, throw better error message
                self.formats.append(create_cell_format(body_payload, parent_format))
            else:
                self.formats.append(parent_format)

            if body_payload.get('cell'):
                assert body_payload.get('format') is not None  # TODO, throw better error message
                self.cells.append(body_payload['cell'])
            else:
                self.cells.append(body_payload)

    def __iter__(self):
        """Return an iterable which is a tuple of content and format iterables."""
        for cel, form in zip(self.cells, self.formats):
            yield (cel, form)
        #return iter()


    # def gen_color_pair(self, index):
    #     """Generates a curses-compatible color-pair to be passed into addstr()."""
    #     return curses.color_pair(self.formats[index].color)


def create_cell_format(body_payload, parent_format):
    """Create a format object for a cell by merging parent and cell formats."""
    if not isinstance(body_payload, str) and body_payload.get('format'):
        # instantiate a Format object to do the type checking.
        _ = Format(body_payload,
                   _key='format',
                   _elem='body',
                   _exception=FormatError,
                   _keys_from=['justify', 'color', 'wordwrap', 'margin', 'type'],
                   _type_list=[str, int, bool, str, str]
                   )
        # now create a new format input that applies the cell's format on top of slide format.

        # get all the stuff in the slide format that is not a derived field
        bare_format_dict = {k: v for k, v in vars(parent_format).items() if k not in ('l_margin', 'r_margin', 't_margin', 'b_margin')}
        # get all the stuff in the slide format that is not a default.
        non_default_slide_format = {k: v for k, v in bare_format_dict.items() if v != DEFAULT_FORMAT[k]}
        LOGGER.debug(f'non_default_slide_format={non_default_slide_format}')

        # get all the stuff in the cell format that overrides the slide format.
        overriding_cell_format = {k: v for k, v in body_payload['format'].items() if v != vars(parent_format)[k]}
        LOGGER.debug(f'non_default_cell_format={overriding_cell_format}')

        # merge the 2 formats, with the cell formats overriding.
        merged_format = {**non_default_slide_format, **overriding_cell_format}

        # overlay this new format over the default list to create the new format.
        new_format = {'format': {**DEFAULT_FORMAT, **merged_format}}
        LOGGER.debug(f'newformat = {new_format}')
        # finaly, create a new format object to be used in the remainder of the function.

        return Format(new_format,
                    _key='format',
                    _elem='body',
                    _exception=FormatError,
                    _keys_from=['justify', 'color', 'wordwrap', 'margin', 'type'],
                    _type_list=[str, int, bool, str, str]
                    )

    return parent_format
