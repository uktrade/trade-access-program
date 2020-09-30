from django.db import models
from django.db.models import PROTECT

from web.core.abstract_models import BaseMetaModel


class Company(BaseMetaModel):
    duns_number = models.IntegerField(unique=True)
    name = models.CharField(max_length=500)

    class Meta:
        verbose_name_plural = 'companies'

    @property
    def last_dnb_get_company_response(self):
        return self.dnb_get_company_responses.order_by('-created').first()


class DnbGetCompanyResponse(BaseMetaModel):
    company = models.ForeignKey(
        Company, on_delete=PROTECT, null=True, related_name='dnb_get_company_responses'
    )
    data = models.JSONField()

    @property
    def company_registration_number(self):
        registration_numbers = self.data.get('registration_numbers') or []
        reg_number_list = [
            r for r in registration_numbers
            if r['registration_type'] == 'uk_companies_house_number'
        ]
        reg_number = reg_number_list[0]['registration_number'] if reg_number_list else None
        return reg_number

    @property
    def company_address(self):
        return ', '.join(
            [v for k, v in self.data.items() if k.startswith('address_') and v]
        ) or None
