"""Classes for Presentation and Deck/Slide Settings and Metadata."""
from .exceptions import SettingsError, MetaDataError
from datetime import date
import getpass

class Settings:

    def __init__(self, *args, **kwargs):

        # defaults
        if args:
            self.slide_name = args[0]
        else:
            self.slide_name = None

        self.pagenum: bool = True
        self.titlebar: bool = True
        self.authorfooter: bool = True
        self.incremental: bool = False
        self.frontpage: bool = False

        for key, val in kwargs.items():
            if key not in vars(self):
                e = SettingsError(f'Bad key \'{key}\'.', slide=self.slide_name)
                e.show()
                quit(e.exit_code)
            elif not isinstance(val, bool):
                e = SettingsError(f'Bad value \'{val}\' for \'{key}\'.', slide=self.slide_name)
                e.show()
                quit(e.exit_code)

            else:
                setattr(self, key, kwargs[key])

    def __repr__(self):
        kv = [f'{k}={v}' for k,v in vars(self).items() if k != 'slide_name']
        if self.slide_name:
            return f'Settings(\'{self.slide_name}\', {", ".join(kv)})'
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
