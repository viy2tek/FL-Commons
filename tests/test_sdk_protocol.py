import unittest
from unittest.mock import patch
from fl_commons.sdk import Client, APIError


class SDKProtocolTests(unittest.TestCase):
    def test_invalid_server_response_is_structured_error(self):
        for payload in (b"[]", b'{"x":NaN}', b'{"result":1,"result":2}', b"not-json"):
            with patch("fl_commons.sdk.http.client.HTTPConnection") as factory:
                factory.return_value.getresponse.return_value.status = 200
                factory.return_value.getresponse.return_value.read.return_value = payload
                with self.assertRaises(APIError) as error:
                    Client("a" * 64).health()
                self.assertEqual(error.exception.code, "protocol_error")

    def test_command_requires_result_envelope(self):
        with patch("fl_commons.sdk.http.client.HTTPConnection") as factory:
            factory.return_value.getresponse.return_value.status = 200
            factory.return_value.getresponse.return_value.read.return_value = b'{"status":"ok"}'
            with self.assertRaises(APIError) as error:
                Client("a" * 64).command("transport.stop")
            self.assertEqual(error.exception.code, "protocol_error")
