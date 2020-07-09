from unittest.mock import patch

from django.forms import Field
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_302_FOUND

from web.apply.views import SearchCompanyView, SelectCompanyView, DnbServiceClient
from web.core.exceptions import DnbServiceClientException
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
            expected_url=reverse('viewflow:apply:apply:submit') + '?duns_number=1'
        )

    def test_select_company_post_form_redirect_template(self, *mocks):
        self.set_session_value('search_term', 'company-1')
        response = self.client.post(self.url, {'duns_number': 1}, follow=True)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTemplateUsed(response, 'apply/apply/submit.html')
