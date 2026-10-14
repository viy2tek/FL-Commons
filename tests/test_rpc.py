import queue
import unittest
from fl_commons.errors import OperationError

from test_adapter import Host, KEY


class Wire:
    def __init__(self, key=KEY):
        from flcommons_wire.adapter import Adapter
        self.adapter = Adapter(Host(), key)
        self.queue = queue.Queue()
        self.drop = 0
        self.sent = 0
    def send(self, frame):
        self.sent += 1
        result = self.adapter.handle(frame)
        if self.drop:
            self.drop -= 1
        elif result:
            self.queue.put(result)
    def receive(self, timeout):
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None
    def close(self):
        pass


class RPCTests(unittest.TestCase):
    def setUp(self):
        from fl_commons.optional_midi import MidiBackend
        self.wire = Wire()
        self.bridge = MidiBackend(self.wire, KEY, timeout=0.02, read_attempts=2)

    def test_handshake_and_read_retry(self):
        self.wire.drop = 1
        info = self.bridge.capabilities()
        self.assertEqual(info['mode'], 'simulated')
        self.assertEqual(self.wire.sent, 2)
        self.assertIn('transport.start', info['capabilities'])

    def test_write_timeout_is_unknown_and_never_retried(self):
        from fl_commons.errors import OperationError
        self.bridge.capabilities()
        self.wire.drop = 1
        with self.assertRaises(OperationError) as caught:
            self.bridge.command('transport.start', {})
        self.assertEqual(caught.exception.code, 'outcome_unknown')
        self.assertEqual(self.wire.adapter.host.starts, 1)
        self.assertEqual(self.wire.sent, 2)

    def test_restart_invalidates_mutation_then_reconnects(self):
        from fl_commons.errors import OperationError
        from flcommons_wire.adapter import Adapter
        self.bridge.capabilities()
        self.wire.adapter = Adapter(Host(), KEY)
        with self.assertRaises(OperationError) as caught:
            self.bridge.command('transport.start', {})
        self.assertEqual(caught.exception.code, 'session_changed')
        self.assertEqual(self.wire.adapter.host.starts, 0)
        self.bridge.capabilities()
        self.bridge.command('transport.start', {})
        self.assertTrue(self.bridge.command('transport.state', {})['playing'])

    def test_missing_peer_times_out(self):
        from fl_commons.optional_midi import MidiBackend
        wrong_peer = MidiBackend(Wire('b' * 64), KEY, timeout=0.01, read_attempts=2)
        with self.assertRaises(OperationError) as caught:
            wrong_peer.capabilities()
        self.assertEqual(caught.exception.code, 'unavailable')

    def test_bad_and_uncorrelated_frames_do_not_replace_reply(self):
        from flcommons_wire.protocol import encode
        self.wire.queue.put(b'bad')
        self.wire.queue.put(encode({'kind': 'response', 'id': 'other'}, KEY))
        self.assertEqual(self.bridge.capabilities()['protocol'], 1)


if __name__ == '__main__':
    unittest.main()
