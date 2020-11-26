from unittest.mock import patch

from web.companies.services import DnbServiceClient
from web.core.exceptions import DnbServiceClientException
from web.grant_management.services import SupportingInformationContent
from web.tests.factories.companies import DnbGetCompanyResponseFactory
from web.tests.factories.grant_applications import CompletedGrantApplicationFactory
from web.tests.helpers import BaseTestCase


class TestGrantManagementSupportingInformation(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.notify_service_patch = patch('web.grant_management.flows.NotifyService')
        cls.notify_service_patch.start()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.notify_service_patch.stop()

    def setUp(self):
        super().setUp()
        self.ga = CompletedGrantApplicationFactory(company__dnb_get_company_responses=None)
        self.ga.send_for_review()
        self.si_content = SupportingInformationContent(self.ga)

    @patch.object(DnbServiceClient, 'get_company', side_effect=DnbServiceClientException)
    def test_business_entity_content_on_dnb_service_error(self, *mocks):
        self.assertIsNone(self.si_content.verify_business_entity_content)

    @patch.object(
        DnbServiceClient, 'get_company',
        return_value={
            'primary_name': 'company-1',
            'is_employees_number_estimated': True,
            'employee_number': 1,
            'annual_sales': None,
            'annual_sales_currency': None
        }
    )
    def test_business_entity_content_if_annual_sales_is_none(self, *mocks):
        self.assertEqual(self.si_content.verify_business_entity_content['annual_sales'], 0)

    @patch.object(DnbServiceClient, 'get_company', return_value={'primary_name': 'company-1'})
    def test_dnb_company_data_from_db_cache_instead_of_dnb_service(self, *mocks):
        DnbGetCompanyResponseFactory(company=self.ga.company, dnb_data={'response': 1})
        DnbGetCompanyResponseFactory(company=self.ga.company, dnb_data={'response': 2})
        self.assertIsNotNone(self.si_content.dnb_company_data)
        self.assertEqual(self.si_content.dnb_company_data['response'], 2)
