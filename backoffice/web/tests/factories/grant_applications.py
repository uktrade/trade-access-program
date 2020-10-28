from datetime import timedelta
from decimal import Decimal

import factory
from dateutil.utils import today

from web.grant_applications.models import GrantApplication


class GrantApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantApplication

    search_term = factory.Sequence(lambda n: f'search_term-{n}')
    company = factory.SubFactory('web.tests.factories.companies.CompanyFactory')
    applicant_full_name = factory.Sequence(lambda n: f'name-{n}')
    applicant_email = factory.Sequence(lambda n: f'test{n}@test.com')
    applicant_mobile_number = factory.Sequence(lambda n: f'+44{n:011}')
    job_title = 'director'
    event = factory.SubFactory('web.tests.factories.events.EventFactory')
    is_already_committed_to_event = True
    previous_applications = 1
    is_first_exhibit_at_event = True
    number_of_times_exhibited_at_event = 0
    products_and_services_description = factory.Sequence(lambda n: f'description-{n}')
    business_name_at_exhibit = factory.Sequence(lambda n: f'name-{n}')
    other_business_names = factory.Sequence(lambda n: f'other-business-names-{n}')
    previous_years_turnover_1 = Decimal('1.23')
    previous_years_turnover_2 = Decimal('1.23')
    previous_years_turnover_3 = Decimal('0.00')
    previous_years_export_turnover_1 = Decimal('1.23')
    previous_years_export_turnover_2 = Decimal('1.23')
    previous_years_export_turnover_3 = Decimal('0.00')
    products_and_services_competitors = factory.Sequence(lambda n: f'description-{n}')
    number_of_employees = GrantApplication.NumberOfEmployees.HAS_FEWER_THAN_10
    sector = factory.SubFactory('web.tests.factories.sector.SectorFactory')
    website = factory.Sequence(lambda n: f'www.website-{n}.com')
    has_exported_before = False
    is_planning_to_grow_exports = True
    is_seeking_export_opportunities = True
    de_minimis_aid_public_authority = factory.Sequence(lambda n: f'authority-{n}')
    de_minimis_aid_date_awarded = factory.Sequence(lambda n: today() + timedelta(n))
    de_minimis_aid_amount = 1
    de_minimis_aid_description = factory.Sequence(lambda n: f'description-{n}')
    de_minimis_aid_recipient = factory.Sequence(lambda n: f'recipient-{n}')
    de_minimis_aid_date_received = factory.Sequence(lambda n: today() + timedelta(n))
    application_summary = [{
        'heading': 'About you',
        'summary': [{
            'key': f'Question {n}',
            'value': f'Answer {n}',
            'action': {
                'text': f'Action {n}',
                'url': f'/action-url-{n}',
            }
        }],
    } for n in range(10)]
