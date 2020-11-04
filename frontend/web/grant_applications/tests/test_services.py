import json
import logging
from unittest.mock import patch
from urllib.parse import urljoin

import httpretty

from web.grant_applications.services import (
    BackofficeService, BackofficeServiceException,
    get_backoffice_choices, get_companies_from_search_term, generate_company_select_options
)
from web.tests.helpers.backoffice_objects import (
    FAKE_GRANT_APPLICATION, FAKE_GRANT_MANAGEMENT_PROCESS, FAKE_SEARCH_COMPANIES, FAKE_COMPANY,
    FAKE_SECTOR, FAKE_EVENT, FAKE_TRADE_EVENT_AGGREGATES, FAKE_STATE_AID
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

        # Fake backoffice state aid object
        cls.bsa = FAKE_STATE_AID
        cls.bsa_response_body = json.dumps(cls.bsa)

        # Fake backoffice list state aid object
        cls.lsa = [FAKE_STATE_AID]
        cls.lsa_response_body = json.dumps(cls.lsa)

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

        # Fake backoffice trade event aggregates object
        cls.tea = FAKE_TRADE_EVENT_AGGREGATES
        cls.tea_response_body = json.dumps(cls.tea)

    @httpretty.activate
    def test_create_company(self):
        httpretty.register_uri(
            httpretty.POST,
            self.service.companies_url,
            status=201,
            body=self.company_response_body,
        )
        company = self.service.create_company(
            duns_number=self.company['duns_number'],
            registration_number=self.company['registration_number'],
            name=self.company['name']
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
            duns_number=self.company['duns_number'],
            registration_number=self.company['registration_number'],
            name=self.company['name']
        )
        create_mock.assert_not_called()
        self.assertEqual(company, self.company)

    @patch.object(BackofficeService, 'create_company')
    @patch.object(BackofficeService, 'list_companies')
    def test_get_or_create_company_for_new_company(self, list_mock, create_mock):
        list_mock.return_value = []
        create_mock.return_value = self.company
        company = self.service.get_or_create_company(
            duns_number=self.company['duns_number'],
            registration_number=self.company['registration_number'],
            name=self.company['name']
        )
        self.assertEqual(company, self.company)
        create_mock.assert_called_once_with(
            duns_number=self.company['duns_number'],
            registration_number=self.company['registration_number'],
            name=self.company['name']
        )

    @patch.object(BackofficeService, 'create_company')
    @patch.object(BackofficeService, 'list_companies')
    def test_get_or_create_company_for_bad_list_response(self, list_mock, _):
        list_mock.return_value = [self.company, self.company]
        self.assertRaises(
            BackofficeServiceException,
            self.service.get_or_create_company,
            duns_number=self.company['duns_number'],
            registration_number=self.company['registration_number'],
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
    def test_create_state_aid(self):
        httpretty.register_uri(
            httpretty.POST,
            self.service.state_aid_url,
            status=201,
            body=self.bsa_response_body
        )
        bsa = self.service.create_state_aid(**FAKE_STATE_AID)
        self.assertEqual(bsa['id'], self.bsa['id'])

        requests = httpretty.latest_requests()
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].method, 'POST')
        self.assertDictEqual(requests[0].parsed_body, FAKE_STATE_AID)

    @httpretty.activate
    def test_update_state_aid(self):
        httpretty.register_uri(
            httpretty.PATCH,
            urljoin(self.service.state_aid_url, f'{self.bsa["id"]}/'),
            status=200,
            body=self.bsa_response_body,
            match_querystring=False
        )
        self.service.update_state_aid(self.bsa['id'], amount=1000)
        request = httpretty.last_request()
        self.assertEqual(request.method, 'PATCH')
        self.assertEqual(request.parsed_body, {'amount': 1000})

    @httpretty.activate
    def test_delete_state_aid(self):
        httpretty.register_uri(
            httpretty.DELETE,
            urljoin(self.service.state_aid_url, f'{self.bsa["id"]}/'),
            status=204
        )
        self.service.delete_state_aid(self.bsa['id'])
        request = httpretty.last_request()
        self.assertEqual(request.method, 'DELETE')

    @httpretty.activate
    def test_get_state_aid(self):
        httpretty.register_uri(
            httpretty.GET,
            urljoin(self.service.state_aid_url, f'{self.bsa["id"]}/'),
            status=200,
            body=self.bsa_response_body,
            match_querystring=False
        )
        bsa = self.service.get_state_aid(self.bsa['id'])
        request = httpretty.last_request()
        self.assertEqual(bsa['id'], self.bsa['id'])
        self.assertEqual(request.method, 'GET')

    @httpretty.activate
    def test_list_state_aids(self):
        httpretty.register_uri(
            httpretty.GET,
            self.service.state_aid_url,
            status=200,
            body=self.lsa_response_body,
            match_querystring=False
        )
        lsa = self.service.list_state_aids()
        self.assertEqual(lsa, self.lsa)

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
    def test_get_trade_event_aggregates(self):
        httpretty.register_uri(
            httpretty.GET,
            self.service.trade_event_aggregates_url,
            status=200,
            body=json.dumps(self.tea)
        )
        aggregates = self.service.get_trade_event_aggregates()
        self.assertDictEqual(aggregates, FAKE_TRADE_EVENT_AGGREGATES)

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


class TestServices(BaseTestCase):

    @patch.object(BackofficeService, 'request_factory', side_effect=BackofficeServiceException)
    def test_get_backoffice_choices_exception_gives_empty_list(self, _):
        choices = get_backoffice_choices(
            object_type='fake', choice_id_key='fake', choice_name_key='fake'
        )
        self.assertListEqual(choices, [])

    @patch.object(BackofficeService, 'search_companies', side_effect=BackofficeServiceException)
    def test_get_companies_with_blank_search_term(self, search_companies_mock):
        self.assertIsNone(get_companies_from_search_term(''))
        search_companies_mock.assert_not_called()

    @patch.object(BackofficeService, 'search_companies', side_effect=BackofficeServiceException)
    def test_get_companies_from_search_term_registration_number(self, search_companies_mock):
        self.assertIsNone(get_companies_from_search_term(search_term='01234567'))
        search_companies_mock.assert_called_once_with(registration_numbers=['01234567'])

    @patch.object(BackofficeService, 'search_companies', return_value=FAKE_SEARCH_COMPANIES)
    def test_get_companies_from_search_term_primary_name(self, search_companies_mock):
        companies = get_companies_from_search_term(search_term='fake')
        search_companies_mock.assert_called_once_with(primary_name='fake')
        self.assertEqual(companies, FAKE_SEARCH_COMPANIES)

    def test_generate_company_select_options(self):
        fake = FAKE_SEARCH_COMPANIES[0]
        options = generate_company_select_options(FAKE_SEARCH_COMPANIES)
        self.assertDictEqual(
            options,
            {
                'choices': [(fake['dnb_data']['duns_number'], fake['dnb_data']['primary_name'])],
                'hints': [fake['registration_number']]
            }
        )
