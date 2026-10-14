import json
import unittest


class CatalogTests(unittest.TestCase):
    def test_catalog_reports_evidence_without_enabling_native_calls(self):
        from fl_commons.api import API
        from fl_commons.errors import OperationError
        api = API()
        catalog = api.command('sdk.catalog', {'domain': 'transport'})
        transport = next(item for item in catalog['entries'] if item['symbol'] == 'FHD_Transport')
        self.assertEqual(transport['id'], 79)
        self.assertEqual(transport['state'], 'contract_tested')
        self.assertFalse(transport['callable_via_api'])
        self.assertFalse(catalog['fl_runtime_tested'])
        self.assertEqual(catalog['target_build'], '26.1.7.5653')
        with self.assertRaises(OperationError):
            api.command('FHD_Transport', {})

    def test_pagination_is_complete_and_bounded(self):
        from fl_commons.catalog import sdk_catalog
        symbols = []
        offset = 0
        while True:
            page = sdk_catalog(offset=offset, limit=7)
            self.assertLessEqual(len(page['entries']), 7)
            self.assertLess(len(json.dumps(page).encode()), 16384)
            symbols.extend(entry['symbol'] for entry in page['entries'])
            if page['next_offset'] is None: break
            offset = page['next_offset']
        self.assertEqual(len(symbols), page['total'])
        self.assertEqual(len(symbols), len(set(symbols)))
        self.assertIn('FHD_GetProjectInfo', symbols)
        self.assertIn('FHD_GetContextInfo', symbols)

    def test_bad_catalog_parameters_are_rejected(self):
        from fl_commons.api import API
        from fl_commons.errors import OperationError
        for params in ({'offset': -1}, {'limit': 33}, {'limit': True},
                       {'domain': []}, {'domain': 'everything'}, {'arbitrary_call': 79}):
            with self.subTest(params=params), self.assertRaises(OperationError) as caught:
                API().command('sdk.catalog', params)
            self.assertEqual(caught.exception.code, 'invalid_params')

    def test_catalog_available_without_fl_or_midi(self):
        from fl_commons.api import API
        self.assertIn('sdk.catalog', API().capabilities()['capabilities'])
        self.assertIn('sdk.catalog', API(demo=True).capabilities()['capabilities'])
