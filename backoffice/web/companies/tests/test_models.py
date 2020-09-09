from web.tests.factories.companies import CompanyFactory, DnbGetCompanyResponseFactory
from web.tests.helpers import BaseTestCase


class TestModels(BaseTestCase):

    def test_company_last_dnb_get_company_response(self, *mocks):
        company = CompanyFactory()
        DnbGetCompanyResponseFactory(company=company)
        dnb_company_instance_2 = DnbGetCompanyResponseFactory(company=company)
        self.assertEqual(company.last_dnb_get_company_response, dnb_company_instance_2)

    def test_company_last_dnb_get_company_response_none(self, *mocks):
        company = CompanyFactory()
        self.assertIsNone(company.last_dnb_get_company_response)
