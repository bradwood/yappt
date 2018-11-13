"""This module holds miscellaneous validator Mixin classes for validating the incoming YAML."""


class KeyExistsMixIn:
    def __init__(self, payload, *args, _key, _exception, _elem, **kwargs):
        """Raise an error if _key is not in the payload."""
        try:
            _ = payload[_key]
        except (KeyError, AttributeError):
            excp = _exception(f'\'{_key}\' not found in {_elem}.')
            excp.show()
            quit(excp.exit_code)


class ValIsStrMixIn(KeyExistsMixIn):
    def __init__(self, payload, *args, _key, _exception, _elem, **kwargs):
        """Raise an error if payload[_key] is not a string."""
        super().__init__(payload,
                         *args,
                         _key=_key,
                         _exception=_exception,
                         _elem=_elem,
                         **kwargs)
        if not isinstance(payload[_key], str):
            excp = _exception(f'\'{_key}\' is not a string in {_elem}.')
            excp.show()
            quit(excp.exit_code)


class ValIsDictMixIn(KeyExistsMixIn):
    def __init__(self, payload, *args, _key, _exception, _elem, **kwargs):
        """Raise an error if payload[_key] is not a dict."""
        # call superclass validation first
        super().__init__(payload,
                         *args,
                         _key=_key,
                         _exception=_exception,
                         _elem=_elem,
                          **kwargs)
        if not isinstance(payload[_key], dict):
            excp = _exception(f'\'{_key}\' does not have a subtree in {_elem}.')
            excp.show()
            quit(excp.exit_code)


class ValIsDictHasSubKeysMixIn(ValIsDictMixIn):
    def __init__(self, payload, *args, _key, _exception, _elem, _sub_keys, **kwargs):
        """Raise an error if payload[_key] does not have _sub_keys in it."""
        # call superclass validation first
        super().__init__(payload,
                         *args,
                         _key=_key,
                         _exception=_exception,
                         _elem=_elem,
                         **kwargs)
        for sk in _sub_keys:
            if sk not in payload[_key]:
                excp = _exception(f'\'{_key}\' does not have item \'{sk}\' in {_elem}.')
                excp.show()
                quit(excp.exit_code)


class ValIsDictSubKeysFromMixIn(ValIsDictMixIn):
    def __init__(self, payload, *args, _key, _exception, _elem, _keys_from, **kwargs):
        """Raise an error if payload[_key] has sub keys other than _keys_from in it."""
        # call superclass validation first
        super().__init__(payload,
                         *args,
                         _key=_key,
                         _exception=_exception,
                         _elem=_elem,
                         **kwargs)
        for sk in payload[_key]:
            if sk not in _keys_from:
                excp = _exception(f'\'{sk}\' is not a valid item in {_elem}.')
                excp.show()
                quit(excp.exit_code)
