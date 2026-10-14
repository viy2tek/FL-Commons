"""Strict JSON and secret validation used by the API and optional transports."""
import json


class ProtocolError(ValueError):
    pass


def validate_key(key):
    if not isinstance(key, str) or len(key) < 32 or not key.isascii():
        raise ValueError('Secret must contain at least 32 ASCII characters')
    return key.encode('ascii')


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolError('Duplicate JSON key')
        result[key] = value
    return result


def strict_json(data):
    def reject_constant(value):
        raise ProtocolError('Non-finite JSON value')
    try:
        return json.loads(data, object_pairs_hook=_pairs, parse_constant=reject_constant)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ProtocolError('Invalid JSON') from exc
