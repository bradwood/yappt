"""YAPPT Exceptions."""
import click

class YAPPTBaseException(Exception):

    exit_code = 1

    def __init__(self, message):
        ctor_msg = message
        Exception.__init__(self, ctor_msg)
        self.message = message

    def format_message(self):
        return self.message

    def __str__(self):
        return self.message

    def show(self):
        click.echo(f'Error: {self.format_message()}', err=True)

class YAMLParseError(YAPPTBaseException):

    exit_code = 2

    def show(self):
        click.echo(f'YAML error: {self.format_message()}', err=True)

class SettingsError(YAPPTBaseException):

    exit_code = 3

    def __init__(self, message, slide=None):
        super().__init__(message)
        self.slide = slide

    def show(self):
        if self.slide:
            click.echo(f'Settings error in slide: \'{self.slide}\': {self.format_message()}', err=True)
        else:
            click.echo(f'Settings error: {self.format_message()}', err=True)


class MetaDataError(YAPPTBaseException):

    exit_code = 4

    def show(self):
        click.echo(f'Metadata error: {self.format_message()}', err=True)


class SlideError(YAPPTBaseException):

    exit_code = 5

    def show(self):
        click.echo(f'Slide error: {self.format_message()}', err=True)
