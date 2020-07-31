from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from web.core.abstract_models import BaseMetaModel


class GrantApplication(BaseMetaModel):
    duns_number = models.IntegerField()
    applicant_full_name = models.CharField(null=True, max_length=500)
    applicant_email = models.EmailField(null=True)
    event = models.TextField(null=True)
    is_already_committed_to_event = models.BooleanField(null=True)
    is_intending_on_other_financial_support = models.BooleanField(null=True)
    has_previously_applied = models.BooleanField(null=True)
    previous_applications = models.IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(6)]
    )
    is_first_exhibit_at_event = models.BooleanField(null=True)
    number_of_times_exhibited_at_event = models.IntegerField(
        null=True, validators=[MinValueValidator(0)]
    )
