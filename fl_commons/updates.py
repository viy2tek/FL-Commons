"""Verified update staging; downloads never execute and loaded native DLLs never change."""
import base64
from contextlib import contextmanager
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import time
from urllib.parse import urlsplit
import urllib.request
import zipfile
import subprocess
import sys

from flcommons_common.validation import strict_json, ProtocolError
from .errors import OperationError
from .compatibility import validate_profile

PREFIX = b'FLCommons-update-v1\x00'
CHANNEL = 'https://raw.githubusercontent.com/viy2tek/FL-Commons/compatibility-v1/updates/manifest.json'
MAX_MANIFEST = 65536
MAX_ARTIFACT = 32 * 1024 * 1024
FIELDS = {'schema', 'revision', 'expires_at', 'min_runtime', 'artifacts'}
ARTIFACT_FIELDS = {'id', 'kind', 'url', 'sha256', 'size', 'runtime_contract', 'distribution_status'}


def _fail(code, message):
    raise OperationError(code, message)


def _json(data):
    try:
        return strict_json(data)
    except (ProtocolError, UnicodeError, ValueError) as error:
        raise OperationError('update_invalid', 'Invalid update JSON') from error


def _version(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{1,5}(\.[0-9]{1,5}){2}', value):
        _fail('update_invalid', 'Invalid runtime requirement')
    return tuple(map(int, value.split('.')))


def _allowed_url(url, redirect=False):
    if not isinstance(url, str):
        return False
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        return False
    if parts.scheme != 'https' or parts.username or parts.password or parts.fragment or port not in (None, 443):
        return False
    if parts.hostname == 'github.com':
        return parts.path.startswith('/viy2tek/FL-Commons/releases/download/') and not parts.query and '%' not in parts.path and '..' not in parts.path
    if parts.hostname == 'raw.githubusercontent.com':
        return parts.path.startswith('/viy2tek/FL-Commons/compatibility-v1/updates/') and not parts.query and '%' not in parts.path and '..' not in parts.path
    return redirect and parts.hostname in ('release-assets.githubusercontent.com', 'objects.githubusercontent.com')


def verify_manifest(envelope, trusted_keys, min_revision, now):
    if not isinstance(envelope, bytes) or not 0 < len(envelope) <= MAX_MANIFEST:
        _fail('update_invalid', 'Manifest size is invalid')
    outer = _json(envelope)
    if not isinstance(outer, dict) or set(outer) != {'key_id', 'payload', 'signature'}:
        _fail('update_invalid', 'Invalid signed envelope')
    if not isinstance(outer['key_id'], str) or outer['key_id'] not in trusted_keys:
        _fail('update_untrusted', 'Manifest signing key is not pinned')
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
    except ImportError as error:
        raise OperationError('updates_dependency_missing', 'Install fl-commons[updates] to verify signatures') from error
    try:
        raw = base64.b64decode(outer['payload'], validate=True)
        signature = base64.b64decode(outer['signature'], validate=True)
        Ed25519PublicKey.from_public_bytes(trusted_keys[outer['key_id']]).verify(signature, PREFIX + raw)
    except (ValueError, TypeError, InvalidSignature) as error:
        raise OperationError('update_untrusted', 'Manifest signature is invalid') from error
    data = _json(raw)
    if not isinstance(data, dict) or set(data) != FIELDS:
        _fail('update_invalid', 'Invalid manifest fields')
    if type(data['schema']) is not int or data['schema'] != 1 or type(data['revision']) is not int or data['revision'] <= 0:
        _fail('update_invalid', 'Invalid manifest revision')
    if data['revision'] <= min_revision:
        _fail('update_replay', 'Manifest does not advance the accepted revision')
    if type(data['expires_at']) is not int or data['expires_at'] <= now:
        _fail('update_expired', 'Manifest has expired')
    if _version(data['min_runtime']) > (0, 1, 0):
        _fail('runtime_update_required', 'This runtime cannot consume the update')
    artifacts = data['artifacts']
    if not isinstance(artifacts, list) or not 1 <= len(artifacts) <= 16:
        _fail('update_invalid', 'Invalid artifact list')
    ids = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict) or set(artifact) != ARTIFACT_FIELDS:
            _fail('update_invalid', 'Invalid artifact fields')
        if not isinstance(artifact['id'], str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', artifact['id']) or artifact['id'] in ids:
            _fail('update_invalid', 'Invalid or duplicate artifact identity')
        ids.add(artifact['id'])
        if artifact['kind'] not in ('adapter_profile', 'native_source', 'python_runtime') or artifact['distribution_status'] != 'original':
            _fail('update_invalid', 'Artifact distribution is not permitted')
        contract = 'flcommons-python-v1' if artifact['kind'] == 'python_runtime' else 'fpsdk-20210311b-v1'
        if artifact['runtime_contract'] != contract or not _allowed_url(artifact['url']):
            _fail('update_invalid', 'Artifact origin or contract is invalid')
        if not isinstance(artifact['sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', artifact['sha256']):
            _fail('update_invalid', 'Invalid artifact digest')
        if type(artifact['size']) is not int or not 0 < artifact['size'] <= MAX_ARTIFACT:
            _fail('update_invalid', 'Invalid artifact size')
    return dict(data, _envelope=envelope)


class _Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        if not _allowed_url(newurl, redirect=True):
            _fail('update_origin_rejected', 'Update redirected outside the trusted asset hosts')
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def fetch_update(url, limit):
    if not _allowed_url(url):
        _fail('update_origin_rejected', 'Update URL is not in the configured release channel')
    try:
        opener = urllib.request.build_opener(_Redirect())
        with opener.open(urllib.request.Request(url, headers={'User-Agent': 'FLCommons/0.1'}), timeout=5) as response:
            data = response.read(limit + 1)
        if len(data) > limit:
            _fail('update_too_large', 'Update exceeds its size limit')
        return data
    except OSError as error:
        raise OperationError('update_unavailable', 'Update channel is unavailable') from error


def _profiles(data):
    value = _json(data)
    if not isinstance(value, list) or not 1 <= len(value) <= 32:
        _fail('invalid_profile', 'Invalid adapter profile list')
    return [validate_profile(profile) for profile in value]


def _archive(data, kind):
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
        names, total = set(), 0
        for entry in archive.infolist():
            name = entry.filename
            parts = PurePosixPath(name).parts
            total += entry.file_size
            if (not parts or name.startswith('/') or '\\' in name or ':' in name or
                '..' in parts or name.casefold() in names or stat.S_ISLNK(entry.external_attr >> 16) or total > MAX_ARTIFACT):
                _fail('update_invalid', 'Unsafe archive entry')
            names.add(name.casefold())
            if Path(name).suffix.lower() in ('.dll', '.exe', '.obj', '.lib', '.exp', '.dpapi', '.bin') or parts[-1] in ('fp_def.h', 'fp_plugclass.h', 'fp_plugclass.cpp', 'generictransport.h', 'flcommons_config.py', '.env'):
                _fail('update_invalid', 'Archive contains disallowed binary or SDK material')
            if kind == 'python_runtime' and parts[0] not in ('fl_commons', 'flcommons', 'flcommons_common', 'flcommons_wire') and not re.fullmatch(r'fl_commons-[0-9.]+\.dist-info', parts[0]):
                _fail('update_invalid', 'Runtime archive contains an unrelated package')
        if not names or archive.testzip() is not None:
            _fail('update_invalid', 'Invalid archive contents')
        return archive
    except (zipfile.BadZipFile, OSError, RuntimeError) as error:
        raise OperationError('update_invalid', 'Invalid update archive') from error


def _check_artifact(data, artifact):
    if len(data) != artifact['size'] or hashlib.sha256(data).hexdigest() != artifact['sha256']:
        _fail('update_integrity', 'Artifact digest or size does not match its signed manifest')
    if artifact['kind'] == 'adapter_profile':
        _profiles(data)
    else:
        _archive(data, artifact['kind']).close()


def stage_update(manifest, cache_dir, fetch=fetch_update):
    cache = Path(cache_dir).resolve()
    cache.mkdir(parents=True, exist_ok=True)
    envelope = manifest['_envelope']
    destination = cache / hashlib.sha256(envelope).hexdigest()
    # TemporaryDirectory only owns the directory created within this resolved cache.
    with tempfile.TemporaryDirectory(prefix='.stage-', dir=cache) as temporary:
        path = Path(temporary)
        assert path.parent.resolve() == cache
        for artifact in manifest['artifacts']:
            data = fetch(artifact['url'], artifact['size'])
            _check_artifact(data, artifact)
            (path / artifact['sha256']).write_bytes(data)
        (path / 'manifest.json').write_bytes(envelope)
        if not destination.exists():
            os.replace(path, destination)
        else:
            for artifact in manifest['artifacts']:
                _check_artifact((destination / artifact['sha256']).read_bytes(), artifact)
    return destination


def update_directory():
    return Path(os.environ.get('LOCALAPPDATA', os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share')))) / 'FLCommons/updates'


def trusted_keys(state_dir):
    path = Path(state_dir) / 'root.json'
    if not path.exists():
        path = Path(__file__).parent / 'data/update-root.json'
    if not path.exists():
        _fail('update_trust_unconfigured', 'No publisher verification key has been pinned')
    value = _json(path.read_bytes()[:MAX_MANIFEST + 1])
    if not isinstance(value, dict) or not 1 <= len(value) <= 8:
        _fail('update_untrusted', 'Invalid trust root')
    try:
        result = {key: base64.b64decode(data, validate=True) for key, data in value.items()}
        if any(not isinstance(key, str) or len(data) != 32 for key, data in result.items()):
            raise ValueError()
        return result
    except (ValueError, TypeError) as error:
        raise OperationError('update_untrusted', 'Invalid trust root') from error


def _state(directory):
    path = Path(directory) / 'state.json'
    if not path.exists():
        return {'schema': 1, 'highest_revision': 0, 'current': None, 'previous': None,
                'pending': None, 'policy': 'manual', 'last_check': 0}
    value = _json(path.read_bytes()[:MAX_MANIFEST + 1])
    if not isinstance(value, dict) or set(value) != {'schema', 'highest_revision', 'current', 'previous', 'pending', 'policy', 'last_check'} or value['schema'] != 1 or type(value['highest_revision']) is not int or value['highest_revision'] < 0 or value['policy'] not in ('manual', 'automatic') or type(value['last_check']) is not int:
        _fail('update_state_invalid', 'Invalid update activation state')
    for key in ('current', 'previous', 'pending'):
        if value[key] is not None and (not isinstance(value[key], str) or not re.fullmatch(r'[0-9a-f]{64}', value[key])):
            _fail('update_state_invalid', 'Invalid activation identity')
    return value


def _save(directory, state):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(json.dumps(state, sort_keys=True).encode())
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, directory / 'state.json')
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


@contextmanager
def _lock(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'activation.lock').open('a+b') as stream:
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise OperationError('update_busy', 'Another activation is in progress') from error
        try:
            yield
        finally:
            if os.name == 'nt':
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def _validated_stage(stage, directory, now=None):
    stage, directory = Path(stage).resolve(), Path(directory).resolve()
    if stage.parent != directory / 'staged' or not re.fullmatch(r'[0-9a-f]{64}', stage.name):
        _fail('update_invalid', 'Stage is outside the activation cache')
    envelope = (stage / 'manifest.json').read_bytes()
    if hashlib.sha256(envelope).hexdigest() != stage.name:
        _fail('update_integrity', 'Staged manifest identity changed')
    manifest = verify_manifest(envelope, trusted_keys(directory), 0, int(time.time()) if now is None else now)
    for artifact in manifest['artifacts']:
        _check_artifact((stage / artifact['sha256']).read_bytes(), artifact)
    return manifest


def activate_update(stage, state_dir, validate, host_running):
    directory = Path(state_dir).resolve()
    with _lock(directory):
        state = _state(directory)
        manifest = _validated_stage(stage, directory)
        identity = Path(stage).name
        if manifest['revision'] <= state['highest_revision'] and identity not in (state['pending'], state['current']):
            _fail('update_replay', 'Staged update is older than accepted state')
        state.update(highest_revision=max(state['highest_revision'], manifest['revision']), pending=identity)
        _save(directory, state)
        if host_running:
            return {'status': 'pending_reload', 'revision': manifest['revision']}
        if any(a['kind'] == 'native_source' for a in manifest['artifacts']):
            return {'status': 'rebuild_required', 'revision': manifest['revision'], 'stage': str(Path(stage))}
        try:
            if not validate(Path(stage)):
                _fail('update_validation_failed', 'Read-only activation validation failed')
            for artifact in manifest['artifacts']:
                if artifact['kind'] == 'python_runtime':
                    runtime = Path(stage) / 'runtime'
                    if not runtime.exists():
                        with _archive((Path(stage) / artifact['sha256']).read_bytes(), 'python_runtime') as archive:
                            archive.extractall(runtime)
        except Exception:
            # Keep the exact verified stage retryable after a transient read-only failure.
            _save(directory, state)
            raise
        if state['current'] != identity:
            state['previous'], state['current'] = state['current'], identity
        state['pending'] = None
        _commit_activation(directory, state, Path(stage), validate)
        return {'status': 'active', 'revision': manifest['revision']}


def rollback_update(state_dir, validate):
    directory = Path(state_dir).resolve()
    with _lock(directory):
        state = _state(directory)
        if state['previous'] is None:
            _fail('rollback_unavailable', 'No retained verified update is available')
        stage = directory / 'staged' / state['previous']
        _validated_stage(stage, directory, now=0)  # Explicit rollback may retain an expired previously verified artifact.
        if not validate(stage):
            _fail('update_validation_failed', 'Rollback validation failed')
        state['current'], state['previous'], state['pending'] = state['previous'], state['current'], None
        _commit_activation(directory, state, stage, validate)
        return {'status': 'active', 'highest_revision': state['highest_revision']}


def _commit_activation(directory, state, stage, validate):
    if validate is not validate_candidate:
        _save(directory, state)
        return
    from .host import inspect_host
    from .compatibility import select_install_profile, save_native_policy, host_api_from_build
    from .session import session_path
    inventory = inspect_host()
    if inventory['processes']:
        _fail('update_busy', 'FL must be closed before native policy activation')
    manifest = _validated_stage(stage, directory, now=0)
    profiles = [p for a in manifest['artifacts'] if a['kind'] == 'adapter_profile'
                for p in _profiles((stage / a['sha256']).read_bytes())]
    candidates = [entry for entry in inventory['installations']
                  if Path(entry['path']).name.lower() == 'fl64.exe'
                  and entry['version'] == inventory['selected_version']]
    if not profiles or not candidates:
        _save(directory, state)
        return
    if len(candidates) != 1:
        _fail('update_validation_failed', 'Select one standard native installation before activation')
    binary = Path(candidates[0]['path']).parent / 'Plugins/Fruity/Effects/FL Commons API/FL Commons API_x64.dll'
    if not binary.exists():
        _save(directory, state)  # Setup binds the policy when the component is first installed.
        return
    profile = select_install_profile(inventory['selected_version'], profiles)
    destination = session_path().with_name('native-policy.bin')
    destination.parent.mkdir(parents=True, exist_ok=True)
    previous = _state(directory)
    # A crash between the two records must disable native dispatch, never retain broader permissions.
    destination.write_bytes(b'FLCommons-activation-pending')
    try:
        _save(directory, state)
        save_native_policy(binary, profile, host_api_from_build(inventory['selected_version']), destination)
    except Exception:
        _save(directory, previous)
        raise


def active_profiles(state_dir=None):
    directory = Path(state_dir) if state_dir is not None else update_directory()
    state = _state(directory)
    if state['current'] is None:
        return []
    stage = directory / 'staged' / state['current']
    manifest = _validated_stage(stage, directory, now=0)
    profiles = []
    for artifact in manifest['artifacts']:
        if artifact['kind'] == 'adapter_profile':
            profiles.extend(_profiles((stage / artifact['sha256']).read_bytes()))
    return profiles


def update_status(state_dir=None):
    directory = Path(state_dir) if state_dir is not None else update_directory()
    state = _state(directory)
    try:
        configured = bool(trusted_keys(directory))
    except OperationError:
        configured = False
    return dict(state, publisher_trust_configured=configured)


def set_update_policy(policy, state_dir=None):
    if policy not in ('manual', 'automatic'):
        _fail('invalid_params', 'Policy must be manual or automatic')
    directory = Path(state_dir) if state_dir is not None else update_directory()
    with _lock(directory):
        state = _state(directory)
        state['policy'] = policy
        _save(directory, state)
    return dict(state)


def check_updates(state_dir=None, fetch=fetch_update, automatic=False, now=None):
    directory = Path(state_dir) if state_dir is not None else update_directory()
    epoch = int(time.time()) if now is None else now
    with _lock(directory):
        state = _state(directory)
        if automatic and (state['policy'] != 'automatic' or epoch - state['last_check'] < 3600):
            return {'status': 'not_checked', 'reason': 'Policy or bounded cache'}
        roots = trusted_keys(directory)
        state['last_check'] = epoch
        _save(directory, state)  # Bound failed automatic checks as well as successful checks.
        envelope = fetch(CHANNEL, MAX_MANIFEST)
        try:
            manifest = verify_manifest(envelope, roots, state['highest_revision'], epoch)
        except OperationError as error:
            if error.code != 'update_replay':
                raise
            # An unchanged signed feed is normal; recheck signature/schema, not a downgrade activation.
            previous = verify_manifest(envelope, roots, 0, epoch)
            identity = hashlib.sha256(envelope).hexdigest()
            if previous['revision'] != state['highest_revision'] or identity not in (state['current'], state['previous'], state['pending']):
                raise
            state['last_check'] = epoch
            _save(directory, state)
            return {'status': 'up_to_date', 'highest_revision': state['highest_revision']}
        stage = stage_update(manifest, directory / 'staged', fetch)
        state.update(pending=stage.name, highest_revision=manifest['revision'], last_check=epoch)
        _save(directory, state)
        return {'status': 'staged', 'revision': manifest['revision'], 'stage': str(stage)}


def connection_updates(policy=None):
    directory = update_directory()
    try:
        if policy is not None:
            set_update_policy(policy, directory)
        result = check_updates(directory, automatic=True)
        state = _state(directory)
        if state['policy'] == 'automatic' and state['pending']:
            # FL is connected/running: stage only, never modify its loaded native component.
            return dict(result, activation='pending_reload')
        return result
    except (OperationError, OSError) as error:
        return {'status': 'unavailable', 'reason': getattr(error, 'code', 'update_io_error')}


def host_running():
    from .host import inspect_host
    try:
        return bool(inspect_host()['processes'])
    except OperationError:
        return True  # Unknown host state never authorizes native activation.


def validate_candidate(stage):
    from .host import inspect_host
    from .compatibility import select_install_profile
    try:
        inventory = inspect_host()
        manifest = _validated_stage(stage, Path(stage).parent.parent, now=0)
        profiles = [p for a in manifest['artifacts'] if a['kind'] == 'adapter_profile'
                    for p in _profiles((Path(stage) / a['sha256']).read_bytes())]
        if profiles:
            select_install_profile(inventory['selected_version'], profiles)
        return True
    except (OperationError, OSError, KeyError):
        return False


def apply_pending(state_dir=None):
    directory = Path(state_dir) if state_dir is not None else update_directory()
    state = _state(directory)
    if state['pending'] is None:
        return {'status': 'no_pending_update'}
    return activate_update(directory / 'staged' / state['pending'], directory,
                           validate_candidate, host_running())


def run_runtime(arguments, state_dir=None):
    directory = Path(state_dir) if state_dir is not None else update_directory()
    state = _state(directory)
    if state['current'] is None:
        _fail('runtime_unavailable', 'No verified runtime is active')
    stage = directory / 'staged' / state['current']
    manifest = _validated_stage(stage, directory, now=0)
    if not any(a['kind'] == 'python_runtime' for a in manifest['artifacts']):
        _fail('runtime_unavailable', 'Active update contains no Python runtime')
    runtime = stage / 'runtime'
    # Recreate from verified bytes instead of trusting previously extracted mutable modules.
    with tempfile.TemporaryDirectory(prefix='.runtime-', dir=directory) as temporary:
        execution = Path(temporary)
        assert execution.parent.resolve() == directory.resolve()
        for artifact in manifest['artifacts']:
            if artifact['kind'] == 'python_runtime':
                with _archive((stage / artifact['sha256']).read_bytes(), 'python_runtime') as archive:
                    archive.extractall(execution)
        return subprocess.call([sys.executable, '-m', 'fl_commons', *arguments], cwd=execution,
                               env=dict(os.environ, PYTHONPATH=str(execution)))
