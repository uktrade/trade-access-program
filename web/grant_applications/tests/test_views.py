from datetime import timedelta
from unittest.mock import patch
from urllib.parse import urlencode

from dateutil.utils import today
from django.forms import Field
from django.urls import reverse, resolve
from rest_framework.status import HTTP_200_OK, HTTP_302_FOUND

from web.core.exceptions import DnbServiceClientException
from web.grant_applications.models import GrantApplication
from web.grant_applications.views import (
    SearchCompanyView, SelectCompanyView, DnbServiceClient, AboutYourBusinessView,
    AboutYouView
)
from web.tests.helpers import BaseTestCase


@patch.object(DnbServiceClient, 'get_company', return_value={'primary_name': 'company-1'})
@patch.object(
    DnbServiceClient, 'search_companies',
    return_value=[{'primary_name': 'company-1', 'duns_number': 1}]
)
class TestSearchCompanyView(BaseTestCase):

    def setUp(self):
        self.url = reverse('grant_applications:search-company')

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
            expected_url=reverse('grant_applications:select-company') + '?search_term=company-1'
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
        self.url = reverse('grant_applications:select-company')

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
        response = self.client.post(self.url, data={'duns_number': 1})
        self.assertEqual(response.status_code, HTTP_302_FOUND)
        ga = GrantApplication.objects.get(duns_number=1)
        self.assertRedirects(
            response,
            expected_url=reverse('grant_applications:about-your-business', kwargs={'pk': ga.pk})
        )

    def test_select_company_post_form_redirect_template(self, *mocks):
        self.set_session_value('search_term', 'company-1')
        response = self.client.post(self.url, {'duns_number': 1}, follow=True)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTemplateUsed(response, AboutYourBusinessView.template_name)


@patch('web.grant_management.flows.NotifyService')
@patch.object(DnbServiceClient, 'get_company', return_value={'primary_name': 'company-1'})
@patch.object(
    DnbServiceClient, 'search_companies',
    return_value=[{'primary_name': 'company-1', 'duns_number': 1}]
)
class TestAboutYourBusinessView(BaseTestCase):

    def setUp(self):
        self.ga = GrantApplication.objects.create(duns_number=1)
        self.url = reverse('grant_applications:about-your-business', kwargs={'pk': self.ga.pk})
        self.tomorrow = today() + timedelta(days=1)

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTemplateUsed(response, AboutYourBusinessView.template_name)

    def test_get_dnb_service_exception(self, *mocks):
        mocks[1].side_effect = [DnbServiceClientException]
        response = self.client.get(self.url)
        self.assertIn('Could not retrieve company name.', response.content.decode())

    def test_submit_page_post_redirects(self, *mocks):
        response = self.client.post(
            self.url, content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, HTTP_302_FOUND)

    def test_submit_page_post_redirects_to_confirmation_page(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            follow=True
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTemplateUsed(response, AboutYouView.template_name)
        self.assertRedirects(
            response=response,
            expected_url=reverse('grant_applications:about-you', kwargs={'pk': self.ga.pk})
        )


class TestAboutYouView(BaseTestCase):

    def setUp(self):
        self.ga = GrantApplication.objects.create(duns_number=1)
        self.url = reverse('grant_applications:about-you', kwargs={'pk': self.ga.pk})

    def test_post_redirects(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'applicant_full_name': 'A Name',
                'applicant_email': 'test@test.com',
            })
        )
        self.assertEqual(response.status_code, HTTP_302_FOUND)

    def test_post_data_is_saved(self, *mocks):
        self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'applicant_full_name': 'A Name',
                'applicant_email': 'test@test.com',
            })
        )
        self.ga.refresh_from_db()
        self.assertEqual(self.ga.applicant_full_name, 'A Name')
        self.assertEqual(self.ga.applicant_email, 'test@test.com')


class TestTheEventView(BaseTestCase):

    def setUp(self):
        self.ga = GrantApplication.objects.create(duns_number=1)
        self.url = reverse('grant_applications:about-the-event', kwargs={'pk': self.ga.pk})

    def test_post_redirects(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'event': 'Event',
                'is_already_committed_to_event': True,
                'is_intending_on_other_financial_support': True,
            })
        )
        self.assertEqual(response.status_code, HTTP_302_FOUND)

    def test_post_data_is_saved(self, *mocks):
        self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded',
            data=urlencode({
                'event': 'An Event',
                'is_already_committed_to_event': True,
                'is_intending_on_other_financial_support': True,
            })
        )
        self.ga.refresh_from_db()
        self.assertEqual(self.ga.event, 'An Event')
        self.assertTrue(self.ga.is_already_committed_to_event)
        self.assertTrue(self.ga.is_intending_on_other_financial_support)


@patch('web.grant_management.flows.NotifyService')
class TestApplicationReviewView(BaseTestCase):

    def setUp(self):
        self.ga = GrantApplication.objects.create(
            duns_number=1,
            applicant_full_name='A Name',
            applicant_email='test@test.com',
            event='An Event',
            is_already_committed_to_event=True,
            is_intending_on_other_financial_support=False,
        )
        self.url = reverse('grant_applications:application-review', kwargs={'pk': self.ga.pk})

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn('<dl class="govuk-summary-list">', response.content.decode())

    def test_post_redirects(self, *mocks):
        response = self.client.post(
            self.url,
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, HTTP_302_FOUND)
        redirect = resolve(response.url)
        self.assertEqual(redirect.kwargs['pk'], self.ga.id_str)
        self.assertEqual(redirect.kwargs['process_pk'], str(self.ga.grantapplicationprocess.pk))
