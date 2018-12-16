"""The class definition for Widgets: items to be rendered that make a slide."""
import curses
from typing import List, Optional, Tuple

from .content import Body
from .format import Format
from .metasettings import MetaData, Settings

# from datetime import date


class Widget():
    def __init__(self, *,
                 slide_num: int,
                 slide_name: str,
                 total_slides: int,
                 type_: str,
                 body: Optional[List[str]],
                 settings: Settings,
                 metadata: Optional[MetaData],
                 active_cells: Optional[Tuple],
                 format_: Optional[Format],
                 # wait_for_key_press: bool
                 ):
        self.slide_num = slide_num
        self.slide_name = slide_name
        self.pres_date = None
        self.type_ = type_
        self.body = None
        self.settings = settings
        self.active_cells = active_cells
        # self.format_ = format_
        self.header = None
        self.footer = None
        # a stack of child widgets for this window
        self.foreground_widgets: list = []

        footer: list = [None, None, None]  # list for left, centre, right
        header: list = [None, None, None]  # list for left, centre, right

        if type_ == 'background':
            assert isinstance(metadata, MetaData)
            assert body is None
            # assert format_ is None

            if settings.pagenum:  # Print 'n / m' in bottom right
                footer[2] = f'{slide_num+1} / {total_slides}'

            if settings.authorfooter:  # Print author name in bottom left
                footer[0] = metadata.author
            # Print title of deck in the centre of the header bar

            if settings.titlebar:
                header[1] = metadata.title

            if settings.slidetitle:  # Print slide name top left of the slide.
                header[0] = self.slide_name

            if settings.date:
                self.pres_date = metadata.date.strftime('%d %B %Y')
                header[2] = self.pres_date

            self.header = tuple(header)
            self.footer = tuple(footer)
        elif type_ == 'foreground':
            self.body = Body(body, format_)

            # assert isinstance(self.body, Body)
            # assert self.format_ is not None

    def __repr__(self):
        return f'Widget(slide_num={self.slide_num}, type_={self.type_},' + \
            f' active_cells={self.active_cells})'


def generate_widgets_from_slide(slide, slide_num, total_slides)-> List[Widget]:
    """Generate a list of renderable widgets for the passed slide."""
    widgets = []
    # create the background widget for this slide first
    background = Widget(slide_num=slide_num,
                        slide_name=slide.name,
                        total_slides=total_slides,
                        type_='background',
                        body=None,  # backgrounds have no body
                        settings=slide.settings,
                        metadata=slide.metadata,
                        active_cells=None,  # backgrounds have no active cell.
                        format_=None,  # backgrounds have no format.
                        )  # backgrounds never wait for key press.

    widgets.append(background)
    # the slide will be rendered in bits, so create a widget for each bit.

    if slide.settings.incremental:
        for num, body in enumerate(slide.content.body):
            body_part = Widget(slide_num=slide_num,
                               slide_name=slide.name,
                               total_slides=total_slides,
                               type_='foreground',
                               body=body,  # must be a list, even if one 1 item
                               settings=slide.settings,
                               # foregrounds don't need metadata
                               metadata=None,
                               active_cells=slide.layout.active_cells(
                                   tuple([num])),
                               format_=slide.content.format_,
                               )  # Incremental so we wait.
            widgets.append(body_part)

    else:  # no incremental flag, so merge all the body parts into one widget.
        body_part = Widget(slide_num=slide_num,
                           slide_name=slide.name,
                           total_slides=total_slides,
                           type_='foreground',
                           body=slide.content.body,
                           settings=slide.settings,
                           metadata=None,  # foregrounds don't need metadata
                           # activate all the cells as this is not incremental.
                           active_cells=slide.layout.active_cells(
                               tuple([i for i in
                                      range(len(slide.content.body))]
                                     )
                           ),
                           format_=slide.content.format_,
                           )  # This is the only part so we wait.
        widgets.append(body_part)

    return widgets
