"""Functions to render content widgets/elements."""
import logging
import re
import textwrap

from pyfiglet import Figlet, FontNotFound
from reparser import MatchGroup, Parser, Token

from .exceptions import FormatError

LOGGER = logging.getLogger(__name__)

# Parser code stolen from https://github.com/xmikos/reparser with credit.
# LICENCE: https://github.com/xmikos/reparser/blob/master/LICENSE

boundary_chars = r'\s`!()\[\]{{}};:\'".,<>?«»“”‘’*_~='
b_left = r'(?:(?<=[' + boundary_chars + r'])|(?<=^))'  # Lookbehind
b_right = r'(?:(?=[' + boundary_chars + r'])|(?=$))'   # Lookahead

markdown_start = b_left + r'(?<!\\){tag}(?!\s)(?!{tag})'
markdown_end = r'(?<!{tag})(?<!\s)(?<!\\){tag}' + b_right
markdown_link = r'(?<!\\)\[(?P<link>.+?)\]\((?P<url>.+?)\)'
newline = r'\n|\r\n'

url_proto_regex = re.compile(r'(?i)^[a-z][\w-]+:/{1,3}')


def markdown(tag):
    """Return sequence of start and end regex patterns for simple Markdown tag."""
    return (markdown_start.format(tag=tag), markdown_end.format(tag=tag))


def url_complete(url):
    """Prepend a URL with http:// if needed."""
    return url if url_proto_regex.search(url) else 'http://' + url


tokens = [
    Token('bi1',  *markdown(r'\*\*\*'), is_bold=True, is_italic=True),
    Token('bi2',  *markdown(r'___'),    is_bold=True, is_italic=True),
    Token('b1',   *markdown(r'\*\*'),   is_bold=True),
    Token('b2',   *markdown(r'__'),     is_bold=True),
    Token('i1',   *markdown(r'\*'),     is_italic=True),
    Token('i2',   *markdown(r'_'),      is_italic=True),
    Token('pre3', *markdown(r'```'),    skip=True),
    Token('pre2', *markdown(r'``'),     skip=True),
    Token('pre1', *markdown(r'`'),      skip=True),
    Token('s',    *markdown(r'~~'),     is_strikethrough=True),
    Token('u',    *markdown(r'=='),     is_underline=True),
    Token('link', markdown_link, text=MatchGroup('link'),
          link_target=MatchGroup('url', func=url_complete)),
    Token('br', newline, text='\n', segment_type="LINE_BREAK")
]

parser = Parser(tokens)

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


    if format_.type == 'code':
        cell = cell.split('\n')
        cell = [f' {str(num).zfill(2)}│ {data}' for num, data in enumerate(cell)]
        del cell[-1]

    if format_.type == 'figlet':
        try:
            f = Figlet(width=width, justify=format_.justify, font=format_.figfont)
        except FontNotFound:
            LOGGER.warning(f'{format_.figfont} figlet not found, using standard font.')
            f = Figlet(width=width, justify=format_.justify, font='standard')
        cell = f.renderText(cell)
        cell = cell.split('\n')


    for line in cell:
        assert isinstance(line, str)
        if format_.type == 'figlet':
            # no parsing or line justifying for figlets so just yield None for this case.
            yield line, None
        else:
            my_line = MyString(line)
            # yield the unparsed line, then the parsed line
            yield my_line.__dict__[format_.justify](my_line, width - 1), \
                parser.parse(my_line.__dict__[format_.justify](my_line, width - 1))


def render_line(y, x, line_segments, color_pair):
    """Write out the markdown line applying color/formatting as needed."""
    pass
