"""Manages the format attributes of a particular slide."""

from .validator_mixins import ValIsDictCheckSubKeyTypesMixIn
from .exceptions import FormatError

DEFAULT_FORMAT = {
    'justify': 'left',
    'color': 0,
    'wordwrap': False,
    'margin': '1-1-1-1',
    'type': 'text',
    'figfont': 'standard',
}

class Format(ValIsDictCheckSubKeyTypesMixIn):
    def __init__(self, payload, *args, **kwargs):
        super().__init__(payload, *args, **kwargs)  # run mixin validations
        format_ = payload['format']

        #  list-constrained items
        valid_opts = {
            'justify': ['left', 'centre', 'center', 'right'],
            'type': ['text', 'code', 'figlet', 'markdown'],
        }
        # set defaults
        self.__dict__.update(DEFAULT_FORMAT)
        # self.justify: str = 'left'
        # self.color: int = 0
        # self.wordwrap: bool = False
        # self.margin: str = '1-1-1-1'
        # self.type: str = 'text'

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
                margin_pack = '0-0-0-0'

            self.l_margin, self.r_margin, self.t_margin, self.b_margin = [int(i) for i in margin_pack.split('-')]

        except (ValueError, AttributeError):
            fe = FormatError(f'{kwargs["_elem"]}. Could not parse margin parameter, expected \'x-y-z-w\'-style string.')
            fe.show()
            quit(fe.exit_code)

    def __repr__(self):
        kv = [f'{k}=\'{v}\'' for k, v in vars(self).items()]
        return f'Format({", ".join(kv)})'
