import httpretty

from web.companies import services
from web.companies.services import DnbServiceClient
from web.core.exceptions import DnbServiceClientException
from web.tests.helpers import BaseAPITestCase


class DnbServiceTests(BaseAPITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dnb_service_client = DnbServiceClient()
        cls.search_response_body = \
            '{' \
            '  "results": [' \
            '    {"primary_name": "name-1","duns_number": 1,"registered_address_country": "GB"},' \
            '    {"primary_name": "name-2","duns_number": 2,"registered_address_country": "GB"},' \
            '    {"primary_name": "name-3","duns_number": 3,"registered_address_country": "PL"}' \
            '  ]' \
            '}'

    @httpretty.activate
    def test_get_company(self):
        response_body = \
            '{' \
            '  "results": [' \
            '    {"primary_name": "name-1","duns_number": 1,"registered_address_country": "GB"}' \
            '  ]' \
            '}'
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
        response_body = \
            '{' \
            '  "results": [' \
            '    {"primary_name": "name-3","duns_number": 3,"registered_address_country": "PL"}' \
            '  ]' \
            '}'
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
            body=self.search_response_body,
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
            body=self.search_response_body,
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
                httpretty.Response(status=200, body=self.search_response_body)
            ]
        )
        dnb_company = self.dnb_service_client.get_company(duns_number=1)
        self.assertEqual(dnb_company['primary_name'], 'name-1')

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


class ServicesTests(BaseAPITestCase):

    def test_save_dnb_get_company_response_with_dnb_company_data(self):
        dnb_company_data = {
            'primary_name': 'name-1',
            'duns_number': 1,
            'registered_address_country': 'GB'
        }
        company = services.save_company_and_dnb_response(
            duns_number=1, dnb_company_data=dnb_company_data
        )
        self.assertEqual(company.duns_number, 1)
        self.assertEqual(company.dnbgetcompanyresponse_set.count(), 1)
        self.assertEqual(company.last_dnb_get_company_response.data, dnb_company_data)

    def test_save_dnb_get_company_response_without_dnb_company_data(self):
        company = services.save_company_and_dnb_response(duns_number=1)
        self.assertEqual(company.duns_number, 1)
        self.assertFalse(company.dnbgetcompanyresponse_set.exists())
