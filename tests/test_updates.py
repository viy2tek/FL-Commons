import base64
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
except ImportError:
    raise unittest.SkipTest('Install fl-commons[updates] to run signature tests')
from fl_commons.compatibility import builtin_profiles
from fl_commons.errors import OperationError
from fl_commons.updates import verify_manifest, stage_update, activate_update, rollback_update, _lock, _Redirect, _allowed_url, set_update_policy, check_updates, active_profiles, validate_candidate

KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))  # Test-only, never a production root.
ROOT = {'fixture': KEY.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)}
URL = 'https://github.com/viy2tek/FL-Commons/releases/download/compatibility-v1/profile.json'


def signed(payload):
    raw = json.dumps(payload).encode()
    return json.dumps({'key_id': 'fixture', 'payload': base64.b64encode(raw).decode(),
                      'signature': base64.b64encode(KEY.sign(b'FLCommons-update-v1\x00' + raw)).decode()}).encode()


def payload(data, revision=1, kind='adapter_profile'):
    return {'schema': 1, 'revision': revision, 'expires_at': 9999999999, 'min_runtime': '0.1.0',
            'artifacts': [{'id': 'native-profile', 'kind': kind, 'url': URL,
                           'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data),
                           'runtime_contract': 'fpsdk-20210311b-v1', 'distribution_status': 'original'}]}


class UpdateTests(unittest.TestCase):
    def test_production_rollback_accepts_retained_expired_profile_and_syncs_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath('root.json').write_text(json.dumps({'fixture': base64.b64encode(ROOT['fixture']).decode()}))
            executable = root / 'FL64.exe'
            binary = root / 'Plugins/Fruity/Effects/FL Commons API/FL Commons API_x64.dll'
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b'MZfixture')
            policy = root / 'native-policy.bin'
            inventory = {'selected_version': '26.1.7.5653', 'processes': [],
                         'installations': [{'path': str(executable), 'version': '26.1.7.5653'}]}
            with patch('fl_commons.host.inspect_host', return_value=inventory), patch('fl_commons.session.session_path', return_value=root / 'native-session.bin'), patch('fl_commons.session._dpapi', side_effect=lambda data, protect: data), patch('fl_commons.updates.time.time', return_value=1000):
                for revision, expiry in ((1, 2000), (2, 4000)):
                    profiles = copy.deepcopy(builtin_profiles())
                    if revision == 1:
                        profiles[0]['operations'] = {'transport.state': 'transport.state'}
                    data = json.dumps(profiles).encode()
                    document = payload(data, revision)
                    document['expires_at'] = expiry
                    stage = stage_update(verify_manifest(signed(document), ROOT, 0, 1000), root / 'staged', lambda u, n: data)
                    activate_update(stage, root, validate_candidate, False)
                self.assertTrue(policy.read_bytes().endswith(b'\n7\n'))
                with patch('fl_commons.updates.time.time', return_value=3000):
                    self.assertEqual(rollback_update(root, validate_candidate)['status'], 'active')
                self.assertTrue(policy.read_bytes().endswith(b'\n1\n'))
                before = json.loads((root / 'state.json').read_text())
                with patch('fl_commons.compatibility.save_native_policy', side_effect=OSError('fixture failure')):
                    with self.assertRaises(OSError):
                        rollback_update(root, validate_candidate)
                self.assertEqual(json.loads((root / 'state.json').read_text()), before)
                self.assertEqual(policy.read_bytes(), b'FLCommons-activation-pending')

    def test_failed_automatic_check_is_cached_without_advancing_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath('root.json').write_text(json.dumps({'fixture': base64.b64encode(ROOT['fixture']).decode()}))
            set_update_policy('automatic', root)
            with self.assertRaises(OSError):
                check_updates(root, lambda u, n: (_ for _ in ()).throw(OSError('offline')), automatic=True, now=4000)
            self.assertEqual(check_updates(root, automatic=True, now=4001)['status'], 'not_checked')
            self.assertEqual(json.loads((root / 'state.json').read_text())['highest_revision'], 0)

    def test_manual_policy_has_no_network_and_automatic_check_is_cached(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath('root.json').write_text(json.dumps({'fixture': base64.b64encode(ROOT['fixture']).decode()}))
            calls = []
            def fetch(url, limit):
                calls.append(url)
                return signed(self.document) if url.endswith('manifest.json') else self.data
            self.assertEqual(check_updates(root, fetch, automatic=True, now=4000)['status'], 'not_checked')
            self.assertEqual(calls, [])
            set_update_policy('automatic', root)
            result = check_updates(root, fetch, automatic=True, now=4000)
            self.assertEqual(result['status'], 'staged')
            self.assertEqual(check_updates(root, fetch, automatic=True, now=4001)['status'], 'not_checked')
            self.assertEqual(len(calls), 2)
            activate_update(Path(result['stage']), root, lambda s: True, False)
            self.assertEqual(active_profiles(root), builtin_profiles())

    def test_older_signed_feed_is_rejected_after_activation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath('root.json').write_text(json.dumps({'fixture': base64.b64encode(ROOT['fixture']).decode()}))
            stage = stage_update(verify_manifest(signed(payload(self.data, 2)), ROOT, 0, 1000), root / 'staged', lambda u, n: self.data)
            activate_update(stage, root, lambda s: True, False)
            with self.assertRaises(OperationError) as caught:
                check_updates(root, lambda u, n: signed(self.document), now=1000)
            self.assertEqual(caught.exception.code, 'update_replay')

    def setUp(self):
        self.data = json.dumps(builtin_profiles()).encode()
        self.document = payload(self.data)

    def test_signature_expiry_replay_and_trust_root(self):
        self.assertEqual(verify_manifest(signed(self.document), ROOT, 0, 1000)['revision'], 1)
        for keys, floor, now in (({}, 0, 1000), (ROOT, 1, 1000), (ROOT, 0, 9999999999)):
            with self.assertRaises(OperationError):
                verify_manifest(signed(self.document), keys, floor, now)
        tampered = json.loads(signed(self.document))
        tampered['payload'] = base64.b64encode(b'{}').decode()
        with self.assertRaises(OperationError):
            verify_manifest(json.dumps(tampered).encode(), ROOT, 0, 1000)

    def test_schema_and_artifact_origin_are_closed(self):
        for edit in (lambda p: p.update(revision=True),
                     lambda p: p.update(min_runtime='99.0.0'),
                     lambda p: p['artifacts'][0].update(url='https://evil.example/plugin.dll'),
                     lambda p: p['artifacts'][0].update(kind='executable'),
                     lambda p: p['artifacts'][0].update(distribution_status='sdk-derived'),
                     lambda p: p['artifacts'][0].update(size=33554433)):
            document = copy.deepcopy(self.document)
            edit(document)
            with self.assertRaises(OperationError):
                verify_manifest(signed(document), ROOT, 0, 1000)

    def test_stage_validates_hash_size_and_preserves_existing_state(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / 'staged'
            manifest = verify_manifest(signed(self.document), ROOT, 0, 1000)
            stage = stage_update(manifest, cache, lambda url, limit: self.data)
            self.assertTrue((stage / 'manifest.json').is_file())
            for data in (b'broken', self.data + b'x'):
                with self.assertRaises(OperationError):
                    stage_update(manifest, cache / 'failure', lambda url, limit: data)
            self.assertTrue((stage / 'manifest.json').is_file())

    def test_archive_traversal_and_sdk_material_are_rejected(self):
        for name in ('../outside.py', '/absolute.py', 'source/c/fp_plugclass.cpp', 'plugin.dll'):
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w') as archive:
                archive.writestr(name, 'invalid')
            data = buffer.getvalue()
            manifest = verify_manifest(signed(payload(data, kind='native_source')), ROOT, 0, 1000)
            with tempfile.TemporaryDirectory() as directory, self.assertRaises(OperationError):
                stage_update(manifest, Path(directory), lambda url, limit: data)

    def test_failed_activation_and_loaded_fl_preserve_current(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = verify_manifest(signed(self.document), ROOT, 0, 1000)
            stage = stage_update(manifest, root / 'staged', lambda url, limit: self.data)
            root.joinpath('root.json').write_text(json.dumps({'fixture': base64.b64encode(ROOT['fixture']).decode()}))
            self.assertEqual(activate_update(stage, root, lambda s: True, True)['status'], 'pending_reload')
            with self.assertRaises(OperationError):
                activate_update(stage, root, lambda s: False, False)
            self.assertEqual(json.loads((root / 'state.json').read_text())['current'], None)
            self.assertEqual(activate_update(stage, root, lambda s: True, False)['status'], 'active')

    def test_rollback_does_not_reset_replay_floor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath('root.json').write_text(json.dumps({'fixture': base64.b64encode(ROOT['fixture']).decode()}))
            for revision in (1, 2):
                manifest = verify_manifest(signed(payload(self.data, revision)), ROOT, revision - 1, 1000)
                stage = stage_update(manifest, root / 'staged', lambda url, limit: self.data)
                activate_update(stage, root, lambda s: True, False)
            rollback_update(root, lambda s: True)
            self.assertEqual(json.loads((root / 'state.json').read_text())['highest_revision'], 2)

    def test_concurrent_activation_is_rejected_and_crash_journal_resumes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath('root.json').write_text(json.dumps({'fixture': base64.b64encode(ROOT['fixture']).decode()}))
            manifest = verify_manifest(signed(self.document), ROOT, 0, 1000)
            stage = stage_update(manifest, root / 'staged', lambda url, limit: self.data)
            with _lock(root), self.assertRaises(OperationError) as caught:
                activate_update(stage, root, lambda s: True, False)
            self.assertEqual(caught.exception.code, 'update_busy')
            activate_update(stage, root, lambda s: True, True)
            self.assertEqual(activate_update(stage, root, lambda s: True, False)['status'], 'active')

    def test_untrusted_redirect_and_credential_url_are_rejected(self):
        self.assertFalse(_allowed_url('https://user:secret@github.com/viy2tek/FL-Commons/releases/download/a/b'))
        with self.assertRaises(OperationError):
            _Redirect().redirect_request(None, None, 302, '', {}, 'https://evil.example/a')

    def test_duplicate_keys_and_symlink_archive_are_rejected(self):
        with self.assertRaises(OperationError):
            verify_manifest(b'{"key_id":"fixture","key_id":"fixture"}', ROOT, 0, 1000)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            entry = zipfile.ZipInfo('link')
            entry.external_attr = (0o120777 << 16)
            archive.writestr(entry, '../private')
        data = buffer.getvalue()
        manifest = verify_manifest(signed(payload(data, kind='native_source')), ROOT, 0, 1000)
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(OperationError):
            stage_update(manifest, Path(directory), lambda url, limit: data)

    def test_original_runtime_activates_for_a_new_process_without_install_scripts(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr('fl_commons/__init__.py', '__version__ = "0.1.0"')
            archive.writestr('fl_commons/__main__.py', 'print("verified runtime fixture")')
        data = buffer.getvalue()
        document = payload(data, kind='python_runtime')
        document['artifacts'][0]['runtime_contract'] = 'flcommons-python-v1'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath('root.json').write_text(json.dumps({'fixture': base64.b64encode(ROOT['fixture']).decode()}))
            stage = stage_update(verify_manifest(signed(document), ROOT, 0, 1000), root / 'staged', lambda u, n: data)
            self.assertEqual(activate_update(stage, root, lambda p: True, False)['status'], 'active')
            self.assertTrue((stage / 'runtime/fl_commons/__main__.py').is_file())
