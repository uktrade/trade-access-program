from rest_framework.test import APITestCase


class AssertResponseMixin:

    def assert_response_data_contains(self, response, data_contains):
        if isinstance(data_contains, dict):
            self.assert_data_contains(response.data, data_contains)
        elif isinstance(data_contains, list):
            self.assertEqual(len(response.data), len(data_contains))
            for i, response_data in enumerate(response.data):
                self.assert_data_contains(response_data, data_contains[i])
        else:
            raise AssertionError('Cannot compare data')

    def assert_data_contains(self, data, data_contains):
        for k, v in data_contains.items():
            self.assertIn(k, data)
            self.assertEqual(data[k], v)


class BaseTestCase(AssertResponseMixin, APITestCase):
    pass
