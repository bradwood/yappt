"""A curses-based terminal renderer for the Mistletoe Markdown Libary."""
import curses
import logging
import html
from urllib.parse import quote
from contextlib import suppress

from mistletoe.base_renderer import BaseRenderer

logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, filename='yappt.log',
                    format=logformat)  # datefmt="%Y-%m-%d %H:%M:%S"

LOGGER = logging.getLogger(__name__)

class CursesRenderer(BaseRenderer):
    """Extends BaseRenderer to enable rendering to a curses-enabled terminal.

    Tries to mess with curses as little as possible, apart from simply writing to the screen.

    """

    def __init__(self, *extras, curses_win=curses.initscr()):
        super().__init__(*extras)
        self.win = curses_win
        self.height, self.width = self.win.getmaxyx()
        self.cur_y, self.cur_x = self.win.getyx()
        self.curses_attr = curses.A_NORMAL
        self.curses_attr_map = {
            'Strong':         curses.A_BOLD,
            'Emphasis':       curses.A_UNDERLINE,
            'InlineCode':     curses.color_pair(255),
            'Strikethrough':  curses.A_REVERSE,
            'Link':           curses.A_UNDERLINE,
            'AutoLink':       curses.A_UNDERLINE,
            'Quote':          curses.A_NORMAL,
            'Heading':        curses.color_pair(208), # TODO add color range.
            'SetextHeading':  curses.color_pair(208),
            'BlockCode':      curses.color_pair(255),
            'CodeFence':      curses.color_pair(255),
            'Quote':          curses.A_NORMAL,  # TODO add color range.
            'ThematicBreak':  curses.A_NORMAL,
        }
        self.quote_depth = 0 # count the depth of nested quotes to print bar prefix
        self.new_line = False # flag to know if we just went to a new line.
        self.list_depth = 0  # count the depth of nested lists to print prefix
        #for ordered list, maintain a stack of the current level's item counter.
        self.ordered_list_current_counter = []
        self.list_stack = []
        self.suppress_double_newline_paragraph = [False]

    @staticmethod
    def escape_html(raw):
        return html.escape(html.unescape(raw)).replace('&#x27;', "'")

    @staticmethod
    def escape_url(raw):
        """
        Escape urls to prevent code injection craziness. (Hopefully.)
        """
        return html.escape(quote(html.unescape(raw), safe='/#:()*?=%@+,&'))

    def render(self, token):

        # handle basic text-emphasis token types
        LOGGER.debug(f'rendering {token.__class__.__name__}')
        with suppress(AttributeError):
            LOGGER.debug(f'token content: {token.content}')

        if token.__class__.__name__ in self.curses_attr_map:
            # turn on the appropriate curses attr
            self.curses_attr = self.curses_attr | self.curses_attr_map[token.__class__.__name__]
            #render it
            rendered = self.render_map[token.__class__.__name__](token)
            # turn off the appropriate curses attr
            self.curses_attr = self.curses_attr & ~self.curses_attr_map[token.__class__.__name__]

        # catchall
        else:
            rendered = self.render_map[token.__class__.__name__](token)
        return rendered

    def render_inner(self, token):
        """Recursively render children."""
        rendered = [self.render(child) for child in token.children]
        #LOGGER.debug(f'rendered = {rendered}')
        if rendered[0]:
            return ''.join(rendered)
        else:
            return ''

    def _newline(self, lines=1, cr=True, indent=0):
        """Move the cursor down one line if possible."""
        self.cur_y += lines
        if cr:  # carriage return
            self.cur_x = 0 + indent
        self.new_line = True

    def render_raw_text(self, token):
        with suppress(curses.error):
            if self.new_line and self.quote_depth > 0:
                #this text is at the beginning of a quoted line, so write the prefix.
                self.win.addstr(self.cur_y, self.cur_x, ' ▎'*self.quote_depth, self.curses_attr)
                self.cur_y, self.cur_x = self.win.getyx()

            if self.new_line and self.list_depth > 0 and self.list_stack:
                # we are in a list so prefix it with bullets/numbers.
                if self.list_stack[-1] == 'ul':  # unordered list
                    bullets = ['●', '○', '■', '□', '-', '-', '-', '-', '-']
                    bullet = bullets[self.list_depth-1]
                    indent = '  '* self.list_depth
                    prefix = ''.join([indent, bullet, ' '])
                    self.win.addstr(self.cur_y, self.cur_x, prefix, curses.A_NORMAL)
                    self.cur_y, self.cur_x = self.win.getyx()
                # TODO: fix bug with list starting with non-zero at some point.
                elif self.list_stack[-1] == 'ol':
                    num = self.ordered_list_current_counter[self.list_depth-1]
                    indent = ''.join(['  ' * self.list_depth])
                    prefix = ''.join([indent, str(num), '. '])
                    self.win.addstr(self.cur_y, self.cur_x, prefix, curses.A_NORMAL)
                    self.cur_y, self.cur_x = self.win.getyx()
                    self.ordered_list_current_counter[self.list_depth-1] += 1

            self.win.addstr(self.cur_y, self.cur_x, token.content, self.curses_attr)
            self.new_line = False
            self.cur_y, self.cur_x = self.win.getyx()
            return '' # token.content

    def render_line_break(self, token):
        # TODO:do we need to care about token.soft here?
        if self.suppress_double_newline_paragraph[-1]:
            pass #self._newline(1)
        else:
            self._newline(1)

        # if not token.soft:
        #     self._newline()
        return ''

    def render_paragraph(self, token):
        # if self.suppress_double_newline_paragraph[-1]:
        #     pass # self._newline(1)
        # else:
        #     self._newline(1)
        _ = [self.render(child) for child in token.children]

        if self.suppress_double_newline_paragraph[-1]:
            self._newline(1)
        else:
            self._newline(2)


        return ''

    def render_heading(self, token): # # TODO: add color scheme support
        if self.suppress_double_newline_paragraph[-1]:
            self._newline(0)
        else:
            self._newline(1)

        self._newline(-1, indent=token.level-1)

        _ = [self.render(child) for child in token.children]

        if self.suppress_double_newline_paragraph[-1]:
            self._newline(1)
        else:
            self._newline(2)

        return '' #self.render_inner(token)

    def render_link(self, token):
        token.children[0].content = f'{token.children[0].content}:({token.target})'
        return self.render_inner(token)

    def render_block_code(self, token):  # TODO: add pygments - use token.language
        LOGGER.debug(token.children[0].content)
        code = token.children[0].content.split('\n')
        del code[-1] # remove the last newline
        # if self.suppress_double_newline_paragraph[-1]:
        #     self._newline(0)
        # else:
        #     self._newline(1)
        for linenum, line in enumerate(code):
            line_prefix = f' {str(linenum).zfill(2)} │ '
            LOGGER.debug(f'y={self.cur_y}')
            LOGGER.debug(f'x={self.cur_x}')
            LOGGER.debug(f'prefix={line_prefix}')
            LOGGER.debug(f'attr={self.curses_attr}')
            # write out the line number prefix
            with suppress(curses.error):
                self.win.addstr(self.cur_y, self.cur_x, line_prefix, curses.A_NORMAL)
                # # write out the code itself
                self.cur_y, self.cur_x = self.win.getyx()
                self.win.addstr(self.cur_y, self.cur_x, line, self.curses_attr)
                # self.cur_y, self.cur_x = self.win.getyx()
                self._newline(1)
                #self.cur_y, self.cur_x = self.win.getyx()

        self._newline(1)
        self.new_line = True
        #self.cur_y, self.cur_x = self.win.getyx()

        return ''

    def render_quote(self, token):
#        self._newline()
        # if self.suppress_double_newline_paragraph[-1]:
        #     pass # self._newline(1)
        # else:
        #     self._newline(1)

        self.suppress_double_newline_paragraph.append(True)
        self.quote_depth += 1

        _ = [self.render(child) for child in token.children]

        self.quote_depth -= 1
        self.suppress_double_newline_paragraph.pop()

        if self.suppress_double_newline_paragraph[-1]:
            pass  # self._newline(1)
        else:
            self._newline(1)

        return ''

    def render_list(self, token):
        # set up the stack properly
        self.list_depth += 1
        self.suppress_double_newline_paragraph.append(True)
        if token.start is not None:
            self.list_stack.append('ol')
            self.ordered_list_current_counter.append(token.start)
        else:
            self.list_stack.append('ul')
        # render
        _ = [self.render(child) for child in token.children]
        # pop the stack
        if token.start is not None:
            self.ordered_list_current_counter.pop()
        self.list_stack.pop()
        self.suppress_double_newline_paragraph.pop()
        self.list_depth -= 1

        if self.list_depth == 0:
            self._newline()
        return ''

    def render_list_item(self, token):
        _ = [self.render(child) for child in token.children]
        return ''

    def render_thematic_break(token):
        return '<hr />'



    # def render_image(self, token):
    #     template = '<img src="{}" alt="{}"{} />'
    #     render_func = self.render
    #     self.render = self.render_to_plain
    #     inner = self.render_inner(token)
    #     self.render = render_func
    #     if token.title:
    #         title = ' title="{}"'.format(self.escape_html(token.title))
    #     else:
    #         title = ''
    #     return template.format(token.src, inner, title)

    # @staticmethod
    # def render_html_span(token):
    #     return token.content



    # def render_table(self, token):
    #     # This is actually gross and I wonder if there's a better way to do it.
    #     #
    #     # The primary difficulty seems to be passing down alignment options to
    #     # reach individual cells.
    #     template = '<table>\n{inner}</table>'
    #     if hasattr(token, 'header'):
    #         head_template = '<thead>\n{inner}</thead>\n'
    #         head_inner = self.render_table_row(token.header, is_header=True)
    #         head_rendered = head_template.format(inner=head_inner)
    #     else:
    #         head_rendered = ''
    #     body_template = '<tbody>\n{inner}</tbody>\n'
    #     body_inner = self.render_inner(token)
    #     body_rendered = body_template.format(inner=body_inner)
    #     return template.format(inner=head_rendered+body_rendered)

    # def render_table_row(self, token, is_header=False):
    #     template = '<tr>\n{inner}</tr>\n'
    #     inner = ''.join([self.render_table_cell(child, is_header)
    #                      for child in token.children])
    #     return template.format(inner=inner)

    # def render_table_cell(self, token, in_header=False):
    #     template = '<{tag}{attr}>{inner}</{tag}>\n'
    #     tag = 'th' if in_header else 'td'
    #     if token.align is None:
    #         align = 'left'
    #     elif token.align == 0:
    #         align = 'center'
    #     elif token.align == 1:
    #         align = 'right'
    #     attr = ' align="{}"'.format(align)
    #     inner = self.render_inner(token)
    #     return template.format(tag=tag, attr=attr, inner=inner)


    # @staticmethod
    # def render_html_block(token):
    #     return token.content

    # def render_document(self, token):
    #     self.footnotes.update(token.footnotes)
    #     inner = '\n'.join([self.render(child) for child in token.children])
    #     return '{}\n'.format(inner) if inner else ''

    # @staticmethod
    # def escape_html(raw):
    #     return html.escape(html.unescape(raw)).replace('&#x27;', "'")

    # @staticmethod
    # def escape_url(raw):
    #     """
    #     Escape urls to prevent code injection craziness. (Hopefully.)
    #     """
    #     return html.escape(quote(html.unescape(raw), safe='/#:()*?=%@+,&'))
