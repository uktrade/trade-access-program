import json
from unittest.mock import patch

import httpretty
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from web.companies.apis import DnbServiceClient
from web.companies.models import DnbGetCompanyResponse
from web.core.exceptions import DnbServiceClientException
from web.tests.factories.companies import CompanyFactory
from web.tests.factories.users import UserFactory
from web.tests.helpers import BaseAPITestCase


class CompaniesApiTests(BaseAPITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dnb_service_client = DnbServiceClient()

    def setUp(self):
        super().setUp()
        self.company = CompanyFactory(name='fake-name', duns_number=1)

    def test_get_company(self, *mocks):
        path = reverse('companies-detail', args=(self.company.id,))
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(
            response,
            data_contains={
                'id': self.company.id_str,
                'duns_number': 1,
                'name': 'fake-name',
            }
        )
        self.assertListEqual(
            [r['data'] for r in response.data['dnb_get_company_responses']],
            [r.data for r in self.company.dnb_get_company_responses.all()]
        )

    def test_list_companies(self, *mocks):
        response = self.client.get(path=reverse('companies-list'))
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(response, data_contains=[{'id': self.company.id_str}])

    def test_list_companies_with_filter(self, *mocks):
        CompanyFactory(duns_number=10)
        CompanyFactory(duns_number=11)
        response = self.client.get(path=reverse('companies-list'), data={'duns_number': 11})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 1)
        self.assert_response_data_contains(response, data_contains=[{'duns_number': 11}])

    @httpretty.activate
    def test_create_new_company(self, *mocks):
        httpretty.register_uri(
            httpretty.POST,
            self.dnb_service_client.company_url,
            status=200,
            body=json.dumps({'results': [self.company.last_dnb_get_company_response.data]}),
            match_querystring=False
        )
        path = reverse('companies-list')
        response = self.client.post(path, {'duns_number': 2, 'name': 'fake-name'})
        self.assertEqual(response.status_code, HTTP_201_CREATED, msg=response.data)
        self.assert_response_data_contains(
            response, data_contains={'name': 'fake-name', 'duns_number': 2}
        )

    @httpretty.activate
    def test_create_company_makes_and_saves_dnb_company_response_data(self, *mocks):
        httpretty.register_uri(
            httpretty.POST,
            self.dnb_service_client.company_url,
            status=200,
            body=json.dumps({'results': [self.company.last_dnb_get_company_response.data]}),
            match_querystring=False
        )
        path = reverse('companies-list')
        response = self.client.post(path, {'duns_number': 2, 'name': 'fake-name'})
        self.assertEqual(response.status_code, HTTP_201_CREATED, msg=response.data)
        self.assertTrue(DnbGetCompanyResponse.objects.filter(company__duns_number=2).exists())


@patch.object(
    DnbServiceClient,
    'search_companies',
    return_value=[{'primary_name': 'fake-name-1', 'x': 1}, {'primary_name': 'fake-name-2', 'y': 2}]
)
class SearchCompaniesApiTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.client.force_login(UserFactory())

    def test_search_company_names(self, *mocks):
        response = self.client.get(reverse('companies-search'), {'search_term': 'fake-name'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertListEqual(
            response.data,
            [{'primary_name': 'fake-name-1', 'x': 1}, {'primary_name': 'fake-name-2', 'y': 2}]
        )

    def test_search_term_required(self, *mocks):
        response = self.client.get(reverse('companies-search'))
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST, msg=response.data)
        self.assertEqual(response.data['search_term'][0].code, 'required')

    def test_cannot_use_blank_search_term(self, *mocks):
        response = self.client.get(reverse('companies-search'), {'search_term': ''})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST, msg=response.data)
        self.assertEqual(response.data['search_term'][0].code, 'blank')

    def test_503_on_dnb_service_exception(self, *mocks):
        mocks[0].side_effect = [DnbServiceClientException]
        response = self.client.get(reverse('companies-search'), {'search_term': 'fake-name'})
        self.assertEqual(response.status_code, 503)
