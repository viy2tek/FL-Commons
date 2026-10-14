import subprocess
import sys
import unittest


class APITests(unittest.TestCase):
    def test_default_api_reports_no_real_backend(self):
        from fl_commons.api import API
        from fl_commons.errors import OperationError
        api = API()
        info = api.capabilities()
        self.assertEqual(info['mode'], 'disconnected')
        self.assertNotIn('transport.start', info['capabilities'])
        with self.assertRaises(OperationError) as caught:
            api.command('transport.start', {})
        self.assertEqual(caught.exception.code, 'backend_unavailable')

    def test_demo_works_without_midi_or_wire_imports(self):
        script = '''
import sys
from fl_commons.api import API
from fl_commons.server import create_server
api = API(demo=True)
assert api.capabilities()['mode'] == 'simulated'
api.command('transport.start', {})
assert api.command('transport.state', {})['playing']
api.command('transport.stop', {})
assert not api.command('transport.state', {})['playing']
assert not any(name.startswith(('mido', 'rtmidi', 'flcommons_wire', 'fl_commons.bridge')) for name in sys.modules)
'''
        result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_defaults_to_api_and_requires_explicit_midi(self):
        from fl_commons.cli import build_api
        from fl_commons.api import API
        self.assertIsInstance(build_api(demo=False, midi=False, input_name=None, output_name=None, key=None), API)
        with self.assertRaises(ValueError):
            build_api(demo=False, midi=False, input_name='port', output_name='port', key=None)
        with self.assertRaises(ValueError):
            build_api(demo=True, midi=True, input_name='port', output_name='port', key='a' * 64)
