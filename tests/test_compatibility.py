import copy
import unittest
from fl_commons.compatibility import builtin_profiles, resolve_operation, validate_profile
from fl_commons.errors import OperationError


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.observed = {'fl_build': '26.1.7.5653', 'host_version_raw': 26001007,
                         'runtime_contract': 'fpsdk-20210311b-v1',
                         'gui_responsive': True, 'state_callback_observed': True}

    def test_product_build_change_preserves_matching_contract(self):
        profiles = builtin_profiles()
        self.assertEqual(resolve_operation('transport.stop', self.observed, profiles)['status'], 'limited')
        self.observed['fl_build'] = '26.1.7.9999'
        self.assertEqual(resolve_operation('transport.stop', self.observed, profiles)['status'], 'experimental')

    def test_missing_contract_and_unknown_mapping_disable_operation(self):
        for key in ('host_version_raw', 'runtime_contract'):
            observed = dict(self.observed)
            observed.pop(key)
            self.assertEqual(resolve_operation('transport.stop', observed, builtin_profiles())['status'], 'unsupported')
        for mutate in (lambda p: p.update(adapter_id='eval'),
                       lambda p: p['operations'].update({'shell.run': 'shell.run'}),
                       lambda p: p['operations'].update({'transport.stop': 'unsafe.selector'}),
                       lambda p: p.update(host_api_versions=[2147483648]),
                       lambda p: p.update(host_api_versions=[True])):
            profile = copy.deepcopy(builtin_profiles()[0])
            mutate(profile)
            with self.assertRaises(OperationError):
                validate_profile(profile)

    def test_partial_degradation_and_unknown_state(self):
        self.observed['state_callback_observed'] = False
        self.assertEqual(resolve_operation('transport.state', self.observed, builtin_profiles())['status'], 'temporarily_unavailable')
        self.assertEqual(resolve_operation('transport.stop', self.observed, builtin_profiles())['status'], 'limited')
        self.observed['gui_responsive'] = False
        self.assertEqual(resolve_operation('transport.stop', self.observed, builtin_profiles())['status'], 'temporarily_unavailable')

    def test_fl25_can_match_a_verified_interface_profile_without_fabricated_evidence(self):
        profile = copy.deepcopy(builtin_profiles()[0])
        profile['host_api_versions'] = [25000000]
        self.observed.update(fl_build='25.0.0.1', host_version_raw=25000000)
        self.assertEqual(resolve_operation('transport.stop', self.observed, [profile])['status'], 'experimental')
        self.assertEqual(resolve_operation('transport.stop', self.observed, builtin_profiles())['status'], 'unsupported')

    def test_malformed_and_older_host_versions_are_rejected(self):
        for version in ('25.bad', '24.0.0.1', None, '26.1.7.5653.extra'):
            self.observed['fl_build'] = version
            self.assertEqual(resolve_operation('transport.stop', self.observed, builtin_profiles())['status'], 'unsupported')
