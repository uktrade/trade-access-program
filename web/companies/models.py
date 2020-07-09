from django.db import models

from web.core.abstract_models import BaseMetaModel


class Company(BaseMetaModel):
    dnb_service_duns_number = models.IntegerField(unique=True)

    class Meta:
        verbose_name_plural = 'Companies'
