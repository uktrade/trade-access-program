import factory

from web.apply.models import ApplicationProcess


class ApplicationProcessFactory(factory.DjangoModelFactory):
    class Meta:
        model = ApplicationProcess
