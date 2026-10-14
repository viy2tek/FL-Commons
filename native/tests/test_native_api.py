"""Real sockets against original controlled host; not an FL runtime test."""
import ctypes
import http.client
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import time
import unittest

from fl_commons.sdk import Client, APIError

BINARY = Path(os.environ.get("FL_COMMONS_TEST_HOST", "work/native-api/api_host.exe")).resolve()
TOKEN = secrets.token_hex(32)


def launch(milliseconds=30000, mode="active"):
    process = subprocess.Popen([str(BINARY), TOKEN, str(milliseconds), mode],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    line = process.stdout.readline()
    if not line.strip().isdigit():
        raise AssertionError(process.communicate())
    return process, int(line)


class NativeAPI(unittest.TestCase):
    def test_real_build_is_reported_without_exact_version_gate(self):
        process, port = launch(800, 'build-changed')
        try:
            report = Client(TOKEN, port=port).compatibility()
            self.assertEqual(report['fl_build'], '26.1.7.9999')
            self.assertEqual(report['runtime_contract'], 'fpsdk-20210311b-v1')
        finally:
            process.terminate()
            process.communicate(timeout=3)

    def test_unverified_contract_disables_host_dispatch(self):
        process, port = launch(600, 'unknown-abi')
        try:
            client = Client(TOKEN, port=port)
            self.assertEqual(client.capabilities()['capabilities'], [])
            with self.assertRaises(APIError) as caught:
                client.command('transport.stop')
            self.assertEqual(caught.exception.code, 'capability_unavailable')
            output = process.communicate(timeout=3)[0]
            self.assertIn('calls=0', output)
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate(timeout=3)

    def test_read_only_probe_never_dispatches_transport(self):
        process, port = launch(500, 'build-changed')
        try:
            client = Client(TOKEN, port=port)
            client.health()
            client.compatibility()
            client.capabilities()
            client.command('transport.state')
            self.assertIn('calls=0', process.communicate(timeout=3)[0])
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate(timeout=3)

    @classmethod
    def setUpClass(cls):
        cls.process, cls.port = launch()
        cls.client = Client(TOKEN, port=cls.port)

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.communicate(timeout=5)

    def raw(self, body='{"method":"transport.state","params":{}}', extra="", token=TOKEN, host=None):
        payload = (f"POST /v1/commands HTTP/1.1\r\nHost: {host or f'127.0.0.1:{self.port}'}\r\n"
                   f"Authorization: Bearer {token}\r\nContent-Type: application/json\r\n"
                   f"Content-Length: {len(body.encode())}\r\n{extra}\r\n{body}").encode()
        with socket.create_connection(("127.0.0.1", self.port), 5) as connection:
            connection.sendall(payload)
            response = http.client.HTTPResponse(connection)
            response.begin()
            return response.status, json.loads(response.read())

    def test_health_and_capabilities(self):
        self.assertEqual(self.client.health()["status"], "ok")
        capabilities = self.client.capabilities()
        self.assertEqual(capabilities["mode"], "controlled-host")
        self.assertEqual(capabilities["compatibility"], "unverified")
        self.assertNotIn("transport.start", capabilities["capabilities"])

    def test_authentication(self):
        self.assertEqual(self.raw(token="x" * 64)[0], 401)

    def test_compatibility_reports_evidence_without_certification(self):
        report = self.client.compatibility()
        self.assertEqual(report["profile"], "fpsdk-20210311b-transport-v1")
        self.assertEqual(report["mode"], "controlled-host")
        self.assertIsNone(report["fl_build"])
        self.assertTrue(report["gui_dispatch_observed"])
        self.assertTrue(report["gui_responsive"])
        self.assertFalse(report["fl_runtime_validated"])
        self.assertEqual(len(report["session_id"]), 32)
        methods = {item["method"]: item for item in report["operations"]}
        self.assertEqual(methods["transport.stop"]["validation"], "unverified")
        self.assertTrue(methods["transport.stop"]["experimental"])
        self.assertFalse(methods["transport.stop"]["automatically_probed"])
        self.assertNotIn("mixer.set_volume", methods)

    def test_sessions_change_after_reload(self):
        first = self.client.compatibility()["session_id"]
        process, port = launch(500)
        try:
            second = Client(TOKEN, port=port).compatibility()["session_id"]
            self.assertNotEqual(first, second)
            process.communicate(timeout=3)
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate()

    def test_origin_and_host(self):
        self.assertEqual(self.raw(extra="Origin: http://example.com\r\n")[0], 403)
        self.assertEqual(self.raw(host="example.com")[0], 403)

    def test_compatibility_requires_authentication(self):
        with self.assertRaises(APIError) as error:
            Client("z" * 64, port=self.port).compatibility()
        self.assertEqual(error.exception.status, 401)

    def test_probe_does_not_invent_gui_activity(self):
        process, port = launch(500, "stalled")
        try:
            report = Client(TOKEN, port=port).compatibility()
            self.assertFalse(report["gui_dispatch_observed"])
            self.assertFalse(report["gui_responsive"])
            self.assertFalse(report["state_callback_observed"])
            self.assertFalse(report["fl_runtime_validated"])
            self.assertIsNone(report["last_gui_idle_age_ms"])
            process.communicate(timeout=3)
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate()

    def test_duplicate_and_transfer_headers(self):
        for extra in ("Content-Length: 0\r\n", "Transfer-Encoding: chunked\r\n",
                      "Authorization: Bearer bad\r\n"):
            self.assertEqual(self.raw(extra=extra)[0], 400)

    def test_json_boundary(self):
        for body in ('{"method":"transport.stop","params":{"x":1}}',
                     '{"method":"transport.stop","method":"transport.state","params":{}}',
                     '{"method":"transport.stop","params":{}} trailing',
                     '\v{"method":"transport.stop","params":{}}'):
            self.assertEqual(self.raw(body=body)[0], 400)
        self.assertEqual(self.raw(body='{"params":{},"method":"transport.state"}')[0], 200)
        self.assertEqual(self.raw(body="x" * 1025)[0], 413)

    def test_commands_and_unsupported(self):
        self.assertEqual(self.client.command("transport.play_pause")["host_result"], 8)
        self.assertTrue(self.client.command("transport.state")["playing"])
        self.assertEqual(self.client.command("transport.stop")["disposition"], "handled")
        self.assertFalse(self.client.command("transport.state")["playing"])
        with self.assertRaises(APIError) as error:
            self.client.command("transport.start")
        self.assertEqual(error.exception.code, "unsupported")

    def test_deadline_cancels_before_execution(self):
        process, port = launch(3800, "paused")
        try:
            with self.assertRaises(APIError) as error:
                Client(TOKEN, port=port).command("transport.stop")
            self.assertEqual(error.exception.code, "not_executed")
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, stderr)
            self.assertIn("calls=0", stdout)
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate()

    def test_unload_interrupts_incomplete_request(self):
        process, port = launch(500)
        with socket.create_connection(("127.0.0.1", port), 5) as connection:
            connection.sendall(b"POST /v1/commands HTTP/1.1\r\n")
            started = time.monotonic()
            stdout, stderr = process.communicate(timeout=3)
            self.assertEqual(process.returncode, 0, stderr)
            self.assertLess(time.monotonic() - started, 1.5)

    def test_slow_reader_cannot_hold_gui_queue_lock(self):
        process, port = launch(500, "large")
        connection = socket.socket()
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)
        connection.settimeout(3)
        try:
            connection.connect(("127.0.0.1", port))
            body = '{"method":"transport.stop","params":{}}'
            connection.sendall((f"POST /v1/commands HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
                                f"Authorization: Bearer {TOKEN}\r\nContent-Type: application/json\r\n"
                                f"Content-Length: {len(body)}\r\n\r\n{body}").encode())
            started = time.monotonic()
            stdout, stderr = process.communicate(timeout=3)
            self.assertEqual(process.returncode, 0, stderr)
            self.assertLess(time.monotonic() - started, 1.5)
            self.assertIn("calls=1", stdout)
        finally:
            connection.close()
            if process.poll() is None:
                process.terminate()
                process.communicate()

    def test_started_command_reports_uncertain_outcome(self):
        process, port = launch(3200, "slow")
        try:
            with self.assertRaises(APIError) as error:
                Client(TOKEN, port=port).command("transport.stop")
            self.assertEqual(error.exception.code, "outcome_unknown")
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, stderr)
            self.assertIn("calls=1", stdout)
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate()

    def test_initial_state_is_unknown(self):
        process, port = launch(500)
        try:
            self.assertIsNone(Client(TOKEN, port=port).command("transport.state")["playing"])
            process.communicate(timeout=3)
            self.assertEqual(process.returncode, 0)
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate()

    def test_factory_rejects_non_fl_process(self):
        dll = ctypes.WinDLL(str(BINARY.parent / "FL Commons API.dll"))
        factory = dll.CreatePlugInstance
        factory.argtypes = [ctypes.c_void_p, ctypes.c_ssize_t]
        factory.restype = ctypes.c_void_p
        self.assertIsNone(factory(0, 1))


if __name__ == "__main__":
    unittest.main()
