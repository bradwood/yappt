"""Class for the Slide Object."""
from typing import Dict, Any, Tuple
from .exceptions import SlideError, LayoutError, ContentError
from .metasettings import MetaData, Settings
from .layout import Layout
from .content import Content


class Slide:
    def __init__(self,
                 name: str,
                 data: Dict[str, Any],
                 deck_settings: Settings, # deck-level settings
                 metadata: MetaData, # deck-level metadata
                 ):

        self.name = name

        # check data payload
        if not isinstance(data, dict):
            se = SlideError(f'Slide \'{name}\' has no dictionary under it.')
            se.show()
            quit(se.exit_code)

        # Now check each sub-element of the slide...
        # A slide has:
        # - a name -- the top-lost yaml element
        # - settings (these are the same structure as the deck-level
        #   but apply only to this slide and override as needed.
        #   if empty, the deck-level setting carries through.
        # - a layout (see below)
        # - metadata -- which is passed as is from the deck-level as is
        # - content -- which holds the following under it:
        #    - format: formatting data for the entire body.
        #    - body: which holds the body content of the slide.

        ### LAYOUT
        # Layout processing is done as follows:
        # - a '-'-separated string of integers is passed.
        # - Each integer reprents a row
        # - the _value_ of each in is the number of cells in that row
        # - rows will be spaced evenly from top to bottom when rendering.

        # process layout
        try:
            # if no layout in slide, assume "1"
            self.layout = Layout(str(data.get('layout','1')))
        except (LayoutError) as le:
            se = SlideError(f'Error parsing slide {name}.')
            se.show()
            le.show()
            quit(le.exit_code)

        self.content = Content(data,
                               _key='content',
                               _exception=ContentError,
                               _elem=name,
                               _sub_keys=['body'],
                               )

        # check content array length is compatible with the layout specified

        if len(self.content.body) != self.layout.cell_count:
            ler = LayoutError(f'Slide \'{name}\' has incompatible/bad layout: {self.layout.layout_str}.\n' +
                             'There must be the same number of layout digits as body sections.')
            ler.show()
            quit(ler.exit_code)

        # strip any name value from the passed deck_settings and turn it into a dict.
        deck_settings_dict = {k: v for k, v in vars(deck_settings).items() if k != 'slide_name'}

        # merge slide-specific settings onto the deck_settings_dict with slide overriding
        try:
            new_settings = {**deck_settings_dict, **data['settings']}
        except (KeyError, TypeError):
            # no seettings passed in data so just use the deck settings.
            new_settings = deck_settings_dict

        self.settings = Settings(name, **new_settings)

        self.metadata = metadata

    def __repr__(self):
        return f'Slide(\'{self.name}\' layout={self.layout}, settings={self.settings})'

