from datetime import timedelta
from unittest.mock import patch, create_autospec

from dateutil.utils import today
from django.urls import reverse, resolve

from web.core.notify import NotifyService
from web.tests.factories.grant_applications import GrantApplicationFactory
from web.tests.helpers import BaseTestCase


@patch('web.grant_management.flows.NotifyService')
class TestInterfaceGrantManagementFlow(BaseTestCase):

    def setUp(self):
        self.ga = GrantApplicationFactory()
        self.url = reverse('grant_applications:application-review', kwargs={'pk': self.ga.pk})
        self.tomorrow = today() + timedelta(days=1)
        self.set_session_value(key='application_summary', value=self.ga.application_summary)

    def test_starts_grant_applications_flow_process(self, *mocks):
        response = self.client.post(
            self.url, content_type='application/x-www-form-urlencoded'
        )
        self.assertTrue(hasattr(self.ga, 'grant_application_process'))
        redirect = resolve(response.url)
        self.assertEqual(redirect.kwargs['pk'], self.ga.id_str)
        self.assertEqual(redirect.kwargs['process_pk'], str(self.ga.grant_application_process.pk))

    def test_post_sends_email_notification(self, *mocks):
        notify_service = create_autospec(NotifyService)
        mocks[0].return_value = notify_service
        self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
        )
        notify_service.send_application_submitted_email.assert_called()
