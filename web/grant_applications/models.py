from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import PROTECT
from django.utils.translation import gettext_lazy as _

from web.core.abstract_models import BaseMetaModel
from web.grant_management.flows import GrantManagementFlow


def sector_code_validator(value):
    _raise = False

    if value[:2] != 'SL':
        _raise = True

    try:
        int(value[2:])
    except ValueError:
        _raise = True

    if _raise:
        raise ValidationError('%(value)s must have format SL0000', params={'value': value})


class Sector(BaseMetaModel):
    sector_code = models.CharField(max_length=6, validators=[sector_code_validator])
    name = models.CharField(max_length=500)
    cluster_name = models.CharField(max_length=500)
    full_name = models.CharField(max_length=500)
    sub_sector_name = models.CharField(max_length=500, null=True)
    sub_sub_sector_name = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.full_name


class GrantApplication(BaseMetaModel):

    class NumberOfEmployees(models.TextChoices):
        HAS_FEWER_THAN_10 = 'fewer-than-10', _('Fewer than 10')
        HAS_10_TO_49 = '10-to-49', _('10 to 49')
        HAS_50_TO_249 = '50-to-249', _('50 to 249')
        HAS_250_OR_MORE = '250-or-more', _('250 or More')

        @classmethod
        def get_choice_by_number(cls, number_of_employees):
            if number_of_employees < 10:
                return cls.HAS_FEWER_THAN_10
            elif 10 <= number_of_employees <= 49:
                return cls.HAS_10_TO_49
            elif 50 <= number_of_employees <= 249:
                return cls.HAS_50_TO_249
            elif number_of_employees >= 250:
                return cls.HAS_250_OR_MORE

    search_term = models.CharField(max_length=500)
    company = models.ForeignKey('companies.Company', on_delete=PROTECT, null=True)
    applicant_full_name = models.CharField(null=True, max_length=500)
    applicant_email = models.EmailField(null=True)
    event = models.ForeignKey('trade_events.Event', on_delete=PROTECT, null=True)
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
    turnover = models.IntegerField(null=True, validators=[MinValueValidator(0)])
    number_of_employees = models.CharField(
        null=True, choices=NumberOfEmployees.choices, max_length=20
    )
    sector = models.ForeignKey(Sector, on_delete=PROTECT, null=True)
    website = models.URLField(null=True, max_length=500)
    has_exported_before = models.BooleanField(null=True)
    is_planning_to_grow_exports = models.BooleanField(null=True)
    is_seeking_export_opportunities = models.BooleanField(null=True)
    has_received_de_minimis_aid = models.BooleanField(null=True)
    de_minimis_aid_public_authority = models.CharField(null=True, blank=True, max_length=500)
    de_minimis_aid_date_awarded = models.DateField(null=True, blank=True)
    de_minimis_aid_amount = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(1)]
    )
    de_minimis_aid_description = models.CharField(null=True, blank=True, max_length=500)
    de_minimis_aid_recipient = models.CharField(null=True, blank=True, max_length=500)
    de_minimis_aid_date_received = models.DateField(null=True, blank=True)
    application_summary = JSONField(default=list)

    def send_for_review(self):
        return GrantManagementFlow.start.run(grant_application=self)

    @property
    def answers(self):
        _answers = []
        for summary in self.application_summary:
            _answers += [[row['key'], row['value']] for row in summary['summary']]
        return _answers
