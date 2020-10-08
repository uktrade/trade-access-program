import json
import logging
from unittest.mock import patch
from urllib.parse import urljoin

import httpretty

from web.grant_applications.services import BackofficeService, BackofficeServiceException
from web.tests.helpers.backoffice_objects import (
    FAKE_GRANT_APPLICATION, FAKE_GRANT_MANAGEMENT_PROCESS, FAKE_SEARCH_COMPANIES, FAKE_COMPANY,
    FAKE_SECTOR, FAKE_EVENT
)
from web.tests.helpers.testcases import BaseTestCase, LogCaptureMixin


class TestBackofficeService(LogCaptureMixin, BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = BackofficeService()

        # Fake backoffice grant application object
        cls.bga = FAKE_GRANT_APPLICATION
        cls.bga_response_body = json.dumps(cls.bga)

        # Fake backoffice grant management process object
        cls.gmp = FAKE_GRANT_MANAGEMENT_PROCESS
        cls.gmp_response_body = json.dumps(cls.gmp)

        # Fake backoffice company object
        cls.company = FAKE_COMPANY
        cls.company_response_body = json.dumps(cls.company)

        # Fake backoffice search companies response object
        cls.scr = FAKE_SEARCH_COMPANIES
        cls.scr_response_body = json.dumps(cls.scr)

        # Fake backoffice list events response object
        cls.ler = [FAKE_EVENT]
        cls.ler_response_body = json.dumps(cls.ler)

        # Fake backoffice list sectors response object
        cls.lsr = [FAKE_SECTOR]
        cls.lsr_response_body = json.dumps(cls.lsr)

    @httpretty.activate
    def test_create_company(self):
        httpretty.register_uri(
            httpretty.POST,
            self.service.companies_url,
            status=201,
            body=self.company_response_body,
        )
        company = self.service.create_company(
            duns_number=self.company['duns_number'], name=self.company['name']
        )
        requests = httpretty.latest_requests()
        self.assertEqual(company['id'], self.company['id'])
        self.assertEqual(len(requests), 1)

    @httpretty.activate
    def test_get_company(self):
        httpretty.register_uri(
            httpretty.GET,
            urljoin(self.service.companies_url, f"{self.company['id']}/"),
            status=200,
            body=self.company_response_body,
        )
        company = self.service.get_company(company_id=self.company['id'])
        self.assertEqual(company['id'], self.company['id'])

    @httpretty.activate
    def test_list_companies(self):
        httpretty.register_uri(
            httpretty.GET,
            self.service.companies_url,
            status=200,
            body=json.dumps([self.company, self.company])
        )
        companies = self.service.list_companies()
        self.assertEqual(len(companies), 2)

    @patch.object(BackofficeService, 'create_company')
    @patch.object(BackofficeService, 'list_companies')
    def test_get_or_create_company_for_existing_company(self, list_mock, create_mock):
        list_mock.return_value = [self.company]
        company = self.service.get_or_create_company(
            duns_number=self.company['duns_number'], name=self.company['name']
        )
        create_mock.assert_not_called()
        self.assertEqual(company, self.company)

    @patch.object(BackofficeService, 'create_company')
    @patch.object(BackofficeService, 'list_companies')
    def test_get_or_create_company_for_new_company(self, list_mock, create_mock):
        list_mock.return_value = []
        create_mock.return_value = self.company
        company = self.service.get_or_create_company(
            duns_number=self.company['duns_number'], name=self.company['name']
        )
        self.assertEqual(company, self.company)
        create_mock.assert_called_once_with(
            duns_number=self.company['duns_number'], name=self.company['name']
        )

    @patch.object(BackofficeService, 'create_company')
    @patch.object(BackofficeService, 'list_companies')
    def test_get_or_create_company_for_bad_list_response(self, list_mock, _):
        list_mock.return_value = [self.company, self.company]
        self.assertRaises(
            BackofficeServiceException,
            self.service.get_or_create_company,
            duns_number=self.company['duns_number'],
            name=self.company['name']
        )

    @httpretty.activate
    def test_create_grant_application(self):
        httpretty.register_uri(
            httpretty.POST,
            self.service.grant_applications_url,
            status=201,
            body=self.bga_response_body
        )
        bga = self.service.create_grant_application(search_term='search-term')
        self.assertEqual(bga['id'], self.bga['id'])

        requests = httpretty.latest_requests()
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].method, 'POST')
        self.assertDictEqual(requests[0].parsed_body, {'search_term': 'search-term'})

    @httpretty.activate
    def test_update_grant_application(self):
        httpretty.register_uri(
            httpretty.PATCH,
            urljoin(self.service.grant_applications_url, f'{self.bga["id"]}/'),
            status=200,
            body=self.bga_response_body,
            match_querystring=False
        )
        self.service.update_grant_application(self.bga['id'], turnover=2000)
        request = httpretty.last_request()
        self.assertEqual(request.method, 'PATCH')
        self.assertEqual(request.parsed_body, {'turnover': 2000})

    @httpretty.activate
    def test_get_grant_application(self):
        httpretty.register_uri(
            httpretty.GET,
            urljoin(self.service.grant_applications_url, f'{self.bga["id"]}/'),
            status=200,
            body=self.bga_response_body,
            match_querystring=False
        )
        bga = self.service.get_grant_application(self.bga['id'])
        request = httpretty.last_request()
        self.assertEqual(bga['id'], self.bga['id'])
        self.assertEqual(request.method, 'GET')

    @httpretty.activate
    def test_get_grant_application_flattens_response_data(self):
        httpretty.register_uri(
            httpretty.GET,
            urljoin(self.service.grant_applications_url, f'{self.bga["id"]}/'),
            status=200,
            body=self.bga_response_body,
            match_querystring=False
        )
        bga = self.service.get_grant_application(
            self.bga['id'],
            flatten_map={
                'event': 'event.name',
                'company': 'company.duns_number',
                'sector': 'sector.id',
            }
        )
        self.assertNotEqual(bga, FAKE_GRANT_APPLICATION)
        self.assertEqual(bga['event'], FAKE_GRANT_APPLICATION['event']['name'])
        self.assertEqual(bga['company'], FAKE_GRANT_APPLICATION['company']['duns_number'])
        self.assertEqual(bga['sector'], FAKE_GRANT_APPLICATION['sector']['id'])

    @httpretty.activate
    def test_get_grant_application_flattens_response_data_create_new_key(self):
        httpretty.register_uri(
            httpretty.GET,
            urljoin(self.service.grant_applications_url, f'{self.bga["id"]}/'),
            status=200,
            body=self.bga_response_body,
            match_querystring=False
        )
        bga = self.service.get_grant_application(
            self.bga['id'],
            flatten_map={
                'new-key': 'event.name',
            }
        )
        self.assertEqual(bga['new-key'], FAKE_GRANT_APPLICATION['event']['name'])
        self.assertDictEqual(bga['event'], FAKE_GRANT_APPLICATION['event'])

    @httpretty.activate
    def test_send_grant_application_for_review(self):
        httpretty.register_uri(
            httpretty.POST,
            urljoin(self.service.grant_applications_url, f"{self.bga['id']}/send-for-review/"),
            status=200,
            body=self.gmp_response_body
        )
        gmp = self.service.send_grant_application_for_review(self.bga['id'], 'fake-summary')
        self.assertEqual(gmp['id'], self.gmp['id'])

    @httpretty.activate
    def test_search_companies(self):
        httpretty.register_uri(
            httpretty.GET,
            urljoin(self.service.companies_url, 'search/'),
            status=200,
            body=self.scr_response_body,
            match_querystring=False
        )
        scr = self.service.search_companies(search_term='Company')
        self.assertEqual(scr, self.scr)

    @httpretty.activate
    def test_list_trade_events(self):
        httpretty.register_uri(
            httpretty.GET,
            self.service.trade_events_url,
            status=200,
            body=self.ler_response_body,
            match_querystring=False
        )
        ler = self.service.list_trade_events(params={})
        self.assertEqual(ler, self.ler)

    @httpretty.activate
    def test_list_trade_events_with_filter(self):
        httpretty.register_uri(
            httpretty.GET,
            self.service.trade_events_url,
            status=200,
            body=self.ler_response_body,
            match_querystring=False
        )
        ler = self.service.list_trade_events(params={'key': 'value'})
        self.assertEqual(ler, self.ler)

    @httpretty.activate
    def test_list_sectors(self):
        httpretty.register_uri(
            httpretty.GET,
            self.service.sectors_url,
            status=200,
            body=self.lsr_response_body,
            match_querystring=False
        )
        lsr = self.service.list_sectors()
        self.assertEqual(lsr, self.lsr)

    @httpretty.activate
    def test_retry_on_500(self):
        httpretty.register_uri(
            httpretty.GET,
            urljoin(self.service.grant_applications_url, f'{self.bga["id"]}/'),
            match_querystring=False,
            responses=[
                httpretty.Response(status=500, body=''),
                httpretty.Response(status=200, body=self.bga_response_body)
            ]
        )
        bga = self.service.get_grant_application(self.bga['id'])
        self.assertEqual(bga['id'], self.bga['id'])
        self.assertEqual(len(httpretty.latest_requests()), 2)

    @httpretty.activate
    def test_no_retry_on_400_and_backoffice_service_exception_is_raised(self):
        httpretty.register_uri(
            httpretty.GET,
            urljoin(self.service.grant_applications_url, f'{self.bga["id"]}/'),
            status=400,
            match_querystring=False
        )
        self.assertRaises(
            BackofficeServiceException, self.service.get_grant_application, self.bga['id']
        )
        self.assertEqual(len(httpretty.latest_requests()), 1)

    @httpretty.activate
    def test_log_error_on_400(self):
        self.log_capture.setLevel(logging.ERROR)
        url = urljoin(self.service.grant_applications_url, f'{self.bga["id"]}/')
        httpretty.register_uri(httpretty.GET, url, status=400, match_querystring=False)
        self.assertRaises(
            BackofficeServiceException, self.service.get_grant_application, self.bga['id']
        )
        self.log_capture.check_present(
            ('web.grant_applications.services', 'ERROR', 'An error occurred'),
        )

    @httpretty.activate
    def test_log_info_on_all_requests(self):
        self.log_capture.setLevel(logging.INFO)
        url = urljoin(self.service.grant_applications_url, f'{self.bga["id"]}/')
        httpretty.register_uri(httpretty.GET, url, status=200, match_querystring=False)
        self.service.get_grant_application(self.bga['id'])
        self.log_capture.check_present(
            ('web.grant_applications.services', 'INFO', f'EXTERNAL GET : {url} : No content'),
        )

    @httpretty.activate
    def test_request_factory_unknown_object_type(self):
        self.assertRaises(
            ValueError, self.service.request_factory,
            object_type='bad-type', choice_id_key='', choice_name_key='',
        )
