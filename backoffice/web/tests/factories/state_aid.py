from datetime import timedelta

import factory
from dateutil.utils import today

from web.grant_applications.models import StateAid


class StateAidFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StateAid

    authority = factory.Sequence(lambda n: f'authority-{n}')
    date_received = factory.Sequence(lambda n: today().date() - timedelta(days=n))
    amount = 1000
    description = factory.Sequence(lambda n: f'description-{n}')
    grant_application = factory.SubFactory(
        'web.tests.factories.grant_applications.GrantApplicationFactory'
    )
