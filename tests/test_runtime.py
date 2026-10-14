import importlib.util
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from test_adapter import KEY


class RuntimeTests(unittest.TestCase):
    def test_bundle_contains_portable_adapter_without_overwrite(self):
        from fl_commons.cli import prepare_adapter
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'FL Commons'
            prepare_adapter(output, KEY)
            self.assertTrue((output / 'flcommons_wire' / 'adapter.py').is_file())
            self.assertTrue((output / 'device_FLCommons.py').is_file())
            self.assertTrue((output / 'flcommons_wire' / 'LICENSE').is_file())
            with self.assertRaises(FileExistsError):
                prepare_adapter(output, KEY)

    def test_script_queues_and_replies_only_from_idle(self):
        from fl_commons.cli import prepare_adapter
        from flcommons_wire.protocol import encode, decode
        import time
        replies = []
        modules = {'flcommons_config': SimpleNamespace(SECRET=KEY),
                   'general': SimpleNamespace(getVersion=lambda: 1),
                   'ui': SimpleNamespace(getVersion=lambda: 'fixture'),
                   'transport': SimpleNamespace(start=lambda: None),
                   'device': SimpleNamespace(isAssigned=lambda: True,
                                             midiOutSysex=replies.append)}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'bundle'
            prepare_adapter(output, KEY)
            spec = importlib.util.spec_from_file_location('device_fixture', output / 'device_FLCommons.py')
            script = importlib.util.module_from_spec(spec)
            with patch.dict(sys.modules, modules):
                spec.loader.exec_module(script)
                script.OnInit()
                body = dict(kind='request', protocol=1, client='fixture', id='1', seq=1,
                            boot=None, method='bridge.hello', params={}, sent_at=time.time())
                event = SimpleNamespace(sysex=encode(body, KEY), handled=False)
                script.OnSysEx(event)
                self.assertTrue(event.handled)
                self.assertEqual(replies, [])
                script.OnIdle()
                self.assertEqual(decode(replies[0], KEY)['result']['fl_version'], 'fixture')
                other = SimpleNamespace(sysex=b'\xf0\x01\xf7', handled=False)
                script.OnSysEx(other)
                self.assertFalse(other.handled)
                script.OnDeInit()

    def test_simulator_uses_real_authenticated_protocol(self):
        from fl_commons.simulator import SimulatedWire
        from fl_commons.optional_midi import MidiBackend
        bridge = MidiBackend(SimulatedWire(KEY), KEY)
        self.assertEqual(bridge.capabilities()['mode'], 'simulated')
        bridge.command('transport.start', {})
        self.assertTrue(bridge.command('transport.state', {})['playing'])
        bridge.close()

    def test_midi_backend_preserves_full_frame(self):
        from fl_commons.midi import MidiWire
        from flcommons_wire.protocol import encode
        sent = []
        holder = {}
        class Message:
            type = 'sysex'
            def __init__(self, kind, data):
                self.data = data
            def bytes(self):
                return [240] + list(self.data) + [247]
        backend = SimpleNamespace(
            get_input_names=lambda: ['return'], get_output_names=lambda: ['send'],
            open_input=lambda name, callback: holder.update(callback=callback) or SimpleNamespace(close=lambda: None),
            open_output=lambda name: SimpleNamespace(send=sent.append, close=lambda: None))
        with patch.dict(sys.modules, {'mido': SimpleNamespace(Backend=lambda name: backend, Message=Message)}):
            wire = MidiWire('return', 'send')
            frame = encode({'value': 1}, KEY)
            wire.send(frame)
            holder['callback'](sent[0])
            self.assertEqual(wire.receive(0.01), frame)
            wire.close()


if __name__ == '__main__':
    unittest.main()
