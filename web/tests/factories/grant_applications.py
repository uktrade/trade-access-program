from datetime import timedelta

import factory
from dateutil.utils import today

from web.grant_applications.models import GrantApplication


class GrantApplicationFactory(factory.DjangoModelFactory):
    class Meta:
        model = GrantApplication

    duns_number = 239896579
    applicant_full_name = factory.Sequence(lambda n: f'name-{n}')
    applicant_email = factory.Sequence(lambda n: f'test{n}@test.com')
    event = factory.SubFactory('web.tests.factories.events.EventFactory')
    is_already_committed_to_event = True
    is_intending_on_other_financial_support = True
    has_previously_applied = True
    previous_applications = 1
    is_first_exhibit_at_event = True
    number_of_times_exhibited_at_event = 0
    goods_and_services_description = factory.Sequence(lambda n: f'description-{n}')
    business_name_at_exhibit = factory.Sequence(lambda n: f'name-{n}')
    turnover = 1000
    number_of_employees = 1
    sector = factory.Sequence(lambda n: f'sector-{n}')
    website = factory.Sequence(lambda n: f'www.website-{n}.com')
    has_exported_before = False
    is_planning_to_grow_exports = True
    is_seeking_export_opportunities = True
    has_received_de_minimis_aid = False
    de_minimis_aid_public_authority = factory.Sequence(lambda n: f'authority-{n}')
    de_minimis_aid_date_awarded = factory.Sequence(lambda n: today() + timedelta(n))
    de_minimis_aid_amount = 1
    de_minimis_aid_description = factory.Sequence(lambda n: f'description-{n}')
    de_minimis_aid_recipient = factory.Sequence(lambda n: f'recipient-{n}')
    de_minimis_aid_date_received = factory.Sequence(lambda n: today() + timedelta(n))
    application_summary = [{
        'key': f'Question {n}',
        'value': f'Answer {n}',
        'action': {'text': f'Action {n}', 'url': f'/action-url-{n}'}
    } for n in range(10)]
