"""Class for managing the content part of a slide."""

from .validator_mixins import ValIsDictWithSubKeysMixIn
from .exceptions import ContentError


class Content(ValIsDictWithSubKeysMixIn):
    def __init__(self, payload, *args, **kwargs):
        super().__init__(payload, *args, **kwargs) # run mixin validations
        content = payload['content']

        self.body = content['body']

        if isinstance(content['body'], list):
            self.body = content['body']
        else:
            self.body = [content['body']]  # make it a list with 1 item
