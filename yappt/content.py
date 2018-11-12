"""Class for managing the content part of a slide."""

from .exceptions import ContentError


class Content:
    def __init__(self, content_data):
        try:
            self.body = content_data['body']
        except (KeyError, TypeError):
            cerr = ContentError('No \'body\' element in slide content.')
            raise cerr

        if isinstance(content_data['body'], list):
            self.body = content_data['body']
        else:
            self.body = [content_data['body']]  # make it a list with 1 item
