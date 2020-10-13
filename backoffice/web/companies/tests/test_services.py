import json

import httpretty

from web.companies import services
from web.companies.services import DnbServiceClient, CompaniesHouseClient
from web.core.exceptions import DnbServiceClientException, CompaniesHouseApiException
from web.tests.factories.companies import CompanyFactory
from web.tests.helpers import BaseAPITestCase


class DnbServiceTests(BaseAPITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dnb_service_client = DnbServiceClient()
        cls.search_response = {
            'results': [
                {'primary_name': 'name-1', 'duns_number': 1, 'registered_address_country': 'GB'},
                {'primary_name': 'name-2', 'duns_number': 2, 'registered_address_country': 'GB'},
                {'primary_name': 'name-3', 'duns_number': 3, 'registered_address_country': 'PL'}
            ]
        }
        cls.get_response = {
            'results': [
                {'primary_name': 'name-1', 'duns_number': 1, 'registered_address_country': 'GB'}
            ]
        }

    @httpretty.activate
    def test_get_company(self):
        response_body = json.dumps({
            'results': [
                {'primary_name': 'name-1', 'duns_number': 1, 'registered_address_country': 'GB'}
            ]
        })
        httpretty.register_uri(
            httpretty.POST,
            self.dnb_service_client.company_url,
            status=200,
            body=response_body,
            match_querystring=False
        )
        dnb_company = self.dnb_service_client.get_company(duns_number=1)
        self.assertEqual(dnb_company['primary_name'], 'name-1')

    @httpretty.activate
    def test_get_non_gb_company_returns_none(self):
        response_body = json.dumps({
            'results': [
                {'primary_name': 'name-3', 'duns_number': 3, 'registered_address_country': 'PL'}
            ]
        })
        httpretty.register_uri(
            httpretty.POST,
            self.dnb_service_client.company_url,
            status=200,
            body=response_body,
            match_querystring=False
        )
        dnb_company = self.dnb_service_client.get_company(duns_number=3)
        self.assertIsNone(dnb_company)

    @httpretty.activate
    def test_search_companies(self):
        httpretty.register_uri(
            httpretty.POST,
            self.dnb_service_client.company_url,
            status=200,
            body=json.dumps(self.search_response),
            match_querystring=False
        )
        dnb_companies = self.dnb_service_client.search_companies(search_term='name')
        self.assertEqual(len(dnb_companies), 2)

    @httpretty.activate
    def test_search_returns_UK_companies_only(self):
        httpretty.register_uri(
            httpretty.POST,
            self.dnb_service_client.company_url,
            status=200,
            body=json.dumps(self.search_response),
            match_querystring=False
        )
        dnb_companies = self.dnb_service_client.search_companies(search_term='name')
        for company in dnb_companies:
            self.assertEqual(company['registered_address_country'], 'GB')

    @httpretty.activate
    def test_retry_on_500(self):
        httpretty.register_uri(
            httpretty.POST, self.dnb_service_client.company_url, match_querystring=False,
            responses=[
                httpretty.Response(status=500, body=''),
                httpretty.Response(status=200, body=json.dumps(self.get_response))
            ]
        )
        dnb_company = self.dnb_service_client.get_company(duns_number=1)
        self.assertEqual(dnb_company['primary_name'], 'name-1')
        self.assertEqual(len(httpretty.latest_requests()), 2)

    @httpretty.activate
    def test_no_retry_on_400_and_dnb_exception_is_raised(self):
        httpretty.register_uri(
            httpretty.POST,
            self.dnb_service_client.company_url,
            status=400,
            match_querystring=False
        )
        self.assertRaises(
            DnbServiceClientException,
            self.dnb_service_client.get_company,
            duns_number=1
        )
        self.assertEqual(len(httpretty.latest_requests()), 1)


class CompaniesHouseClientTests(BaseAPITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ch_client = CompaniesHouseClient()
        cls.search_response = {
            'items': [{
                'title': 'Company 1',
                'address_snippet': '1 New street, Locality, Country, ZZ0 9ZZ',
                'address': {
                    'locality': 'Locality',
                    'postal_code': 'ZZ0 9ZZ',
                    'address_line_1': 'New street',
                    'country': 'Country',
                    'premises': '1'
                },
                'description_identifier': ['incorporated-on'],
                'company_status': 'active',
                'links': {'self': '/company/10000001'},
                'kind': 'searchresults#company',
                'description': '10000001 - Incorporated on  3 April 2001',
                'matches': {'snippet': [], 'title': [1, 7]},
                'date_of_creation': '2001-04-03',
                'company_number': '10000001',
                'company_type': 'ltd'
            }],
            'start_index': 0,
            'page_number': 1,
            'kind': 'search#companies',
            'total_results': 1,
            'items_per_page': 20
        }

    @httpretty.activate
    def test_search_companies(self):
        httpretty.register_uri(
            httpretty.GET,
            self.ch_client.company_url,
            status=200,
            body=json.dumps(self.search_response),
            match_querystring=False
        )
        companies = self.ch_client.search_companies(search_term='Company 1')
        self.assertListEqual(companies, self.search_response['items'])

    @httpretty.activate
    def test_retry_on_500(self):
        httpretty.register_uri(
            httpretty.GET, self.ch_client.company_url, match_querystring=False,
            responses=[
                httpretty.Response(status=500, body=''),
                httpretty.Response(status=200, body=json.dumps(self.search_response))
            ]
        )
        companies = self.ch_client.search_companies(search_term='Company 1')
        self.assertListEqual(companies, self.search_response['items'])
        self.assertEqual(len(httpretty.latest_requests()), 2)

    @httpretty.activate
    def test_no_retry_on_400_and_exception_is_raised(self):
        httpretty.register_uri(
            httpretty.GET,
            self.ch_client.company_url,
            status=400,
            match_querystring=False
        )
        self.assertRaises(
            CompaniesHouseApiException,
            self.ch_client.search_companies,
            search_term='Company 1'
        )
        self.assertEqual(len(httpretty.latest_requests()), 1)


class ServicesTests(BaseAPITestCase):

    @httpretty.activate
    def test_refresh_dnb_company_response_data_with_dnb_response(self):
        httpretty.register_uri(
            httpretty.POST,
            DnbServiceClient().company_url,
            status=200,
            body=json.dumps({'results': [{'duns_number': 1, 'registered_address_country': 'GB'}]}),
            match_querystring=False
        )
        company = CompanyFactory(duns_number=1, dnb_get_company_responses=None)
        dnb_get_company_response = services.refresh_dnb_company_response_data(company)
        self.assertIsNotNone(dnb_get_company_response)
        self.assertEqual(dnb_get_company_response.company, company)
        self.assertEqual(company.last_dnb_get_company_response, dnb_get_company_response)

    @httpretty.activate
    def test_refresh_dnb_company_response_data_with_no_dnb_response(self):
        httpretty.register_uri(
            httpretty.POST,
            DnbServiceClient().company_url,
            status=200,
            body=json.dumps({'results': []}),
            match_querystring=False
        )
        company = CompanyFactory(duns_number=1, dnb_get_company_responses=None)
        dnb_get_company_response = services.refresh_dnb_company_response_data(company)
        self.assertIsNone(dnb_get_company_response)
        self.assertIsNone(company.last_dnb_get_company_response)
