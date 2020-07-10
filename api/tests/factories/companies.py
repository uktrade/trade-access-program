import factory

from api.companies.models import Company
from api.tests.factories.base import BaseMetaFactory


class CompanyFactory(BaseMetaFactory):
    class Meta:
        model = Company

    dnb_service_duns_number = factory.Sequence(lambda n: n)
