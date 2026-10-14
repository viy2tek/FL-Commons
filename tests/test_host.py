import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch


class HostTests(unittest.TestCase):
    def test_only_latest_version_and_its_processes_are_selected(self):
        from fl_commons.host import inspect_host
        data = {'installations': [
                    {'path': 'C:\\old\\FL64.exe', 'version': '26.1.9.9999'},
                    {'path': 'C:\\new\\FL64.exe', 'version': '26.1.10.5653'},
                    {'path': 'C:\\new\\FL64 (scaled).exe', 'version': '26.1.10.5653'}],
                'processes': [
                    {'pid': 1, 'path': 'C:\\old\\FL64.exe', 'name': 'FL64', 'identity_verified': True},
                    {'pid': 2, 'path': 'C:\\new\\FL64.exe', 'name': 'FL64', 'identity_verified': True},
                    {'pid': 3, 'path': None, 'name': 'FL64', 'identity_verified': False}]}
        with patch('fl_commons.host.sys.platform', 'win32'), patch(
                'fl_commons.host.subprocess.run', return_value=SimpleNamespace(returncode=0, stdout=json.dumps(data), stderr='')):
            result = inspect_host()
        self.assertEqual([item['version'] for item in result['installations']], ['26.1.10.5653'] * 2)
        self.assertEqual([item['pid'] for item in result['processes']], [2])
        self.assertEqual(result['selected_version'], '26.1.10.5653')

    def test_unknown_version_never_causes_silent_older_selection(self):
        from fl_commons.host import inspect_host
        from fl_commons.errors import OperationError
        data = {'installations': [{'path': 'C:\\FL\\FL64.exe', 'version': None}], 'processes': []}
        with patch('fl_commons.host.sys.platform', 'win32'), patch(
                'fl_commons.host.subprocess.run', return_value=SimpleNamespace(returncode=0, stdout=json.dumps(data), stderr='')):
            with self.assertRaises(OperationError):
                inspect_host()

    def test_sdk_inspection_over_authenticated_http(self):
        import threading
        from fl_commons.api import API
        from fl_commons.sdk import Client
        from fl_commons.server import create_server
        inventory = {'platform': 'windows', 'installations': [], 'processes': [],
                     'coverage': 'standard-install-locations-and-named-processes',
                     'control_connected': False}
        server = create_server(API(), 'a' * 64, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with patch('fl_commons.host.inspect_host', return_value=inventory):
                client = Client('a' * 64, port=server.server_address[1])
                self.assertEqual(client.inspect_host(), inventory)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_real_api_exposes_inspection_without_transport_success(self):
        from fl_commons.api import API
        from fl_commons.errors import OperationError
        result = {'platform': 'windows', 'installations': [], 'processes': [],
                  'coverage': 'standard-install-locations-and-named-processes',
                  'control_connected': False}
        with patch('fl_commons.api.sys.platform', 'win32'), patch('fl_commons.host.inspect_host', return_value=result):
            api = API()
            self.assertEqual(api.command('host.inspect', {}), result)
            self.assertIn('host.inspect', api.capabilities()['capabilities'])
            with self.assertRaises(OperationError) as caught:
                api.command('transport.start', {})
            self.assertEqual(caught.exception.code, 'backend_unavailable')

    def test_windows_query_parses_real_output_contract(self):
        from fl_commons.host import inspect_host
        data = {'installations': [{'path': 'C:\\FL\\FL64.exe', 'version': '26.1.7.5653'}],
                'processes': [{'pid': 123, 'path': 'C:\\FL\\FL64.exe', 'name': 'FL64',
                               'identity_verified': True}]}
        with patch('fl_commons.host.sys.platform', 'win32'), patch(
                'fl_commons.host.subprocess.run', return_value=SimpleNamespace(returncode=0, stdout=json.dumps(data), stderr='')):
            result = inspect_host()
        self.assertEqual(result['installations'][0]['version'], '26.1.7.5653')
        self.assertTrue(result['processes'][0]['identity_verified'])
        self.assertFalse(result['control_connected'])

    def test_query_failures_are_not_reported_as_no_fl(self):
        import subprocess
        from fl_commons.host import inspect_host
        from fl_commons.errors import OperationError
        for output in ('bad-json', '{}', '{"installations":{},"processes":[]}'):
            with self.subTest(output=output), patch('fl_commons.host.sys.platform', 'win32'), patch(
                    'fl_commons.host.subprocess.run', return_value=SimpleNamespace(returncode=0, stdout=output, stderr='')):
                with self.assertRaises(OperationError):
                    inspect_host()
        with patch('fl_commons.host.sys.platform', 'win32'), patch(
                'fl_commons.host.subprocess.run', side_effect=subprocess.TimeoutExpired('powershell', 5)):
            with self.assertRaises(OperationError) as caught:
                inspect_host()
        self.assertEqual(caught.exception.code, 'host_inspection_failed')

    def test_other_platform_is_explicitly_unsupported(self):
        from fl_commons.host import inspect_host
        from fl_commons.errors import OperationError
        with patch('fl_commons.host.sys.platform', 'linux'):
            with self.assertRaises(OperationError) as caught:
                inspect_host()
        self.assertEqual(caught.exception.code, 'unsupported_platform')
