"""Evidence-backed SDK interface facts; never a raw native-call endpoint."""
import json
from pathlib import Path

from .errors import OperationError


def sdk_catalog(offset=0, limit=32, domain=None):
    if (type(offset) is not int or offset < 0 or type(limit) is not int or
            not 1 <= limit <= 32 or domain is not None and not isinstance(domain, str)):
        raise OperationError('invalid_params', 'Use offset >= 0, limit 1..32 and a known domain')
    with (Path(__file__).parent / 'data' / 'sdk_catalog.json').open(encoding='utf-8') as stream:
        data = json.load(stream)
    entries = data.pop('entries')
    domains = sorted({entry['domain'] for entry in entries})
    if domain is not None:
        if domain not in domains:
            raise OperationError('invalid_params', 'Unknown catalog domain')
        entries = [entry for entry in entries if entry['domain'] == domain]
    total = len(entries)
    return dict(data, domains=domains, total=total, offset=offset,
                entries=entries[offset:offset + limit],
                next_offset=offset + limit if offset + limit < total else None)
