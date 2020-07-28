from datetime import timedelta
from unittest.mock import patch
from urllib.parse import urlencode

from dateutil.utils import today
from django.forms import Field
from django.urls import reverse, resolve
from rest_framework.status import HTTP_200_OK, HTTP_302_FOUND

from web.core.exceptions import DnbServiceClientException
from web.grant_applications.views import (
    SearchCompanyView, SelectCompanyView, DnbServiceClient, ConfirmationView
)
from web.grant_management.models import GrantApplicationProcess
from web.tests.factories.users import UserFactory
from web.tests.helpers import BaseTestCase


@patch.object(DnbServiceClient, 'get_company', return_value={'primary_name': 'company-1'})
@patch.object(
    DnbServiceClient, 'search_companies',
    return_value=[{'primary_name': 'company-1', 'duns_number': 1}]
)
class TestSearchCompanyView(BaseTestCase):

    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse('apply:search-company')

    def test_search_company_get_template(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTemplateUsed(response, SearchCompanyView.template_name)

    def test_search_term_required(self, *mocks):
        response = self.client.post(self.url)
        self.assertFormError(response, 'form', 'search_term', 'This field is required.')

    def test_search_company_post_form_redirect_path(self, *mocks):
        response = self.client.post(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, HTTP_302_FOUND)
        self.assertRedirects(
            response,
            expected_url=reverse('apply:select-company') + '?search_term=company-1'
        )

    def test_search_company_post_form_redirect_template(self, *mocks):
        response = self.client.post(self.url, data={'search_term': 'company-1'}, follow=True)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTemplateUsed(response, SelectCompanyView.template_name)


@patch.object(DnbServiceClient, 'get_company', return_value={'primary_name': 'company-1'})
@patch.object(
    DnbServiceClient, 'search_companies',
    return_value=[{'primary_name': 'company-1-name', 'duns_number': 1}]
)
class TestSelectCompanyView(BaseTestCase):

    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse('apply:select-company')

    def test_select_company_get_template(self, *mocks):
        response = self.client.get(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTemplateUsed(response, SelectCompanyView.template_name)
        self.assertIn('company-1-name', response.content.decode())

    def test_select_company_get_template_on_dnb_service_exception(self, *mocks):
        mocks[0].side_effect = [DnbServiceClientException]
        response = self.client.get(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertNotIn('company-1-name', response.content.decode())

    def test_required_fields(self, *mocks):
        self.set_session_value('search_term', 'company-1')
        response = self.client.post(self.url)
        self.assertFormError(
            response, 'form', 'duns_number', Field.default_error_messages['required']
        )

    def test_select_company_post_form_redirect_path(self, *mocks):
        self.set_session_value('search_term', 'company-1')
        response = self.client.post(self.url, {'duns_number': 1})
        self.assertEqual(response.status_code, HTTP_302_FOUND)
        self.assertRedirects(
            response,
            expected_url=reverse('apply:submit-application') + '?duns_number=1'
        )

    def test_select_company_post_form_redirect_template(self, *mocks):
        self.set_session_value('search_term', 'company-1')
        response = self.client.post(self.url, {'duns_number': 1}, follow=True)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTemplateUsed(response, 'apply/submit_application.html')


@patch('web.grant_management.flows.NotifyService')
@patch.object(DnbServiceClient, 'get_company', return_value={'primary_name': 'company-1'})
@patch.object(
    DnbServiceClient, 'search_companies',
    return_value=[{'primary_name': 'company-1', 'duns_number': 1}]
)
class TestGrantApplicationFlowSubmit(BaseTestCase):

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

    def test_submit_page_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTemplateUsed(response, 'apply/submit_application.html')

    def test_submit_page_get_dnb_service_exception(self, *mocks):
        mocks[1].side_effect = [DnbServiceClientException]
        response = self.client.get(self.url)
        self.assertIn('Could not retrieve company name.', response.content.decode())

    def test_submit_page_post_event_date_in_future(self, *mocks):
        yesterday = today() - timedelta(days=1)
        self.flow_submit_post_data['event_date_day'] = yesterday.day
        response = self.client.post(
            self.url,
            data=urlencode(self.flow_submit_post_data),
            content_type='application/x-www-form-urlencoded'
        )
        self.assertIn('Event date must be in the future.', response.content.decode())

    def test_submit_page_post_data_is_saved(self, *mocks):
        response = self.client.post(
            self.url,
            data=urlencode(self.flow_submit_post_data),
            content_type='application/x-www-form-urlencoded'
        )

        self.assertEqual(response.status_code, HTTP_302_FOUND)
        redirect_kwargs = resolve(response.url).kwargs
        apply_process = GrantApplicationProcess.objects.get(pk=redirect_kwargs['process_pk'])

        self.assertEqual(apply_process.applicant_full_name, 'A Name')
        self.assertEqual(apply_process.applicant_email, 'test@test.com')
        self.assertEqual(apply_process.event_date, self.tomorrow.date())
        self.assertEqual(apply_process.event_name, 'An Event')
        self.assertEqual(apply_process.requested_amount, 500)

    def test_submit_page_post_redirects(self, *mocks):
        response = self.client.post(
            self.url,
            data=urlencode(self.flow_submit_post_data),
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, HTTP_302_FOUND)

    def test_submit_page_post_redirects_to_confirmation_page(self, *mocks):
        response = self.client.post(
            self.url,
            data=urlencode(self.flow_submit_post_data),
            content_type='application/x-www-form-urlencoded',
            follow=True
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTemplateUsed(response, ConfirmationView.template_name)
        self.assertRedirects(
            response=response,
            expected_url=reverse(
                'apply:confirmation', args=(GrantApplicationProcess.objects.first().pk,)
            )
        )
