from datetime import timedelta
from unittest.mock import patch, create_autospec

from dateutil.utils import today
from django.urls import reverse, resolve

from web.core.notify import NotifyService
from web.grant_applications.models import GrantApplication
from web.grant_management.flows import GrantApplicationFlow
from web.tests.helpers import BaseTestCase


@patch('web.grant_management.flows.NotifyService')
class TestGrantApplicationFlow(BaseTestCase):

    def setUp(self):
        self.ga = GrantApplication.objects.create(duns_number=1)
        self.url = reverse('grant_applications:application-review', kwargs={'pk': self.ga.pk})
        self.tomorrow = today() + timedelta(days=1)

    def test_is_start_of_process(self, *mocks):
        self.assertTrue(GrantApplicationFlow.start.task_type, 'START')

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
