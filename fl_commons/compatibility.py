"""Resolve implemented operations by explicit interface evidence, never by names alone."""
import json
from pathlib import Path
import re
import hashlib
import os
import tempfile

from .errors import OperationError

METHODS = ('transport.state', 'transport.play_pause', 'transport.stop')
CONTRACT = 'fpsdk-20210311b-v1'
FIELDS = {'schema', 'adapter_id', 'runtime_contract', 'host_major_min',
          'host_api_versions', 'operations', 'tested_builds'}


def version_tuple(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{1,5}(?:\.[0-9]{1,5}){3}', value):
        return None
    result = tuple(map(int, value.split('.')))
    return result if max(result) <= 65535 else None


def validate_profile(data):
    valid = isinstance(data, dict) and set(data) == FIELDS
    if valid:
        valid = (type(data['schema']) is int and data['schema'] == 1 and
                 data['adapter_id'] == 'native-sdk-transport-v1' and
                 data['runtime_contract'] == CONTRACT and
                 type(data['host_major_min']) is int and data['host_major_min'] >= 25 and
                 isinstance(data['host_api_versions'], list) and bool(data['host_api_versions']) and
                 all(type(v) is int and 25000000 <= v <= 65535000000 for v in data['host_api_versions']) and
                 isinstance(data['operations'], dict) and bool(data['operations']) and
                 all(k in METHODS and v == k for k, v in data['operations'].items()) and
                 isinstance(data['tested_builds'], list) and
                 all(version_tuple(v) and version_tuple(v)[0] >= 25 for v in data['tested_builds']))
    if not valid:
        raise OperationError('invalid_profile', 'Unsupported or invalid compatibility profile')
    return data


def builtin_profiles():
    data = json.loads((Path(__file__).parent / 'data/compatibility.json').read_text(encoding='utf-8'))
    return [validate_profile(profile) for profile in data]


def host_api_from_build(build):
    version = version_tuple(build)
    if not version or version[0] < 25 or version[1] >= 1000 or version[2] >= 1000:
        raise OperationError('version_unverified', 'Host API version cannot be derived from this installation')
    return version[0] * 1000000 + version[1] * 1000 + version[2]


def select_install_profile(build, profiles):
    host_api = host_api_from_build(build)
    for profile in profiles:
        validate_profile(profile)
        if version_tuple(build)[0] >= profile['host_major_min'] and host_api in profile['host_api_versions']:
            return profile
    raise OperationError('capability_unavailable', 'No verified native ABI profile is available; a compatibility update is required')


def save_native_policy(binary, profile, host_api, path=None):
    from .session import _dpapi, session_path
    validate_profile(profile)
    if host_api not in profile['host_api_versions']:
        raise OperationError('invalid_profile', 'Host API is not covered by this profile')
    digest = hashlib.sha256(Path(binary).read_bytes()).hexdigest()
    mask = sum(1 << METHODS.index(method) for method in profile['operations'])
    record = f'FLCommons-policy-v1\n{digest}\n{CONTRACT}\n{host_api}\n{mask}\n'.encode('ascii')
    destination = Path(path) if path is not None else session_path().with_name('native-policy.bin')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(_dpapi(record, True))
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return destination


def resolve_operation(method, observed, profiles):
    unavailable = {'adapter_id': None, 'method': method, 'status': 'unsupported',
                   'reason': 'No implemented adapter matches the observed interface',
                   'requirements': {}, 'tested_builds': []}
    version = version_tuple(observed.get('fl_build'))
    if method not in METHODS or version is None or version[0] < 25:
        return unavailable
    if type(observed.get('host_version_raw')) is not int or observed['host_version_raw'] // 1000000 != version[0]:
        return unavailable
    candidates = []
    for profile in profiles:
        validate_profile(profile)
        if (version[0] >= profile['host_major_min'] and
            observed.get('runtime_contract') == profile['runtime_contract'] and
            type(observed.get('host_version_raw')) is int and
            observed['host_version_raw'] in profile['host_api_versions'] and
            method in profile['operations']):
            candidates.append(profile)
    if not candidates:
        return unavailable
    profile = next((p for p in candidates if observed['fl_build'] in p['tested_builds']), candidates[0])
    status = 'limited' if observed['fl_build'] in profile['tested_builds'] else 'experimental'
    reason = 'Documented interface matches; build-specific evidence is reported separately'
    if not observed.get('gui_responsive') or method == 'transport.state' and not observed.get('state_callback_observed'):
        status, reason = 'temporarily_unavailable', 'Required GUI or state callback has not been observed'
    return dict(unavailable, adapter_id=profile['adapter_id'], method=profile['operations'][method],
                status=status, reason=reason, requirements={'runtime_contract': CONTRACT,
                'host_api_versions': profile['host_api_versions']}, tested_builds=profile['tested_builds'])
