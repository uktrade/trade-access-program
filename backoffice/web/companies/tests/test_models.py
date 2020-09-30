from web.tests.factories.companies import CompanyFactory, DnbGetCompanyResponseFactory
from web.tests.helpers import BaseTestCase


class TestCompanyModel(BaseTestCase):

    def test_last_dnb_get_company_response(self, *mocks):
        company = CompanyFactory(dnb_get_company_responses=None)
        DnbGetCompanyResponseFactory(company=company)
        dnb_company_instance_2 = DnbGetCompanyResponseFactory(company=company)
        self.assertEqual(company.last_dnb_get_company_response, dnb_company_instance_2)


class TestDnbGetCompanyResponseModel(BaseTestCase):

    def test_company_registration_number(self, *mocks):
        instance = DnbGetCompanyResponseFactory()
        self.assertEqual(
            instance.company_registration_number,
            instance.data['registration_numbers'][0]['registration_number']
        )

        instance.data['registration_numbers'] = None
        self.assertIsNone(instance.company_registration_number)

    def test_company_address(self, *mocks):
        instance = DnbGetCompanyResponseFactory()
        self.assertEqual(
            instance.company_address,
            'Belgrave House, 76 Buckingham Palace Road, LONDON, SW1W 9TQ, UK',
        )

        instance.data['address_line_1'] = ''
        instance.data['address_line_2'] = ''
        instance.data['address_town'] = ''
        instance.data['address_county'] = ''
        instance.data['address_postcode'] = ''
        instance.data['address_country'] = ''
        self.assertIsNone(instance.company_address)
