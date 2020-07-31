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
    goods_and_services_description = models.TextField(null=True)
    business_name_at_exhibit = models.CharField(null=True, max_length=500)
    turnover = models.IntegerField(null=True, validators=[MinValueValidator(1)])
    number_of_employees = models.IntegerField(null=True, validators=[MinValueValidator(1)])
    sector = models.CharField(null=True, max_length=500)
    website = models.CharField(null=True, max_length=500)
    has_exported_before = models.BooleanField(null=True)
    is_planning_to_grow_exports = models.BooleanField(null=True)
    is_seeking_export_opportunities = models.BooleanField(null=True)
    has_received_de_minimis_aid = models.BooleanField(null=True)
    de_minimis_aid_public_authority = models.CharField(null=True, max_length=500)
    de_minimis_aid_date_awarded = models.DateField(null=True)
    de_minimis_aid_amount = models.IntegerField(null=True, validators=[MinValueValidator(1)])
    de_minimis_aid_description = models.CharField(null=True, max_length=500)
    de_minimis_aid_recipient = models.CharField(null=True, max_length=500)
    de_minimis_aid_date_received = models.DateField(null=True)
