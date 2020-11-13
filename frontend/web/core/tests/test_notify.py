import logging
from unittest.mock import create_autospec

from django.test import override_settings
from notifications_python_client import NotificationsAPIClient
from requests import HTTPError

from testfixtures import LogCapture

from web.core.notify import NotifyService
from web.tests.helpers.testcases import BaseTestCase


class FakeNotifyServiceMixin:
    TEMPLATES = [
        {'id': 1, 'name': 'application-submitted'},
        {'id': 2, 'name': 'application-approved'},
        {'id': 3, 'name': 'application-rejected'},
        {'id': 4, 'name': 'magic-link'}
    ]

    def setUp(self):
        super().setUp()
        self.notifications_api_client = create_autospec(NotificationsAPIClient)
        self.notifications_api_client.get_all_templates.return_value = {
            'templates': self.TEMPLATES
        }
        self.notify_service = NotifyService(
            api_client=self.notifications_api_client
        )


class TestNotifyEmail(FakeNotifyServiceMixin, BaseTestCase):

    @override_settings(NOTIFY_ENABLED=False)
    def test_does_not_send_email_when_notify_enabled_false(self):
        self.notify_service.send_email(
            email_address='test@test.com',
            template_name='test-template',
            personalisation={}
        )
        self.assertFalse(self.notifications_api_client.send_email_notification.called)
        self.assertTrue(self.notifications_api_client.post_template_preview.called)

    @override_settings(NOTIFY_ENABLED=True)
    def test_log_and_continue_on_notify_exception(self):
        log_capture = LogCapture(level=logging.ERROR)
        self.notifications_api_client.send_email_notification.side_effect = [HTTPError]
        self.notify_service.send_email(
            email_address='test@test.com',
            template_name='test-template',
            personalisation={}
        )
        log_capture.uninstall()
        self.assertEqual(len(log_capture.records), 1)
        self.assertEqual(log_capture.records[0].levelno, logging.ERROR)
        self.assertTrue(self.notifications_api_client.send_email_notification.called)
        self.assertFalse(self.notifications_api_client.post_template_preview.called)
