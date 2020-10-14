import json
from unittest.mock import patch

import httpretty
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from web.companies.models import DnbGetCompanyResponse
from web.companies.services import DnbServiceClient
from web.core.exceptions import DnbServiceClientException, CompaniesHouseApiException
from web.tests.external_api_responses import FAKE_DNB_SEARCH_COMPANIES
from web.tests.factories.companies import CompanyFactory
from web.tests.factories.users import UserFactory
from web.tests.helpers import BaseAPITestCase


class CompaniesApiTests(BaseAPITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dnb_service_client = DnbServiceClient()

    def test_get_company(self, *mocks):
        self.company = CompanyFactory(name='fake-name', duns_number=1)
        path = reverse('companies:companies-detail', args=(self.company.id,))
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(
            response,
            data_contains={
                'id': self.company.id_str,
                'duns_number': '1',
                'name': 'fake-name',
            }
        )
        self.assertListEqual(
            [r['dnb_data'] for r in response.data['dnb_get_company_responses']],
            [r.dnb_data for r in self.company.dnb_get_company_responses.all()]
        )

    def test_list_companies(self, *mocks):
        self.company = CompanyFactory(name='fake-name', duns_number=1)
        response = self.client.get(path=reverse('companies:companies-list'))
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(response, data_contains=[{'id': self.company.id_str}])

    def test_list_companies_with_filter(self, *mocks):
        CompanyFactory(duns_number=10)
        CompanyFactory(duns_number=11)
        response = self.client.get(reverse('companies:companies-list'), data={'duns_number': '11'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 1)
        self.assert_response_data_contains(response, data_contains=[{'duns_number': '11'}])

    def test_list_companies_with_filter_returns_nothing(self, *mocks):
        CompanyFactory(duns_number=10)
        response = self.client.get(reverse('companies:companies-list'), data={'duns_number': '0'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertListEqual(response.data, [])

    @httpretty.activate
    def test_create_new_company(self, *mocks):
        httpretty.register_uri(
            httpretty.POST,
            self.dnb_service_client.company_url,
            status=200,
            body=json.dumps(FAKE_DNB_SEARCH_COMPANIES),
            match_querystring=False
        )
        path = reverse('companies:companies-list')
        response = self.client.post(
            path, data={'name': 'fake-name', 'duns_number': '2', 'registration_number': '1'}
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED, msg=response.data)
        self.assert_response_data_contains(
            response,
            data_contains={'name': 'fake-name', 'duns_number': '2', 'registration_number': '1'}
        )

    @httpretty.activate
    def test_create_company_makes_and_saves_dnb_company_response_data(self, *mocks):
        httpretty.register_uri(
            httpretty.POST,
            self.dnb_service_client.company_url,
            status=200,
            body=json.dumps(FAKE_DNB_SEARCH_COMPANIES),
            match_querystring=False
        )
        path = reverse('companies:companies-list')
        response = self.client.post(
            path, data={'duns_number': '2', 'registration_number': '10000001', 'name': 'fake-name'}
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED, msg=response.data)
        self.assertTrue(DnbGetCompanyResponse.objects.filter(company__duns_number=2).exists())


@patch.object(DnbServiceClient, 'get_company', return_value={'primary_name': 'Company 1'})
@patch.object(
    DnbServiceClient, 'search_companies',
    return_value=[{
        'primary_name': 'Company 1',
        'registration_numbers': [
            {'registration_type': 'uk_companies_house_number', 'registration_number': '03977902'}
          ]
    }])
class SearchCompaniesApiTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.client.force_login(UserFactory())

    def test_search_via_search_term(self, *mocks):
        response = self.client.get(reverse('companies:search'), {'search_term': 'fake-name'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['dnb_data']['primary_name'], 'Company 1')

    def test_search_via_duns_number(self, *mocks):
        response = self.client.get(reverse('companies:search'), {'duns_number': '1'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['dnb_data']['primary_name'], 'Company 1')

    def test_either_search_term_or_duns_number_required(self, *mocks):
        response = self.client.get(reverse('companies:search'))
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST, msg=response.data)
        self.assertEqual(
            response.data['non_field_errors'][0],
            'One of search_term or duns_number required.'
        )

    def test_503_on_dnb_service_exception(self, *mocks):
        mocks[0].side_effect = [DnbServiceClientException]
        response = self.client.get(reverse('companies:search'), {'search_term': 'fake-name'})
        self.assertEqual(response.status_code, 503)

    def test_503_on_companies_house_api_exception(self, *mocks):
        mocks[0].side_effect = [CompaniesHouseApiException]
        response = self.client.get(reverse('companies:search'), {'search_term': 'fake-name'})
        self.assertEqual(response.status_code, 503)
