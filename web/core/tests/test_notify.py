import logging
from unittest.mock import create_autospec

from django.test import override_settings
from notifications_python_client import NotificationsAPIClient
from requests import HTTPError

from testfixtures import LogCapture

from web.core.notify import NotifyService
from web.tests.helpers import BaseTestCase


class TestNotifyApplicationSubmittedEmail(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.notifications_api_client = create_autospec(NotificationsAPIClient)
        self.notify_client = NotifyService(
            api_client=self.notifications_api_client
        )

    @override_settings(NOTIFY_ENABLED=True)
    def test_successful_application_sends_email(self):
        self.notify_client.send_application_submitted_email(
            email_address='test@test.com', applicant_full_name='test'
        )
        self.assertTrue(self.notifications_api_client.send_email_notification.called)

    @override_settings(NOTIFY_ENABLED=False)
    def test_successful_application_does_not_send_email(self):
        self.notify_client.send_application_submitted_email(
            email_address='test@test.com', applicant_full_name='test'
        )
        self.assertFalse(self.notifications_api_client.send_email_notification.called)
        self.assertTrue(self.notifications_api_client.post_template_preview.called)

    @override_settings(NOTIFY_ENABLED=True)
    def test_log_and_continue_on_notify_exception(self):
        log_capture = LogCapture(level=logging.ERROR)
        self.notifications_api_client.send_email_notification.side_effect = [HTTPError]
        self.notify_client.send_application_submitted_email(
            email_address='test@test.com', applicant_full_name='test'
        )
        log_capture.uninstall()
        self.assertEqual(len(log_capture.records), 1)
        self.assertEqual(log_capture.records[0].levelno, logging.ERROR)
        self.assertTrue(self.notifications_api_client.send_email_notification.called)
        self.assertFalse(self.notifications_api_client.post_template_preview.called)
