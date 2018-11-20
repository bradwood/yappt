"""Classes for Presentation and Deck/Slide Settings and Metadata."""
import getpass
from datetime import date
from .validator_mixins import ValIsDictCheckSubKeyTypesMixIn


class Settings(ValIsDictCheckSubKeyTypesMixIn):

    def __init__(self, payload, *args, **kwargs):
        super().__init__(payload, *args, **kwargs)  # run mixin validations
        settings = payload['settings']

        # defaults
        self.pagenum: bool = True
        self.titlebar: bool = True
        self.slidetitle: bool = True
        self.authorfooter: bool = True
        self.date: bool = True
        self.incremental: bool = False
        self.v_margin: int = 1
        self.h_margin: int = 1

        for key in settings:
            setattr(self, key, settings[key])

    def __repr__(self):
        kv = [f'{k}={v}' for k,v in vars(self).items() if k != 'slide_name']
        return f'Settings({", ".join(kv)})'


class MetaData(ValIsDictCheckSubKeyTypesMixIn):

    def __init__(self, payload, *args, **kwargs):
        super().__init__(payload, *args, **kwargs)  # run mixin validations
        metadata = payload['metadata']

        # defaults
        self.title: str = 'YAPPT'
        self.author: str = getpass.getuser()
        self.date: date = date.today()

        for key in metadata:
            setattr(self, key, metadata[key])

    def __repr__(self):
        kv = [f'{k}=\'{v}\'' for k, v in vars(self).items()]
        return f'MetaData({", ".join(kv)})'
