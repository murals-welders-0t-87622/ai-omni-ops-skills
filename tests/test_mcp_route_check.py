import importlib.util
import json
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('mcp_route_check', Path(__file__).resolve().parents[1] / 'scripts/mcp_route_check.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RouteCheckTests(unittest.TestCase):
    def setUp(self):
        self.route = {'data': {'primary': {'functionKey': 'copy', 'mcpTools': ['read', 'create']}}}
        self.catalog = {'tools': [{'name': 'read'}]}

    def test_missing_tool_is_not_execution_success(self):
        result = module.check_route(self.route, self.catalog)
        self.assertEqual(result['available'], ['read'])
        self.assertEqual(result['missing'], ['create'])
        self.assertFalse(result['business_execution_verified'])

    def test_wrapped_mcp_text_and_catalog(self):
        route = {'result': {'content': [{'type': 'text', 'text': json.dumps(self.route)}]}}
        result = module.check_route(route, {'result': self.catalog})
        self.assertEqual(result['missing'], ['create'])

    def test_partial_catalog_cannot_prove_absence(self):
        with self.assertRaises(ValueError):
            module.check_route(self.route, {**self.catalog, 'nextCursor': 'next'})

    def test_missing_recommendations_are_not_success(self):
        with self.assertRaises(ValueError):
            module.check_route({'data': {'primary': {}}}, self.catalog)

    def test_rpc_failure_is_not_success(self):
        with self.assertRaises(ValueError):
            module.check_route({'error': {'code': -1}}, self.catalog)

    def test_all_recommendations_hidden_is_not_mistaken_for_empty_route(self):
        route = {'data': {'primary': {'functionKey': 'copy', 'mcpTools': [], 'unavailableMcpTools': ['create']}}}
        result = module.check_route(route, self.catalog)
        self.assertEqual(result['missing'], ['create'])
        self.assertFalse(result['business_execution_verified'])

    def test_catalog_is_rechecked_when_connection_changes(self):
        route = {'data': {'primary': {'functionKey': 'copy', 'mcpTools': ['read'], 'unavailableMcpTools': ['create']}}}
        result = module.check_route(route, {'tools': [{'name': 'read'}, {'name': 'create'}]})
        self.assertEqual(result['available'], ['read', 'create'])
        self.assertEqual(result['missing'], [])
        self.assertFalse(result['business_execution_verified'])

    def test_visible_tools_do_not_establish_route_correctness(self):
        catalog = {'tools': [{'name': 'read'}, {'name': 'create'}]}
        self.assertIsNone(module.check_route(self.route, catalog)['expected_route_match'])
        result = module.check_route(self.route, catalog, ['image_design'])
        self.assertEqual(result['missing'], [])
        self.assertFalse(result['expected_route_match'])
        self.assertFalse(result['business_execution_verified'])

    def test_multiple_verified_expected_routes_and_invalid_expectation(self):
        self.assertTrue(module.check_route(self.route, self.catalog, ['image_design', 'copy'])['expected_route_match'])
        for expected in ([], [''], 'copy'):
            with self.subTest(expected=expected), self.assertRaises(ValueError):
                module.check_route(self.route, self.catalog, expected)

    def test_missing_function_key_cannot_pass_comparison(self):
        with self.assertRaises(ValueError):
            module.check_route({'data': {'primary': {'mcpTools': ['read']}}}, self.catalog, ['copy'])
