import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
try:
    from tools.sign_update import main
except ImportError:
    raise unittest.SkipTest('Install fl-commons[updates] to run publisher tests')


@unittest.skipUnless(sys.platform == 'win32', 'Publisher private storage uses Windows DPAPI')
class SignerTests(unittest.TestCase):
    def test_private_key_stays_protected_outside_repo(self):
        with tempfile.TemporaryDirectory() as directory:
            key, root = Path(directory) / 'publisher.bin', Path(directory) / 'root.json'
            with contextlib.redirect_stdout(io.StringIO()):
                main(['--create-key', '--key', str(key), '--public-output', str(root)])
            self.assertNotIn(b'FLCommons-publisher-v1', key.read_bytes())
            self.assertEqual(len(json.loads(root.read_text())), 1)
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(['--create-key', '--key', str(key)])

    def test_existing_public_root_is_not_silently_replaced_or_orphaned(self):
        with tempfile.TemporaryDirectory() as directory:
            key, root = Path(directory) / 'publisher.bin', Path(directory) / 'root.json'
            root.write_text('{"existing":"different"}')
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(['--create-key', '--key', str(key), '--public-output', str(root)])
            self.assertEqual(root.read_text(), '{"existing":"different"}')
            self.assertFalse(key.exists())
