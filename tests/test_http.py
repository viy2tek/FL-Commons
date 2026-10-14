import http.client
import json
import threading
import unittest

from test_adapter import KEY


class HTTPTests(unittest.TestCase):
    def setUp(self):
        from fl_commons.api import API
        from fl_commons.server import create_server
        self.server = create_server(API(demo=True), KEY, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.server.api.close()
        self.thread.join()

    def request(self, method='GET', path='/v1/health', data=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=2)
        body = json.dumps(data).encode() if data is not None else None
        base = {'Authorization': 'Bearer ' + KEY}
        if body is not None:
            base['Content-Type'] = 'application/json'
        base.update(headers or {})
        connection.request(method, path, body=body, headers=base)
        response = connection.getresponse()
        result = response.status, json.loads(response.read())
        connection.close()
        return result

    def test_auth_host_and_browser_origin_rejection(self):
        for headers, expected in [({'Authorization': 'Bearer wrong'}, 401),
                                  ({'Host': 'evil.example'}, 403),
                                  ({'Origin': 'http://evil.example'}, 403)]:
            status, _ = self.request(headers=headers)
            self.assertEqual(status, expected)

    def test_sdk_roundtrip_and_capabilities(self):
        from fl_commons.sdk import Client
        client = Client(KEY, port=self.port)
        self.assertEqual(client.health()['version'], '0.1.0')
        self.assertEqual(client.capabilities()['mode'], 'simulated')
        client.command('transport.start')
        self.assertTrue(client.command('transport.state')['playing'])
        client.command('transport.stop')
        self.assertFalse(client.command('transport.state')['playing'])

    def test_sdk_catalog_over_http_is_paginated_and_reports_limits(self):
        from fl_commons.sdk import Client
        client = Client(KEY, port=self.port)
        page = client.sdk_catalog(domain='transport', limit=2)
        self.assertLessEqual(len(page['entries']), 2)
        self.assertFalse(page['fl_runtime_tested'])
        self.assertEqual(page['target_build'], '26.1.7.5653')
        self.assertIn('source', page)

    def test_invalid_json_contract_and_unsupported_capability(self):
        for body, expected in [([], 400), ({'method': 'private.eval', 'params': {}}, 422),
                               ({'method': 'transport.start', 'params': {'x': 1}}, 400),
                               ({'method': 'transport.start', 'params': {}, 'extra': 1}, 400)]:
            status, _ = self.request('POST', '/v1/commands', body)
            self.assertEqual(status, expected)
        status, _ = self.request('POST', '/v1/commands', {}, {'Content-Type': 'text/plain'})
        self.assertEqual(status, 415)
        status, _ = self.request('POST', '/v1/commands', {'x': 'a' * 9000})
        self.assertEqual(status, 413)

    def test_sdk_raises_structured_error(self):
        from fl_commons.sdk import Client, APIError
        with self.assertRaises(APIError) as caught:
            Client('b' * 64, port=self.port).health()
        self.assertEqual(caught.exception.status, 401)
        self.assertEqual(caught.exception.code, 'unauthorized')

    def test_server_refuses_short_secret(self):
        from fl_commons.server import create_server
        with self.assertRaises(ValueError):
            create_server(self.server.api, 'short')


if __name__ == '__main__':
    unittest.main()
