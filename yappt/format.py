"""Manages the format attributes of a particular slide."""

from .validator_mixins import ValIsDictSubKeysFromMixIn
from .exceptions import FormatError


class Format(ValIsDictSubKeysFromMixIn):
    def __init__(self, payload, *args, **kwargs):
        super().__init__(payload, *args, **kwargs)  # run mixin validations
        format_ = payload['format']

        valid_opts = {
            'justify': ['left', 'centre', 'right'],
            'color': ['white'],
            'wordwrap': [True, False],
            'type': ['text', 'code', 'figlet'],
        }
        # defaults
        self.justify: str = 'left'
        self.color: str = 'white'
        self.wordwrap: bool = True
        self.margin: list = '1-1-1-1'
        self.type: str = 'text'

        # check format values are valid.
        for key, val in format_.items():
            if key != 'margin': # we'll handle this separately.
                if val not in valid_opts[key]:
                    msg = f"{kwargs['_elem']}.\n" + \
                        f'Bad value \'{val}\' for \'{key}\'. ' + \
                        f'Expected one of {valid_opts[key]}.'
                    e = FormatError(msg)
                    e.show()
                    quit(e.exit_code)
            else:
                setattr(self, key, format_[key])

        try:
            margin_pack = format_.get('margin')
            if not margin_pack:
                margin_pack = '1-1-1-1'
            left_m, right_m, top_m, bottom_ = margin_pack.split('-')
        except (ValueError, AttributeError):
            fe = FormatError(f'{kwargs["_elem"]}. Could not parse margin parameter, expected \'x-y-z-w\'-style string.')
            fe.show()
            quit(fe.exit_code)

    def __repr__(self):
        kv = [f'{k}=\'{v}\'' for k, v in vars(self).items()]
        return f'Format({", ".join(kv)})'
