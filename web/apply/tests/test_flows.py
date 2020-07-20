from datetime import timedelta
from unittest.mock import patch
from urllib.parse import urlencode

from dateutil.utils import today
from django.urls import reverse, resolve
from rest_framework.status import HTTP_302_FOUND, HTTP_200_OK

from web.apply.flows import ApplyFlow
from web.apply.models import ApplicationProcess
from web.apply.views import ConfirmationView, DnbServiceClient
from web.core.exceptions import DnbServiceClientException
from web.tests.factories.users import UserFactory
from web.tests.helpers import BaseTestCase


@patch.object(DnbServiceClient, 'get_company', return_value={'primary_name': 'company-1'})
@patch.object(
    DnbServiceClient, 'search_companies',
    return_value=[{'primary_name': 'company-1', 'duns_number': 1}]
)
class TestApplyFlowSubmit(BaseTestCase):

    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)

        self.flow_submit_url = reverse('viewflow:apply:apply:submit') + '?duns_number=1'
        self.tomorrow = today() + timedelta(days=1)
        self.flow_submit_post_data = {
            '_continue': '',
            '_viewflow_activation-started': '2020-07-13 08:56:19.898105',
            'applicant_full_name': 'A Name',
            'event_date_day': self.tomorrow.day,
            'event_date_month': self.tomorrow.month,
            'event_date_year': self.tomorrow.year,
            'event_name': 'An Event',
            'requested_amount': '500'
        }

    def test_submit_page_get(self, *mocks):
        response = self.client.get(self.flow_submit_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTemplateUsed(response, 'apply/apply/submit.html')
        self.assertIn('_viewflow_activation-started', response.content.decode())

    def test_submit_page_get_dnb_service_exception(self, *mocks):
        mocks[1].side_effect = [DnbServiceClientException]
        response = self.client.get(self.flow_submit_url)
        self.assertIn('Could not retrieve company name.', response.content.decode())

    def test_submit_is_start_of_process(self, *mocks):
        self.assertTrue(hasattr(ApplyFlow.submit, 'start_view_class'))

    def test_submit_page_post_event_date_in_future(self, *mocks):
        yesterday = today() - timedelta(days=1)
        self.flow_submit_post_data['event_date_day'] = yesterday.day
        response = self.client.post(
            self.flow_submit_url,
            data=urlencode(self.flow_submit_post_data),
            content_type='application/x-www-form-urlencoded'
        )
        self.assertIn('Event date must be in the future.', response.content.decode())

    def test_submit_page_post_data_is_saved(self, *mocks):
        response = self.client.post(
            self.flow_submit_url,
            data=urlencode(self.flow_submit_post_data),
            content_type='application/x-www-form-urlencoded'
        )

        self.assertEqual(response.status_code, HTTP_302_FOUND)
        redirect_kwargs = resolve(response.url).kwargs
        apply_process = ApplicationProcess.objects.get(pk=redirect_kwargs['process_pk'])

        self.assertEqual(apply_process.applicant_full_name, 'A Name')
        self.assertEqual(apply_process.event_date, self.tomorrow.date())
        self.assertEqual(apply_process.event_name, 'An Event')
        self.assertEqual(apply_process.requested_amount, 500)

    def test_submit_page_post_redirects(self, *mocks):
        response = self.client.post(
            self.flow_submit_url,
            data=urlencode(self.flow_submit_post_data),
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, HTTP_302_FOUND)

    def test_submit_page_post_redirects_to_confirmation_page(self, *mocks):
        response = self.client.post(
            self.flow_submit_url,
            data=urlencode(self.flow_submit_post_data),
            content_type='application/x-www-form-urlencoded',
            follow=True
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTemplateUsed(response, ConfirmationView.template_name)
        self.assertRedirects(
            response=response,
            expected_url=reverse(
                'apply:confirmation', args=(ApplicationProcess.objects.first().pk,)
            )
        )
