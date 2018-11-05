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
        click.echo('Error: %s' % self.format_message(), err=True)

class YAMLParseError(YAPPTBaseException):

    exit_code = 2

    def show(self):
        click.echo('YAML error: %s' % self.format_message(), err=True)

class SettingsError(YAPPTBaseException):

    exit_code = 3

    def show(self):
        click.echo('Settings error: %s' % self.format_message(), err=True)


class MetaDataError(YAPPTBaseException):

    exit_code = 4

    def show(self):
        click.echo('Metadata error: %s' % self.format_message(), err=True)
