import uuid

import factory

from web.grant_applications.models import GrantApplicationLink


class GrantApplicationLinkFactory(factory.DjangoModelFactory):
    class Meta:
        model = GrantApplicationLink

    search_term = factory.Sequence(lambda n: f'search-term-{n}')
    backoffice_grant_application_id = factory.LazyFunction(uuid.uuid4)
    sent_for_review = False
