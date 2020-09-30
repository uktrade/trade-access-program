import factory

from web.companies.models import Company, DnbGetCompanyResponse
from web.tests.factories.base import BaseMetaFactory


class CompanyFactory(BaseMetaFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: f'name-{n}')
    duns_number = factory.Sequence(lambda n: n)
    dnb_get_company_responses = factory.RelatedFactory(
        'web.tests.factories.companies.DnbGetCompanyResponseFactory',
        factory_related_name='company'
    )


class DnbGetCompanyResponseFactory(BaseMetaFactory):
    class Meta:
        model = DnbGetCompanyResponse

    company = factory.SubFactory(CompanyFactory)
    data = {
        'duns_number': '239896579',
        'primary_name': 'GOOGLE UK LIMITED',
        'trading_names': [],
        'registration_numbers': [{
            'registration_type': 'uk_companies_house_number',
            'registration_number': '03977902'
        }],
        'global_ultimate_duns_number': '079942718',
        'global_ultimate_primary_name': 'Alphabet Inc.',
        'domain': 'google.co.uk',
        'is_out_of_business': False,
        'address_line_1': 'Belgrave House',
        'address_line_2': '76 Buckingham Palace Road',
        'address_town': 'LONDON',
        'address_county': '',
        'address_postcode': 'SW1W 9TQ',
        'address_country': 'UK',
        'registered_address_line_1': '',
        'registered_address_line_2': '',
        'registered_address_town': 'LONDON',
        'registered_address_county': '',
        'registered_address_postcode': 'SW1W 9TQ',
        'registered_address_country': 'GB',
        'annual_sales': 2026167095.0,
        'annual_sales_currency': 'USD',
        'is_annual_sales_estimated': None,
        'employee_number': 4439,
        'is_employees_number_estimated': True,
    }
