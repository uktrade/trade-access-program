import factory

from web.grant_management.models import GrantApplicationProcess


class ApplicationProcessFactory(factory.DjangoModelFactory):
    class Meta:
        model = GrantApplicationProcess
