import factory

from web.grant_management.models import GrantManagementProcess


class ApplicationProcessFactory(factory.DjangoModelFactory):
    class Meta:
        model = GrantManagementProcess
