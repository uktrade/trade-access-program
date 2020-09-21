from django.test import TestCase
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
            self.assertIn(k, data, msg=f'Value for key "{k}" does not match')
            if isinstance(v, dict):
                self.assertDictEqual(data[k], v, msg=f'Value for key "{k}" does not match')
            else:
                self.assertEqual(data[k], v, msg=f'Value for key "{k}" does not match')


class BaseAPITestCase(AssertResponseMixin, APITestCase):
    pass


class BaseTestCase(AssertResponseMixin, TestCase):

    def set_session_value(self, key, value):
        s = self.client.session
        s[key] = value
        s.save()
