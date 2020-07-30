from django.db import models

from web.core.abstract_models import BaseMetaModel


class GrantApplication(BaseMetaModel):
    duns_number = models.IntegerField()
    applicant_full_name = models.CharField(null=True, max_length=500)
    applicant_email = models.EmailField(null=True)
    event = models.TextField(null=True)
    is_already_committed_to_event = models.BooleanField(null=True)
    is_intending_on_other_financial_support = models.BooleanField(null=True)
