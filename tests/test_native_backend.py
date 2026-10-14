import threading
import unittest
from unittest.mock import patch

from fl_commons.api import API
from fl_commons.sdk import Client, APIError
from fl_commons.server import create_server


class NativeFixture:
    def __init__(self):
        self.playing = False
        self.connected = True
        self.calls = []

    def status(self):
        return {"connected": self.connected, "mode": "fl-native",
                "fl_version": "26.1.7.5653", "session_id": "a" * 32,
                "gui_responsive": True, "compatibility": "experimental"}

    def capabilities(self):
        return {"capabilities": ["transport.state", "transport.play_pause", "transport.stop"],
                "compatibility": "unverified"}

    def command(self, method, params):
        self.calls.append((method, params))
        if method == "transport.play_pause":
            self.playing = not self.playing
        elif method == "transport.stop":
            self.playing = False
        if method == "transport.state":
            return {"playing": self.playing, "source": "host_callback"}
        return {"host_result": 8, "disposition": "handled"}


class NativeBackendTests(unittest.TestCase):
    def setUp(self):
        from fl_commons.native_backend import NativeBackend
        self.native = NativeFixture()
        self.api = API(backend=NativeBackend(self.native))
        self.server = create_server(self.api, "a" * 64, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = Client("a" * 64, port=self.server.server_address[1])

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_status_and_transport_use_native_backend(self):
        self.assertTrue(self.client.status()["connected"])
        self.assertEqual(self.client.status()["fl_version"], "26.1.7.5653")
        self.client.transport.play_pause()
        self.assertTrue(self.client.transport.state()["playing"])
        self.client.transport.stop()
        self.assertFalse(self.client.transport.state()["playing"])
        self.assertEqual([method for method, _ in self.native.calls],
                         ["transport.play_pause", "transport.state", "transport.stop", "transport.state"])

    def test_catalog_and_native_commands_share_one_api(self):
        capabilities = self.client.capabilities()
        self.assertIn("transport.play_pause", capabilities["capabilities"])
        self.assertEqual(capabilities["capability_details"]["transport.play_pause"]["status"], "limited")
        self.assertEqual(capabilities["capability_details"]["transport.stop"]["adapter"], "native_sdk")
        self.assertEqual(self.client.sdk_catalog(limit=1)["target_build"], "26.1.7.5653")
        self.assertEqual(self.native.calls, [])

    def test_disconnect_does_not_report_success_or_dispatch(self):
        self.native.connected = False
        self.assertFalse(self.client.status()["connected"])
        self.assertNotIn("transport.stop", self.client.capabilities()["capabilities"])
        self.assertEqual(self.client.capabilities()["capability_details"]["transport.stop"]["status"],
                         "temporarily_unavailable")
        with self.assertRaises(APIError) as caught:
            self.client.transport.stop()
        self.assertEqual(caught.exception.code, "not_connected")
        self.assertEqual(self.native.calls, [])

    def test_unknown_build_and_invalid_params_do_not_dispatch(self):
        with patch.object(self.native, "status", return_value=dict(self.native.status(), fl_version="99.0.0.1")):
            with self.assertRaises(APIError) as caught:
                self.client.transport.stop()
            self.assertEqual(caught.exception.code, "version_unverified")
        with self.assertRaises(APIError):
            self.client.command("transport.stop", {"arbitrary": 1})
        with self.assertRaises(APIError):
            self.client.command("transport.start")
        self.assertEqual(self.native.calls, [])

    def test_uncertain_write_is_never_retried(self):
        with patch.object(self.native, "command", side_effect=APIError(504, "outcome_unknown", "Uncertain")) as dispatch:
            with self.assertRaises(APIError) as caught:
                self.client.transport.stop()
            self.assertEqual(caught.exception.code, "outcome_unknown")
            self.assertEqual(dispatch.call_count, 1)

    def test_public_import_is_available(self):
        from flcommons import FLStudio
        self.assertIs(FLStudio, Client)
