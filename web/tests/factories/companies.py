import factory

from web.companies.models import Company
from web.tests.factories.base import BaseMetaFactory


class CompanyFactory(BaseMetaFactory):
    class Meta:
        model = Company

    dnb_service_duns_number = factory.Sequence(lambda n: n)
