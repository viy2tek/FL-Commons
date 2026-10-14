from fl_commons.errors import OperationError
import http.client
import json
import threading
import time
import unittest

from test_adapter import KEY, Host
import test_http
from test_rpc import Wire


class LimitsTests(unittest.TestCase):
    def test_large_signed_timestamp_is_safely_ignored(self):
        from flcommons_wire.adapter import Adapter
        from flcommons_wire.protocol import encode
        request = dict(kind='request', protocol=1, client='fixture', id='1', seq=1,
                       boot=None, method='bridge.hello', params={}, sent_at=10**350)
        self.assertIsNone(Adapter(Host(), KEY).handle(encode(request, KEY)))

    def test_busy_bridge_rejects_before_sending(self):
        from fl_commons.optional_midi import MidiBackend
        wire = Wire()
        bridge = MidiBackend(wire, KEY, timeout=0.02)
        started, release = threading.Event(), threading.Event()
        def occupy():
            with bridge.lock:
                started.set()
                release.wait(2)
        worker = threading.Thread(target=occupy)
        worker.start()
        started.wait(1)
        try:
            with self.assertRaises(OperationError) as caught:
                bridge.command('transport.start', {})
            self.assertEqual(caught.exception.code, 'busy')
            self.assertEqual(wire.sent, 0)
        finally:
            release.set()
            worker.join()

    def test_duplicate_json_keys_rejected(self):
        from flcommons_wire.protocol import strict_json, ProtocolError
        with self.assertRaises(ProtocolError):
            strict_json('{"method":"one","method":"two"}')


class HTTPBoundaryTests(unittest.TestCase):
    setUp = test_http.HTTPTests.setUp
    tearDown = test_http.HTTPTests.tearDown

    def test_huge_content_length_returns_error(self):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=2)
        connection.request('POST', '/v1/commands', body=b'', headers={
            'Authorization': 'Bearer ' + KEY, 'Content-Length': '9' * 5000,
            'Content-Type': 'application/json'})
        try:
            response = connection.getresponse()
            self.assertEqual(response.status, 413)
            self.assertEqual(json.loads(response.read())['error']['code'], 'too_large')
        finally:
            connection.close()


if __name__ == '__main__':
    unittest.main()
