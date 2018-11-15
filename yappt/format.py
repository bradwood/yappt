"""Manages the format attributes of a particular slide."""

from .validator_mixins import ValIsDictCheckSubKeyTypesMixIn
from .exceptions import FormatError


class Format(ValIsDictCheckSubKeyTypesMixIn):
    def __init__(self, payload, *args, **kwargs):
        super().__init__(payload, *args, **kwargs)  # run mixin validations
        format_ = payload['format']

        # set an entry here for any option which is list-constrained.
        valid_opts = {
            'justify': ['left', 'centre', 'right'],
            'type': ['text', 'code', 'figlet'],
        }
        # defaults
        self.justify: str = 'left'
        self.color: str = 0
        self.wordwrap: bool = True
        self.margin: str = '1-1-1-1'
        self.type: str = 'text'

        # check format values are valid for list-constrained options.
        for key, val in format_.items():
            if key in valid_opts and val not in valid_opts[key]:
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
            self.l_margin, self.r_margin, self.t_margin, self.b_margin = margin_pack.split('-')

        except (ValueError, AttributeError):
            fe = FormatError(f'{kwargs["_elem"]}. Could not parse margin parameter, expected \'x-y-z-w\'-style string.')
            fe.show()
            quit(fe.exit_code)

    def __repr__(self):
        kv = [f'{k}=\'{v}\'' for k, v in vars(self).items()]
        return f'Format({", ".join(kv)})'
