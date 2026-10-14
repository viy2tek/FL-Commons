import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from fl_commons.session import save_token

DIRECTORY = Path(os.environ.get("FL_COMMONS_TEST_HOST", "work/native-api/api_host.exe")).resolve().parent


class TokenProviderTests(unittest.TestCase):
    def test_native_reads_python_dpapi_token_without_launcher_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "sessão"
            path = root / "FLCommons/native-session.bin"
            save_token("a" * 64, path)
            result = subprocess.run([str(DIRECTORY / "token_provider_test.exe"), str(root)],
                                    capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 0)
            path.write_bytes(b"corrupted")
            result = subprocess.run([str(DIRECTORY / "token_provider_test.exe"), str(root)],
                                    capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 1)
