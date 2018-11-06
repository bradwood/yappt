"""The class definition for Widgets: items to be rendered that make a all or part of a slide."""
from typing import Optional, List, Tuple
from .metasettings import Settings, MetaData
from .utils import create_active_cells

class Widget():
    def __init__(self, *,
                 slide_num: int,
                 total_slides: int,
                 type_: str,
                 content: Optional[str],
                 settings: Settings,
                 metadata: Optional[MetaData],
                 active_cells: Optional[Tuple],
                 wait_for_key_press: bool):

        self.slide_num = slide_num
        self.type_ = type_
        self.content = content
        self.active_cells = active_cells
        self.footer: list = [None, None, None]  # list for left, centre, right
        self.header: list = [None, None, None]  # list for left, centre, right
        self.wait_for_key_press = wait_for_key_press

        if type_ == 'background':
            assert isinstance(metadata, MetaData)
            if settings.pagenum:  # Print 'n / m' in bottom right
                self.footer[2] = f'{slide_num} / {total_slides}'

            if settings.authorfooter: # Print author name in bottom left
                self.footer[0] = metadata.author

            if settings.titlebar:  # Print title of deck in the centre of the header bar
                self.header[1] = metadata.title

    def __repr__(self):
        return f'Widget(slide_num={self.slide_num}, type_={self.type_}, active_cells={self.active_cells})'



def generate_widgets(slide, slide_num, total_slides)-> List[Widget]:
    """Generate a list of renderable widgets for the passed slide."""
    widgets = []
    # create the background widget for this slide first
    background = Widget(slide_num=slide_num,
                        total_slides=total_slides,
                        type_='background',
                        content=None,  # backgrounds have no content
                        settings=slide.settings,
                        metadata=slide.metadata,
                        active_cells=None,  # backgrounds have no active cell.
                        wait_for_key_press=False)  # backgrounds never wait for key press.

    widgets.append(background)
    # the slide will be rendered in bits, so create a widget for each bit.
    if slide.settings.incremental:
        for num, content in enumerate(slide.content):
            content_part = Widget(slide_num=slide_num,
                                  total_slides=total_slides,
                                  type_='foreground',
                                  content=content,
                                  settings=slide.settings,
                                  metadata=None,  # foregrounds don't need metadata
                                  active_cells=create_active_cells(slide.layout, tuple([num])),
                                  wait_for_key_press=True)  # Incremental so we wait.
            widgets.append(content_part)

    else:  # no incremental flag, so we merge all the content parts into one widget.
        content_part = Widget(slide_num=slide_num,
                              total_slides=total_slides,
                              type_='foreground',
                              content=slide.content,
                              settings=slide.settings,
                              metadata=None,  # foregrounds don't need metadata
                              # activate all the cells as this is not incremental.
                              active_cells=create_active_cells(slide.layout, tuple([i for i in range(len(slide.content))])),
                              wait_for_key_press=True)  # This is the only part so we wait.
        widgets.append(content_part)
    print(widgets)
    return widgets
