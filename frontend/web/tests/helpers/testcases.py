import logging

from django.test import TestCase
from testfixtures import LogCapture

from web.core.forms import FORM_MSGS


class BaseTestCase(TestCase):
    form_msgs = FORM_MSGS

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
