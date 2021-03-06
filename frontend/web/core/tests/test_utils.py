from web.core import utils
from web.tests.helpers.testcases import BaseTestCase


class TestUtils(BaseTestCase):

    def test_str_to_bool_exception(self):
        self.assertRaises(ValueError, utils.str_to_bool, 'not-a-bool-str')

    def test_str_to_bool_converts_to_true(self):
        self.assertTrue(utils.str_to_bool('true'))

    def test_str_to_bool_converts_to_false(self):
        self.assertFalse(utils.str_to_bool('false'))

    def test_flatten_value_in_nested_dict(self):
        test_dict = {
            'outer-key': {
                'inner-key': 'inner-value'
            }
        }
        value = utils.flatten_value_in_nested_dict(test_dict, key_path='outer-key.inner-key')
        self.assertEqual(value, 'inner-value')

    def test_flatten_nested_dict(self):
        test_dict = {
            'outer-key-1': {
                'inner-key-1': 'inner-value'
            },
            'outer-key-2': {
                'inner-key-1': {
                    'inner-key-2': 'inner-value'
                }
            }
        }
        flattened_dict = utils.flatten_nested_dict(
            test_dict,
            flatten_map={
                'outer-key-1': 'outer-key-1.inner-key-1',
                'outer-key-2': 'outer-key-2.inner-key-1.inner-key-2'
            }
        )
        self.assertDictEqual(
            flattened_dict,
            {
                'outer-key-1': 'inner-value',
                'outer-key-2': 'inner-value'
            }
        )
