"""Classes for Presentation and Slide Settings and Metadata."""
from .exceptions import SettingsError, MetaDataError
from datetime import date
import getpass

class Settings:

    def __init__(self, *_, **kwargs):

        # defaults
        self.pagenum: bool = True
        self.titlebar: bool = True
        self.authorfooter: bool = True
        self.wordwrap: bool = True
        self.incremental: bool = False
        self.frontpage: bool = False

        for key, val in kwargs.items():
            if key not in vars(self):
                e = SettingsError(f'Bad key \'{key}\'.')
                e.show()
                quit(e.exit_code)
            elif not isinstance(val, bool):
                e = SettingsError(f'Bad value \'{val}\' for \'{key}\'.')
                e.show()
                quit(e.exit_code)

            else:
                setattr(self, key, kwargs[key])

    def __repr__(self):
        kv = [f'{k}={v}' for k,v in vars(self).items()]
        return f'Settings({", ".join(kv)})'

class MetaData:

    def __init__(self, *_, **kwargs):

        # defaults
        self.title: str = 'YAPPT'
        self.author: str = getpass.getuser()
        self.date: date = date.today()

        for key, val in kwargs.items():
            if key not in vars(self):
                e = MetaDataError(f'Bad key \'{key}\'.')
                e.show()
                quit(e.exit_code)
            elif val.__class__ != getattr(self, key).__class__:
                # Type error
                msg = f'Bad value \'{val}\' for \'{key}\'. ' + \
                    f'Expected {getattr(self, key).__class__.__name__}'
                e = MetaDataError(msg)
                e.show()
                quit(e.exit_code)
            else:
                setattr(self, key, kwargs[key])

    def __repr__(self):
        kv = [f'{k}=\'{v}\'' for k, v in vars(self).items()]
        return f'MetaData({", ".join(kv)})'
