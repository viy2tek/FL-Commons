import sys
import tempfile
from pathlib import Path
import unittest


@unittest.skipUnless(sys.platform == "win32", "Windows DPAPI")
class SessionTests(unittest.TestCase):
    def test_encrypted_token_roundtrip_and_corruption(self):
        from fl_commons.session import save_token, read_token
        token = "a" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.bin"
            save_token(token, path)
            self.assertNotIn(token.encode(), path.read_bytes())
            self.assertEqual(read_token(path), token)
            path.write_bytes(b"corrupted")
            with self.assertRaises(OSError):
                read_token(path)

    def test_invalid_token_never_replaces_session(self):
        from fl_commons.session import save_token, read_token
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.bin"
            save_token("a" * 64, path)
            for value in ("short", " " * 64, "b" * 257):
                with self.assertRaises(ValueError):
                    save_token(value, path)
            self.assertEqual(read_token(path), "a" * 64)
