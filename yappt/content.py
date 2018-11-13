"""Class for managing the content part of a slide."""
from .format import Format
from .validator_mixins import ValIsDictHasSubKeysMixIn, ValIsDictSubKeysFromMixIn
from .exceptions import ContentError, FormatError


class Content(ValIsDictHasSubKeysMixIn, ValIsDictSubKeysFromMixIn):
    def __init__(self, payload, *args, **kwargs):
        super().__init__(payload, *args, **kwargs) # run mixin validations
        content = payload['content']

        self.body = content['body']

        if isinstance(content['body'], list):
            self.body = content['body']
        else:
            self.body = [content['body']]  # make it a list with 1 item

        self.format = Format(content,
                             _key='format',
                             _exception=FormatError,
                             _elem=f"slide {kwargs['_elem']}, format section",
                             _keys_from=['justify', 'color', 'wordwrap', 'margin', 'type']
                             )
