import httpretty
from requests import HTTPError

from api.companies.services import DnbServiceClient
from api.tests.helpers import BaseTestCase


class DnbServiceTests(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dnb_service_client = DnbServiceClient()
        cls.response_body = '{' \
                            '  "results": [' \
                            '    {"primary_name": "fake-name-1", "duns_number": 1},' \
                            '    {"primary_name": "fake-name-2", "duns_number": 2}' \
                            '  ]' \
                            '}'

    @httpretty.activate
    def test_get_company(self):
        httpretty.register_uri(
            httpretty.POST,
            self.dnb_service_client.company_url,
            status=200,
            body=self.response_body,
            match_querystring=False
        )
        dnb_company = self.dnb_service_client.get_company(duns_number=1)
        self.assertEqual(dnb_company['primary_name'], 'fake-name-1')

    @httpretty.activate
    def test_search_companies(self):
        httpretty.register_uri(
            httpretty.POST,
            self.dnb_service_client.company_url,
            status=200,
            body=self.response_body,
            match_querystring=False
        )
        dnb_companies = self.dnb_service_client.search_companies(search_term='fake-name')
        self.assertEqual(len(dnb_companies), 2)

    @httpretty.activate
    def test_retry_on_500(self):
        httpretty.register_uri(
            httpretty.POST, self.dnb_service_client.company_url, match_querystring=False,
            responses=[
                httpretty.Response(status=500, body=''),
                httpretty.Response(status=200, body=self.response_body)
            ]
        )
        dnb_company = self.dnb_service_client.get_company(duns_number=1)
        self.assertEqual(dnb_company['primary_name'], 'fake-name-1')

    @httpretty.activate
    def test_no_retry_on_400_and_error_raised(self):
        httpretty.register_uri(
            httpretty.POST,
            self.dnb_service_client.company_url,
            status=400,
            match_querystring=False
        )
        self.assertRaises(HTTPError, self.dnb_service_client.get_company, duns_number=1)
