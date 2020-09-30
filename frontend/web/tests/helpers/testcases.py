import logging

from django.test import TestCase
from testfixtures import LogCapture


class BaseTestCase(TestCase):

    def set_session_value(self, key, value):
        s = self.client.session
        s[key] = value
        s.save()


class LogCaptureMixin:
    log_capture_level = logging.INFO

    def setUp(self):
        super().setUp()
        self.log_capture = LogCapture(level=self.log_capture_level)

    def tearDown(self):
        super().tearDown()
        self.log_capture.uninstall()
