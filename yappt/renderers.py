"""Functions to render content widgets/elements."""
import textwrap
import re
import logging
from .format import Format, DEFAULT_FORMAT
from .exceptions import FormatError

LOGGER = logging.getLogger(__name__)

# define a  string sub-class to map our justification methods.
class MyString(str):
    def __init__(self, *args,**kwargs):
        self.left = str.ljust
        self.right = str.rjust
        self.centre = str.center
        self.center = str.center


class DocWrapper(textwrap.TextWrapper):
    """Wrap text in a document, processing each paragraph individually."""

    def wrap(self, text):
        """Override textwrap.TextWrapper to process 'text' properly when
        multiple paragraphs present"""
        para_edge = re.compile(r"(\n\s*\n)", re.MULTILINE)
        paragraphs = para_edge.split(text)
        wrapped_lines = []
        for para in paragraphs:
            if para.isspace():
                if not self.replace_whitespace:
                    # Do not take the leading and trailing newlines since
                    # joining the list with newlines (as self.fill will do)
                    # will put them back in.
                    if self.expand_tabs:
                        para = para.expandtabs()
                    wrapped_lines.append(para[1:-1])
                else:
                    # self.fill will end up putting in the needed newline to
                    # space out the paragraphs
                    wrapped_lines.append('')
            else:
                wrapped_lines.extend(textwrap.TextWrapper.wrap(self, para))
        return wrapped_lines


def render_header_footer(win, row_num: int, headfoot: tuple):
    """Prints a left, centre and right aligned item to an ncurses window at the row passed."""
    _, winwidth = win.getmaxyx()
    left, centre, right = headfoot

    if left:
        win.addstr(row_num,  # y
                   0,  # x (left-aligned)
                   left,
                   # attr
                   )
    if centre:
        win.addstr(row_num,  # y
                   winwidth // 2 - len(centre) // 2,  # x (centre-aligned)
                   centre,
                   # attr
                   )
    if right:
        win.addstr(row_num,  # y
                   winwidth - len(right) - 1,  # x (right-aligned)
                   right,
                   # attr
                   )

def render_content(content, *, format_, height, width):
    """Apply the format to the content string."""
    # algo:
    # - apply type treatment
    # - apply wordwrap
    # - apply justification

    LOGGER.debug(f'render_content: content={content}')
    # # get a format object if one exists at the cell level.
    # if not isinstance(content, str) and content.get('format'):
    #     # instantiate a Format object to do the type checking.
    #     _ = Format(content,
    #                _key='format',
    #                _elem='body',
    #                _exception=FormatError,
    #                _keys_from=['justify', 'color', 'wordwrap', 'margin', 'type'],
    #                _type_list=[str, int, bool, str, str]
    #                )

    #     # now create a new format input that applies the cell's format on top of slide format.

    #     # get all the stuff in the slide format that is not a derived field
    #     bare_format_dict = {k: v for k, v in vars(format_).items() if k not in ('l_margin', 'r_margin', 't_margin', 'b_margin')}
    #     # get all the stuff in the slide format that is not a default.
    #     non_default_slide_format = {k: v for k, v in bare_format_dict.items() if v != DEFAULT_FORMAT[k]}
    #     LOGGER.debug(f'non_default_slide_format={non_default_slide_format}')

    #     # get all the stuff in the cell format that overrides the slide format.
    #     overriding_cell_format = {k: v for k, v in content['format'].items() if v != vars(format_)[k]}
    #     LOGGER.debug(f'non_default_cell_format={overriding_cell_format}')

    #     # merge the 2 formats, with the cell formats overriding.
    #     merged_format = {**non_default_slide_format, **overriding_cell_format}

    #     # overlay this new format over the default list to create the new format.
    #     new_format = {'format': {**DEFAULT_FORMAT, **merged_format}}
    #     LOGGER.debug(f'newformat = {new_format}')
    #     # finaly, create a new format object to be used in the remainder of the function.

    #     format_ = Format(new_format,
    #                      _key='format',
    #                      _elem='body',
    #                      _exception=FormatError,
    #                      _keys_from=['justify', 'color', 'wordwrap', 'margin', 'type'],
    #                      _type_list=[str, int, bool, str, str]
    #                      )
    try:
        cell = content if isinstance(content, str) else content['cell']
    except KeyError:
        fe = FormatError('No cell element alongside format element in body')
        fe.show()
        quit(fe.exit_code)


    if format_.type == 'text':
        if format_.wordwrap:
            LOGGER.debug('WORDWRAP=true')
            wrapper = DocWrapper(width=width - 1)
            cell = wrapper.wrap(cell)
            LOGGER.debug(f'WRAPPEDcell={cell}')
        else:
            cell = cell.split('\n')


    for line in cell:
        assert isinstance(line, str)
        my_line = MyString(line)
        yield my_line.__dict__[format_.justify](my_line, width - 1)

