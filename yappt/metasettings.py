"""Classes for Presentation and Deck/Slide Settings and Metadata."""
import getpass
from datetime import date

from .exceptions import MetaDataError, SettingsError
from .validator_mixins import ValIsDictSubKeysFromMixIn


class Settings(ValIsDictSubKeysFromMixIn):

    def __init__(self, payload, *args, **kwargs):
        super().__init__(payload, *args, **kwargs)  # run mixin validations
        settings = payload['settings']

        # defaults
        self.pagenum: bool = True
        self.titlebar: bool = True
        self.authorfooter: bool = True
        self.incremental: bool = False

        for key, val in settings.items():
            if not isinstance(val, bool):
                e = SettingsError(f'Bad value \'{val}\' for \'{key}\'.')
                e.show()
                quit(e.exit_code)
            else:
                setattr(self, key, settings[key])

    def __repr__(self):
        kv = [f'{k}={v}' for k,v in vars(self).items() if k != 'slide_name']
        return f'Settings({", ".join(kv)})'


class MetaData(ValIsDictSubKeysFromMixIn):

    def __init__(self, payload, *args, **kwargs):
        super().__init__(payload, *args, **kwargs)  # run mixin validations
        metadata = payload['metadata']

        # defaults
        self.title: str = 'YAPPT'
        self.author: str = getpass.getuser()
        self.date: date = date.today()

        for key, val in metadata.items():
            if val.__class__ != getattr(self, key).__class__:
                # Type error
                msg = f'Bad value \'{val}\' for \'{key}\'. ' + \
                    f'Expected {getattr(self, key).__class__.__name__}'
                e = MetaDataError(msg)
                e.show()
                quit(e.exit_code)
            else:
                setattr(self, key, metadata[key])

    def __repr__(self):
        kv = [f'{k}=\'{v}\'' for k, v in vars(self).items()]
        return f'MetaData({", ".join(kv)})'
