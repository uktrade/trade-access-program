from web.core import utils
from web.tests.helpers.testcases import BaseTestCase


class TestUtils(BaseTestCase):

    def test_str_to_bool_exception(self):
        self.assertRaises(ValueError, utils.str_to_bool, 'not-a-bool-str')

    def test_str_to_bool_converts_to_true(self):
        self.assertTrue(utils.str_to_bool('true'))

    def test_str_to_bool_converts_to_false(self):
        self.assertFalse(utils.str_to_bool('false'))

    def test_flatten_nested_dict(self):
        test_dict = {
            'outer-key': {
                'inner-key': 'expected-value'
            }
        }
        value = utils.flatten_nested_dict(test_dict, key_path=['outer-key', 'inner-key'])
        self.assertEqual(value, 'expected-value')
