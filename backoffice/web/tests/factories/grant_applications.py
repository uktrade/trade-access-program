from decimal import Decimal

import factory

from web.grant_applications.models import GrantApplication


class GrantApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantApplication


class InactiveGrantApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantApplication

    previous_applications = 6


class CompletedGrantApplicationFactory(GrantApplicationFactory):
    previous_applications = 1
    event = factory.SubFactory('web.tests.factories.events.EventFactory')
    is_already_committed_to_event = False
    search_term = factory.Sequence(lambda n: f'search_term-{n}')
    company = factory.SubFactory('web.tests.factories.companies.CompanyFactory')
    manual_company_type = GrantApplication.CompanyType.LIMITED_COMPANY
    manual_company_name = 'A Name'
    manual_company_address_line_1 = 'Line 1'
    manual_company_address_line_2 = 'Line 2'
    manual_company_address_town = 'Town 1'
    manual_company_address_county = 'County 1'
    manual_company_address_postcode = 'ZZ0 1ZZ'
    manual_time_trading_in_uk = GrantApplication.TimeTradingInUk.TWO_TO_FIVE_YEARS
    manual_registration_number = '012345678'
    manual_vat_number = '012345678'
    manual_website = 'https://www.test.com'
    number_of_employees = GrantApplication.NumberOfEmployees.HAS_FEWER_THAN_10
    is_turnover_greater_than = False
    applicant_full_name = factory.Sequence(lambda n: f'name-{n}')
    applicant_email = factory.Sequence(lambda n: f'test{n}@test.com')
    applicant_mobile_number = factory.Sequence(lambda n: f'+44{n:011}')
    job_title = 'director'
    previous_years_turnover_1 = Decimal('1.23')
    previous_years_turnover_2 = Decimal('1.23')
    previous_years_turnover_3 = Decimal('0.00')
    previous_years_export_turnover_1 = Decimal('1.23')
    previous_years_export_turnover_2 = Decimal('1.23')
    previous_years_export_turnover_3 = Decimal('0.00')
    sector = factory.SubFactory('web.tests.factories.sector.SectorFactory')
    other_business_names = factory.Sequence(lambda n: f'other-business-names-{n}')
    products_and_services_description = factory.Sequence(lambda n: f'description-{n}')
    products_and_services_competitors = factory.Sequence(lambda n: f'description-{n}')
    has_exported_before = False
    has_product_or_service_for_export = True
    has_exported_in_last_12_months = True
    export_regions = ['africa', 'north america']
    markets_intending_on_exporting_to = ['existing', 'new']
    is_in_contact_with_dit_trade_advisor = True
    ita_name = 'A TCP name'
    ita_email = 'tcp@test.com'
    ita_mobile_number = '+447777777777'
    export_experience_description = 'A description'
    export_strategy = 'A strategy'
    interest_in_event_description = 'A description'
    is_in_contact_with_tcp = True
    tcp_name = 'A TCP name'
    tcp_email = 'tcp@test.com'
    tcp_mobile_number = '+447777777777'
    is_intending_to_exhibit_as_tcp_stand = True
    stand_trade_name = 'A Name'
    trade_show_experience_description = 'A description'
    additional_guidance = 'Some addition guidance'
    application_summary = [
        {
            'heading': f'Heading {heading}',
            'rows': [{
                'key': f'Question {row}',
                'value': f'Answer {row}',
                'action': {
                    'text': f'Action {row}',
                    'url': f'/action-url-{row}',
                }
            } for row in range(3)],
        } for heading in range(3)
    ]
