import factory

from web.companies.models import Company
from web.tests.factories.base import BaseMetaFactory


class CompanyFactory(BaseMetaFactory):
    class Meta:
        model = Company

    dnb_service_duns_number = 239896579
    name = factory.Sequence(lambda n: f'name-{n}')
