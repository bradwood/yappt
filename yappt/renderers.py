"""Functions to render content widgets/elements."""
import textwrap
import re
import logging
LOGGER = logging.getLogger(__name__)

# define a  string sub-class to map our justification methods.
class MyString(str):
    def __init__(self, *args,**kwargs):
        self.left = str.ljust
        self.right = str.rjust
        self.centre = str.center


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

    if format_.type == 'text':
        if format_.wordwrap:
            LOGGER.debug('WORDWRAP=true')
            wrapper = DocWrapper(width=width - 1)
            # content = wrapper.fill(content.replace('\n',' '))
            content = wrapper.wrap(content)
            LOGGER.debug(f'WRAPPEDCONTENT={content}')
        else:
            content = content.split('\n')


    for line in content:
        assert isinstance(line, str)
        my_line = MyString(line)
        yield my_line.__dict__[format_.justify](my_line, width - 1)

