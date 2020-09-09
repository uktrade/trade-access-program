import factory

from web.grant_management.models import GrantManagementProcess


class GrantManagementProcessFactory(factory.DjangoModelFactory):
    class Meta:
        model = GrantManagementProcess

    grant_application = factory.SubFactory(
        'web.tests.factories.grant_applications.GrantApplicationFactory'
    )
    employee_count_is_verified = False
    turnover_is_verified = False
    decision = None
