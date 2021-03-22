import logging
from unittest.mock import create_autospec

from django.test import override_settings
from notifications_python_client import NotificationsAPIClient
from requests import HTTPError

from testfixtures import LogCapture

from web.core.notify import NotifyService
from web.tests.helpers import BaseTestCase


class TestNotifyMixin:
    TEMPLATES = [
        {'id': 1, 'name': 'application-submitted'},
        {'id': 2, 'name': 'application-approved'},
        {'id': 3, 'name': 'application-rejected'},
        {'id': 4, 'name': 'application-resume'},
        {'id': 5, 'name': 'event-booking-document-approved'},
        {'id': 6, 'name': 'event-booking-document-rejected'},
        {'id': 7, 'name': 'event-booking-evidence'},
        {'id': 8, 'name': 'event-evidence-upload-confirmation'}
    ]

    def setUp(self):
        super().setUp()
        self.notifications_api_client = create_autospec(NotificationsAPIClient)
        self.notifications_api_client.get_all_templates.return_value = {
            'templates': self.TEMPLATES
        }
        self.notify_client = NotifyService(
            api_client=self.notifications_api_client
        )


class TestNotifyEmail(TestNotifyMixin, BaseTestCase):

    @override_settings(NOTIFY_ENABLED=False)
    def test_does_not_send_email_when_notify_enabled_false(self):
        self.notify_client.send_email(
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
        self.notify_client.send_email(
            email_address='test@test.com',
            template_name='test-template',
            personalisation={}
        )
        log_capture.uninstall()
        self.assertEqual(len(log_capture.records), 1)
        self.assertEqual(log_capture.records[0].levelno, logging.ERROR)
        self.assertTrue(self.notifications_api_client.send_email_notification.called)
        self.assertFalse(self.notifications_api_client.post_template_preview.called)


class TestNotifyApplicationSubmitted(TestNotifyMixin, BaseTestCase):

    @override_settings(NOTIFY_ENABLED=True)
    def test_successful_application_sends_email(self):
        self.notify_client.send_application_submitted_email(
            email_address='test@test.com',
            applicant_full_name='test',
            application_id='A'
        )
        self.assertTrue(self.notifications_api_client.send_email_notification.called)
        self.notifications_api_client.send_email_notification.assert_called_once_with(
            email_address='test@test.com',
            template_id=1,
            personalisation={
                'applicant_full_name': 'test',
                'application_id': 'A'
            }
        )


class TestNotifyApplicationApproved(TestNotifyMixin, BaseTestCase):

    @override_settings(NOTIFY_ENABLED=True)
    def test_application_approved_sends_email(self):
        self.notify_client.send_application_approved_email(
            email_address='test@test.com',
            applicant_full_name='test',
            application_id='A'
        )
        self.assertTrue(self.notifications_api_client.send_email_notification.called)
        self.notifications_api_client.send_email_notification.assert_called_once_with(
            email_address='test@test.com',
            template_id=2,
            personalisation={
                'applicant_full_name': 'test',
                'application_id': 'A'
            }
        )


class TestNotifyApplicationRejected(TestNotifyMixin, BaseTestCase):

    @override_settings(NOTIFY_ENABLED=True)
    def test_application_rejected_sends_email(self):
        self.notify_client.send_application_rejected_email(
            email_address='test@test.com',
            applicant_full_name='test',
            application_id='A'
        )
        self.assertTrue(self.notifications_api_client.send_email_notification.called)
        self.notifications_api_client.send_email_notification.assert_called_once_with(
            email_address='test@test.com',
            template_id=3,
            personalisation={
                'applicant_full_name': 'test',
                'application_id': 'A'
            }
        )


class TestNotifyApplicationResume(TestNotifyMixin, BaseTestCase):

    @override_settings(NOTIFY_ENABLED=True)
    def test_application_resume_sends_email(self):
        self.notify_client.send_application_resume_email(
            email_address='test@test.com',
            magic_link='http://magic-link.com/hash'
        )
        self.assertTrue(self.notifications_api_client.send_email_notification.called)
        self.notifications_api_client.send_email_notification.assert_called_once_with(
            email_address='test@test.com',
            template_id=4,
            personalisation={
                'magic_link': 'http://magic-link.com/hash'
            }
        )
