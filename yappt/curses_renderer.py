"""A curses-based terminal renderer for the Mistletoe Markdown Libary."""
import curses
import logging
import html
from urllib.parse import quote

# from functools import wraps
# from collections import namedtuple

from mistletoe.base_renderer import BaseRenderer

# from mistletoe import Document

# from mistletoe.ast_renderer import ASTRenderer

# with open('sample.md', 'r') as fin:
#     with ASTRenderer() as renderer:
#         rendered = renderer.render(Document(fin))

# print(rendered)


logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, filename='yappt.log',
                    format=logformat)  # datefmt="%Y-%m-%d %H:%M:%S"

LOGGER = logging.getLogger(__name__)

# HeaderFormat = namedtuple('HeaderFormat', ['indent', 'attr'])


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
            'Heading':        curses.color_pair(208),
            'SetextHeading':  curses.color_pair(208),
            'BlockCode':      curses.color_pair(255), # TODO figure out the difference here.
            'CodeFence':      curses.color_pair(255),
        }

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
        return ''.join(rendered)

    def _newline(self, lines=1, cr=True, indent=0):
        """Move the cursor down one line if possible."""
        if self.cur_y + lines < self.height:
            self.cur_y += lines
        else:
            self.cur_y = self.height - 1
        if cr:  # carriage return
            self.cur_x = 0 + indent

    def render_raw_text(self, token):
        self.win.addstr(self.cur_y, self.cur_x, token.content, self.curses_attr)
        self.cur_y, self.cur_x = self.win.getyx()
        return '' # token.content

    def render_line_break(self, token):
        if token.soft or not token.soft: # TODO: fix /clean this.
            self._newline()
        return ''

    def render_paragraph(self, token):
        self._newline(2)
        return self.render_inner(token)

    def render_heading(self, token):
        self._newline(2, indent=token.level-1)
        return self.render_inner(token)

    def render_link(self, token):
        token.children[0].content = f'{token.children[0].content}:({token.target})'
        return self.render_inner(token)

    def render_block_code(self, token):
        #template = '<pre><code{attr}>{inner}</code></pre>'
        LOGGER.debug(token.children[0].content)
        # if token.language:
        #     attr = ' class="{}"'.format('language-{}'.format(self.escape_html(token.language)))
        # else:
        #     attr = ''
        # inner = html.escape(token.children[0].content)

        # token.children[0].content
        code = token.children[0].content.split('\n')
        self._newline(2)
        for linenum, line in enumerate(code):
            line_prefix = f' {str(linenum).zfill(2)}│ '
            LOGGER.debug(f'y={self.cur_y}')
            LOGGER.debug(f'x={self.cur_x}')
            LOGGER.debug(f'prefix={line_prefix}')
            LOGGER.debug(f'attr={self.curses_attr}')
            # write out the line number prefix
            self.win.addstr(self.cur_y, self.cur_x, line_prefix, curses.A_NORMAL)
            # write out the code itself
            self.cur_y, self.cur_x = self.win.getyx()
            self.win.addstr(self.cur_y, self.cur_x, line, self.curses_attr)
            self._newline()

        # cell = cell.split('\n')
        # cell = [f'{str(num).zfill(2)}│ {data}' for num, data in enumerate(cell)]

        #self._newline()
        self.cur_y, self.cur_x = self.win.getyx()

        return '' # template.format(attr=attr, inner=inner)


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

    # def render_escape_sequence(self, token):
    #     return self.render_inner(token)

    # @staticmethod
    # def render_html_span(token):
    #     return token.content

    # def render_quote(self, token):
    #     elements = ['<blockquote>']
    #     self._suppress_ptag_stack.append(False)
    #     elements.extend([self.render(child) for child in token.children])
    #     self._suppress_ptag_stack.pop()
    #     elements.append('</blockquote>')
    #     return '\n'.join(elements)



    # def render_list(self, token):
    #     template = '<{tag}{attr}>\n{inner}\n</{tag}>'
    #     if token.start is not None:
    #         tag = 'ol'
    #         attr = ' start="{}"'.format(token.start) if token.start != 1 else ''
    #     else:
    #         tag = 'ul'
    #         attr = ''
    #     self._suppress_ptag_stack.append(not token.loose)
    #     inner = '\n'.join([self.render(child) for child in token.children])
    #     self._suppress_ptag_stack.pop()
    #     return template.format(tag=tag, attr=attr, inner=inner)

    # def render_list_item(self, token):
    #     if len(token.children) == 0:
    #         return '<li></li>'
    #     inner = '\n'.join([self.render(child) for child in token.children])
    #     inner_template = '\n{}\n'
    #     if self._suppress_ptag_stack[-1]:
    #         if token.children[0].__class__.__name__ == 'Paragraph':
    #             inner_template = inner_template[1:]
    #         if token.children[-1].__class__.__name__ == 'Paragraph':
    #             inner_template = inner_template[:-1]
    #     return '<li>{}</li>'.format(inner_template.format(inner))

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
    # def render_thematic_break(token):
    #     return '<hr />'

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
