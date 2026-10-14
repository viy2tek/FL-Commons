import unittest
from unittest.mock import patch
from fl_commons.sdk import Client, APIError


class AdaptiveSdkTests(unittest.TestCase):
    def test_direct_native_sdk_does_not_bypass_capability_policy(self):
        client = Client('a' * 64, port=3211)
        status = {'connected': True, 'fl_version': '26.1.7.5653', 'runtime_contract': 'fpsdk-20210311b-v1',
                  'host_version_raw': 26001007, 'gui_responsive': True, 'state_callback_observed': True}
        with patch.object(client, 'status', return_value=status), \
             patch.object(client, 'capabilities', return_value={'capabilities': ['transport.state']}), \
             patch.object(client, '_request', return_value={'result': None}) as dispatch:
            with self.assertRaises(APIError) as caught:
                client.transport.stop()
            self.assertEqual(caught.exception.code, 'capability_unavailable')
            dispatch.assert_not_called()

    def test_direct_uncertain_write_is_sent_once(self):
        client = Client('a' * 64, port=3211)
        status = {'connected': True, 'fl_version': '26.1.7.5653', 'runtime_contract': 'fpsdk-20210311b-v1',
                  'host_version_raw': 26001007, 'gui_responsive': True, 'state_callback_observed': True}
        with patch.object(client, 'status', return_value=status), \
             patch.object(client, 'capabilities', return_value={'capabilities': ['transport.stop']}), \
             patch.object(client, '_request', side_effect=APIError(0, 'outcome_unknown', 'uncertain')) as dispatch:
            with self.assertRaises(APIError):
                client.transport.stop()
            self.assertEqual(dispatch.call_count, 1)
