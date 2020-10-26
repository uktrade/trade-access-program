import uuid

import factory

from web.grant_applications.models import GrantApplicationLink


class GrantApplicationLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantApplicationLink

    backoffice_grant_application_id = factory.LazyFunction(uuid.uuid4)
    sent_for_review = False
