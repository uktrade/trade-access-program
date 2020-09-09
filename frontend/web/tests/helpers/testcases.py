from django.test import TestCase


class BaseTestCase(TestCase):

    def set_session_value(self, key, value):
        s = self.client.session
        s[key] = value
        s.save()
