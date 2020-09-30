from unittest.mock import patch

from web.companies.services import DnbServiceClient
from web.core.exceptions import DnbServiceClientException
from web.grant_management.services import SupportingInformationContent
from web.tests.factories.companies import DnbGetCompanyResponseFactory
from web.tests.factories.grant_applications import GrantApplicationFactory
from web.tests.helpers import BaseTestCase


class TestGrantManagementSupportingInformation(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.ga = GrantApplicationFactory(company__dnb_get_company_responses=None)
        self.si_content = SupportingInformationContent(self.ga)

    @patch.object(DnbServiceClient, 'get_company', side_effect=DnbServiceClientException)
    def test_employee_count_content_on_dnb_service_error(self, *mocks):
        # Assert no dnb exception is caught and error is mentioned in content
        self.assertIn('tables', self.si_content.employee_count_content)
        self.assertIn(
            'Could not retrieve Dun & Bradstreet data',
            str(self.si_content.employee_count_content)
        )

    @patch.object(DnbServiceClient, 'get_company', side_effect=DnbServiceClientException)
    def test_turnover_content_on_dnb_service_error(self, *mocks):
        # Assert no dnb exception is caught and error is mentioned in content
        self.assertIn('tables', self.si_content.turnover_content)
        self.assertIn(
            'Could not retrieve Dun & Bradstreet data',
            str(self.si_content.turnover_content)
        )

    @patch.object(DnbServiceClient, 'get_company', return_value={'primary_name': 'company-1'})
    def test_dnb_company_data_from_db_cache_instead_of_dnb_service(self, *mocks):
        DnbGetCompanyResponseFactory(company=self.ga.company, data={'response': 1})
        DnbGetCompanyResponseFactory(company=self.ga.company, data={'response': 2})
        self.assertIsNotNone(self.si_content.dnb_company_data)
        self.assertEqual(self.si_content.dnb_company_data['response'], 2)
