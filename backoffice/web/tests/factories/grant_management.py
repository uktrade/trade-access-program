import factory

from web.grant_management.models import GrantManagementProcess


class GrantManagementProcessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantManagementProcess

    grant_application = factory.SubFactory(
        'web.tests.factories.grant_applications.GrantApplicationFactory'
    )
    previous_applications_is_verified = True
    event_commitment_is_verified = True
    business_entity_is_verified = True
    state_aid_is_verified = True
    decision = None
