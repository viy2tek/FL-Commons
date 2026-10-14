from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import contextlib
import io

from native.setup import install_plugin


class SetupTests(unittest.TestCase):
    def test_explicit_modern_installation_is_selected_instead_of_latest(self):
        from native.setup import main
        from fl_commons.compatibility import builtin_profiles
        profile = dict(builtin_profiles()[0], host_api_versions=[25000000])
        inventory = {'selected_version': '26.1.7.5653', 'processes': [], 'installations': [
            {'path': 'C:/FL25/FL64.exe', 'version': '25.0.0.1'},
            {'path': 'C:/FL26/FL64.exe', 'version': '26.1.7.5653'}]}
        with patch('sys.argv', ['setup.py', '--dll', 'fixture.dll', '--installation', 'C:/FL25/FL64.exe']), \
             patch('native.setup.inspect_host', return_value=inventory), \
             patch('native.setup.current_profiles', return_value=[profile]), \
             patch('native.setup.install_plugin', return_value=Path('fixture.dll')) as install, \
             patch('native.setup.save_native_policy'), contextlib.redirect_stdout(io.StringIO()):
            with patch('pathlib.Path.read_bytes', return_value=b'MZ'):
                main()
        self.assertEqual(install.call_args.args[1], Path('C:/FL25'))
    def test_running_fl_prevents_install_and_launch(self):
        from native.setup import main
        with patch("sys.argv", ["setup.py", "--dll", "unused.dll", "--launch"]), \
             patch("native.setup.inspect_host", return_value={"selected_version": "26.1.7.5653", "processes": [{"pid": 1}]}), \
             patch("native.setup.install_plugin") as install, \
             patch("native.setup.subprocess.Popen") as launch, \
             contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                main()
            install.assert_not_called()
            launch.assert_not_called()

    def test_launcher_preserves_the_same_token_given_to_fl(self):
        from native.setup import main
        from fl_commons.session import read_token
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / "FL64.exe"
            executable.write_bytes(b"MZ")
            installation = root / "Plugins/Fruity/Effects"
            installation.mkdir(parents=True)
            binary = root / "FL Commons API.dll"
            binary.write_bytes(b"MZ-original")
            session = root / "session.bin"
            inventory = {"selected_version": "26.1.7.5653", "processes": [],
                         "installations": [{"path": str(executable)}]}
            with patch("sys.argv", ["setup.py", "--dll", str(binary), "--launch"]), \
                 patch("native.setup.inspect_host", return_value=inventory), \
                 patch("native.setup.session_path", return_value=session), \
                 patch.dict("os.environ", {"FL_COMMONS_TOKEN": ""}), \
                 patch("native.setup.subprocess.Popen") as launch, \
                 contextlib.redirect_stdout(io.StringIO()):
                main()
                token = read_token(session)
                self.assertEqual(launch.call_args.kwargs["env"]["FL_COMMONS_TOKEN"], token)
                self.assertNotIn(token.encode(), session.read_bytes())

    def test_install_repeat_and_preserve_other_version(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary = root / "FL Commons API.dll"
            binary.write_bytes(b"MZ-original")
            installation = root / "FL Studio"
            effects = installation / "Plugins/Fruity/Effects"
            effects.mkdir(parents=True)
            destination = install_plugin(binary, installation)
            self.assertEqual(destination.name, "FL Commons API_x64.dll")
            self.assertEqual(destination.read_bytes(), b"MZ-original")
            self.assertEqual(install_plugin(binary, installation), destination)
            binary.write_bytes(b"MZ-new")
            with self.assertRaises(FileExistsError):
                install_plugin(binary, installation)
            self.assertEqual(destination.read_bytes(), b"MZ-original")

    def test_invalid_binary_and_installation_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary = root / "FL Commons API.dll"
            binary.write_bytes(b"invalid")
            with self.assertRaises(ValueError):
                install_plugin(binary, root)
            binary.write_bytes(b"MZ-original")
            with self.assertRaises(ValueError):
                install_plugin(binary, root)
            self.assertFalse((root / "Plugins").exists())
