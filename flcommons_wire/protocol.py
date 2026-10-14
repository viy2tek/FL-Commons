"""FL Commons protocol 1; no FL or third-party imports."""
import hashlib
import hmac
import json
from flcommons_common.validation import ProtocolError, strict_json, validate_key

PREFIX = b'\xf0\x7dFC\x01'
MAX_FRAME = 4096


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def encode(body, key):
    secret = validate_key(key)
    try:
        mac = hmac.new(secret, _canonical(body), hashlib.sha256).hexdigest()
        frame = PREFIX + _canonical({'body': body, 'mac': mac}) + b'\xf7'
    except (ValueError, TypeError, RecursionError) as exc:
        raise ProtocolError('Invalid body') from exc
    if len(frame) > MAX_FRAME:
        raise ProtocolError('Frame exceeds 4096 bytes')
    return frame


def decode(frame, key):
    secret = validate_key(key)
    if (not isinstance(frame, bytes) or len(frame) > MAX_FRAME or
            not frame.startswith(PREFIX) or not frame.endswith(b'\xf7') or
            any(b > 127 for b in frame[1:-1])):
        raise ProtocolError('Invalid SysEx frame')
    envelope = strict_json(frame[len(PREFIX):-1])
    if not isinstance(envelope, dict) or set(envelope) != {'body', 'mac'}:
        raise ProtocolError('Invalid envelope')
    body, mac = envelope['body'], envelope['mac']
    if not isinstance(body, dict) or not isinstance(mac, str) or len(mac) != 64 or not mac.isascii():
        raise ProtocolError('Invalid envelope fields')
    try:
        expected = hmac.new(secret, _canonical(body), hashlib.sha256).hexdigest()
    except (ValueError, TypeError, RecursionError) as exc:
        raise ProtocolError('Invalid body') from exc
    if not hmac.compare_digest(expected, mac):
        raise ProtocolError('Authentication failed')
    return body
