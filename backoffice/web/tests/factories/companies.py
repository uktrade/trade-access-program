import factory

from web.companies.models import Company, DnbGetCompanyResponse
from web.tests.external_api_responses import FAKE_DNB_SEARCH_COMPANIES
from web.tests.factories.base import BaseMetaFactory


class CompanyFactory(BaseMetaFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: f'name-{n}')
    duns_number = factory.Sequence(lambda n: str(n))
    registration_number = factory.Sequence(lambda n: str(n))
    dnb_get_company_responses = factory.RelatedFactory(
        'web.tests.factories.companies.DnbGetCompanyResponseFactory',
        factory_related_name='company'
    )


class DnbGetCompanyResponseFactory(BaseMetaFactory):
    class Meta:
        model = DnbGetCompanyResponse

    company = factory.SubFactory(CompanyFactory)
    dnb_data = FAKE_DNB_SEARCH_COMPANIES['results'][0]
