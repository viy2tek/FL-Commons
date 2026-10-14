import copy
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from fl_commons.compatibility import builtin_profiles, save_native_policy

DIRECTORY = Path(os.environ.get('FL_COMMONS_TEST_HOST', 'work/adaptive-native/api_host.exe')).resolve().parent


class PolicyTests(unittest.TestCase):
    def test_native_policy_is_bound_to_module_and_host_api(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary = DIRECTORY / 'policy_provider_test.exe'
            destination = root / 'FLCommons/native-policy.bin'
            profile = copy.deepcopy(builtin_profiles()[0])
            profile['host_api_versions'] = [25000000]
            save_native_policy(binary, profile, 25000000, destination)
            def probe(version):
                return subprocess.check_output([str(binary), str(root), str(version)], timeout=5).strip()
            self.assertEqual(probe(25000000), b'7')
            self.assertEqual(probe(25000001), b'0')
            destination.write_bytes(b'corrupt')
            self.assertEqual(probe(25000000), b'0')
            self.assertEqual(probe(26001007), b'0')

    def test_missing_policy_retains_builtin_contract_only(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = DIRECTORY / 'policy_provider_test.exe'
            self.assertEqual(subprocess.check_output([str(binary), directory, '26001007']).strip(), b'7')
            self.assertEqual(subprocess.check_output([str(binary), directory, '25000000']).strip(), b'0')
