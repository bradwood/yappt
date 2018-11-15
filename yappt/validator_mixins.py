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

class ValIsDictCheckSubKeyTypesMixIn(ValIsDictSubKeysFromMixIn):
    def __init__(self, payload, *args, _key, _exception, _elem, _keys_from, _type_list, **kwargs):
        """Raise an error if payload[_key] has sub keys which don't comply with types in _type_list ."""
        # call superclass validation first
        super().__init__(payload,
                         *args,
                         _key=_key,
                         _exception=_exception,
                         _keys_from=_keys_from,
                         _elem=_elem,
                         **kwargs)
        if len(_keys_from) != len(_type_list):
            raise ValueError(f'_keys_from length differs from _type_list length')

        for subkey in payload[_key]:
            req_type = _type_list[_keys_from.index(subkey)]
            if not isinstance(payload[_key][subkey], req_type):
                excp = _exception(f'\'{subkey}: {payload[_key][subkey]}\' is not of a valid type in {_elem}. Expected {req_type.__name__}.')
                excp.show()
                quit(excp.exit_code)
