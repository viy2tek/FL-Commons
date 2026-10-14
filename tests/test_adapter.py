import time
import unittest

KEY = 'a' * 64


class Host:
    """Test boundary for the unavailable embedded FL runtime."""
    def __init__(self):
        self.playing = False
        self.starts = 0
    def information(self):
        return {'fl_version': None, 'midi_api_version': 1, 'mode': 'simulated'}
    def capabilities(self):
        return ['transport.state', 'transport.start', 'transport.stop']
    def execute(self, method, params):
        if method == 'transport.start':
            self.starts += 1
            self.playing = True
            return None
        if method == 'transport.stop':
            self.playing = False
            return None
        return {'playing': self.playing, 'recording': False, 'position': 0.0}


class AdapterTests(unittest.TestCase):
    def setUp(self):
        from flcommons_wire.adapter import Adapter
        self.host = Host()
        self.adapter = Adapter(self.host, KEY)
        self.seq = 0
        self.boot = None

    def request(self, method, **changes):
        from flcommons_wire.protocol import encode, decode
        self.seq += 1
        body = dict(kind='request', protocol=1, client='test', id=str(self.seq),
                    seq=self.seq, boot=self.boot, method=method, params={},
                    sent_at=time.time())
        body.update(changes)
        frame = encode(body, KEY)
        reply = decode(self.adapter.handle(frame), KEY)
        return reply, frame

    def hello(self):
        reply, _ = self.request('bridge.hello')
        self.boot = reply['result']['boot']
        return reply

    def test_duplicate_write_executes_once(self):
        from flcommons_wire.protocol import decode
        self.hello()
        reply, frame = self.request('transport.start')
        self.assertTrue(reply['ok'])
        self.assertEqual(decode(self.adapter.handle(frame), KEY), reply)
        self.assertEqual(self.host.starts, 1)

    def test_boot_mismatch_expiry_unknown_and_invalid_params(self):
        self.hello()
        for method, changes, expected in [
            ('transport.start', {'boot': 'old'}, 'session_changed'),
            ('transport.start', {'sent_at': time.time() - 60}, 'expired'),
            ('private.eval', {}, 'unsupported'),
            ('transport.start', {'params': {'value': 1}}, 'invalid_params')]:
            reply, _ = self.request(method, **changes)
            self.assertEqual(reply['error']['code'], expected)
        self.assertEqual(self.host.starts, 0)

    def test_replay_after_cache_eviction_is_rejected(self):
        from flcommons_wire.protocol import decode
        self.hello()
        _, frame = self.request('transport.start')
        for _ in range(130):
            self.request('transport.state')
        reply = decode(self.adapter.handle(frame), KEY)
        self.assertEqual(reply['error']['code'], 'replay')
        self.assertEqual(self.host.starts, 1)

    def test_untrusted_frame_is_silent(self):
        from flcommons_wire.protocol import encode
        self.assertIsNone(self.adapter.handle(encode({'kind': 'request'}, 'b' * 64)))

    def test_capabilities_are_allowlisted(self):
        self.host.capabilities = lambda: ['transport.state']
        reply = self.hello()
        self.assertEqual(reply['result']['capabilities'], ['transport.state'])
        reply, _ = self.request('transport.start')
        self.assertEqual(reply['error']['code'], 'unsupported')

    def test_official_host_detects_only_callable_documented_methods(self):
        from types import SimpleNamespace
        from flcommons_wire.adapter import OfficialHost
        host = OfficialHost(SimpleNamespace(getVersion=lambda: 7),
                            SimpleNamespace(getVersion=lambda: 'test build'),
                            SimpleNamespace(start=lambda: None, stop=None))
        self.assertEqual(host.capabilities(), ['transport.start'])
        self.assertEqual(host.information()['midi_api_version'], 7)


if __name__ == '__main__':
    unittest.main()
