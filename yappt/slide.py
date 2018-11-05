"""Class for the Slide Object."""
from typing import Dict, Any
from .exceptions import SlideError
from .metasettings import MetaData, Settings

class Slide:
    def __init__(self,
                 name: str,
                 data: Dict[str, Any],
                 deck_settings: Settings
                 ):

        self.name = name

        # check data payload
        if not isinstance(data, dict):
            se = SlideError(f'Slide \'{name}\' has no dictionary under it.')
            se.show()
            quit(se.exit_code)

        # check layout
        try:
            layout = str(data.get('layout','1')) # if no layout in slide, assume "1"
            # print(layout)
            self.layout = tuple(map(int, layout.split('-')))
            # print(self.layout)
        except (ValueError, AttributeError):
            se = SlideError(f'Slide \'{name}\' has bad layout \'{layout}\'.')
            se.show()
            quit(se.exit_code)

        # check content
        try:
            if isinstance(data['content'], list):
                # print('content is a list')
                self.content = data['content']  # make it a list
            else:
                # print('content is not a list')
                self.content = [data['content']]  # make it a list
        except KeyError:
            se = SlideError(f'Slide \'{name}\' has no \'content\' element under it.')
            se.show()
            quit(se.exit_code)

        # check content array length is compatible with the layout specified
        if len(self.content) != sum(self.layout) or sum(self.layout) > 6:
            # print(self.content)
            se = SlideError(f'Slide \'{name}\' has incompatible/bad layout: {layout}.')
            se.show()
            quit(se.exit_code)

        # strip any name valuse from the passed deck_settings and turn it into a dict.
        deck_settings_dict = {k: v for k, v in vars(deck_settings).items() if k != 'slide_name'}

        # merge slide-specific settings onto the deck_settings_dict with slide overriding
        try:
            new_settings = {**deck_settings_dict, **data['settings']}
        except KeyError:
            # no seettings passed in data so just use the deck settings.
            new_settings = deck_settings_dict

        self.settings = Settings(name, **new_settings)

    def __repr__(self):
        return f'Slide(\'{self.name}\' layout={self.layout}, settings={self.settings})'
