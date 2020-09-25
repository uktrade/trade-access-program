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
