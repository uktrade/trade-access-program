from datetime import timedelta
from unittest.mock import patch, create_autospec
from urllib.parse import urlencode

from dateutil.utils import today
from django.urls import reverse, resolve

from web.apply.flows import ApplyFlow
from web.apply.views import DnbServiceClient
from web.core.notify import NotifyService
from web.tests.factories.users import UserFactory
from web.tests.helpers import BaseTestCase


@patch('web.apply.flows.NotifyService')
@patch.object(DnbServiceClient, 'get_company', return_value={'primary_name': 'company-1'})
@patch.object(
    DnbServiceClient, 'search_companies',
    return_value=[{'primary_name': 'company-1', 'duns_number': 1}]
)
class TestApplyFlow(BaseTestCase):

    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)

        self.url = reverse('apply:submit-application') + '?duns_number=1'
        self.tomorrow = today() + timedelta(days=1)
        self.flow_submit_post_data = {
            'applicant_full_name': 'A Name',
            'applicant_email': 'test@test.com',
            'event_date_day': self.tomorrow.day,
            'event_date_month': self.tomorrow.month,
            'event_date_year': self.tomorrow.year,
            'event_name': 'An Event',
            'requested_amount': '500'
        }

    def test_submit_page_is_start_of_process(self, *mocks):
        self.assertTrue(ApplyFlow.start.task_type, 'START')

    def test_submit_page_starts_apply_flow_process(self, *mocks):
        response = self.client.post(
            self.url,
            data=urlencode(self.flow_submit_post_data),
            content_type='application/x-www-form-urlencoded'
        )
        redirect_kwargs = resolve(response.url).kwargs
        self.assertTrue(
            ApplyFlow.process_class.objects.filter(pk=redirect_kwargs['process_pk']).exists()
        )

    def test_submit_page_post_sends_email_notification(self, *mocks):
        notify_service = create_autospec(NotifyService)
        mocks[2].return_value = notify_service
        self.client.post(
            self.url,
            data=urlencode(self.flow_submit_post_data),
            content_type='application/x-www-form-urlencoded',
        )
        notify_service.send_application_submitted_email.assert_called()
