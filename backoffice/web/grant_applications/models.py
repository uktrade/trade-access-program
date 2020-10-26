from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import PROTECT
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from web.core.abstract_models import BaseMetaModel
from web.grant_management.flows import GrantManagementFlow


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

    class ApplicantPositionWithinBusiness(models.TextChoices):
        DIRECTOR = 'director', _('Director')
        COMPANY_SECRETARY = 'company-secretary', _('Company Secretary')
        OWNER = 'owner', _('Owner')
        OTHER = 'other', _('Other')

    search_term = models.CharField(max_length=500, null=True)
    is_based_in_uk = models.BooleanField(null=True)
    is_turnover_greater_than = models.BooleanField(null=True)
    company = models.ForeignKey('companies.Company', on_delete=PROTECT, null=True)
    applicant_full_name = models.CharField(null=True, max_length=500)
    applicant_email = models.EmailField(null=True)
    applicant_mobile_number = PhoneNumberField(null=True, region='GB')
    applicant_position_within_business = models.CharField(
        null=True, choices=ApplicantPositionWithinBusiness.choices, max_length=20
    )
    event = models.ForeignKey('trade_events.Event', on_delete=PROTECT, null=True)
    is_already_committed_to_event = models.BooleanField(null=True)
    is_intending_on_other_financial_support = models.BooleanField(null=True)
    previous_applications = models.IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(6)]
    )
    is_first_exhibit_at_event = models.BooleanField(null=True)
    number_of_times_exhibited_at_event = models.IntegerField(
        null=True, validators=[MinValueValidator(0)]
    )
    goods_and_services_description = models.TextField(null=True)
    business_name_at_exhibit = models.CharField(null=True, max_length=500)
    other_business_names = models.CharField(null=True, max_length=500)
    turnover = models.IntegerField(null=True, validators=[MinValueValidator(0)])
    number_of_employees = models.CharField(
        null=True, choices=NumberOfEmployees.choices, max_length=20
    )
    sector = models.ForeignKey('sectors.Sector', on_delete=PROTECT, null=True)
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
    application_summary = models.JSONField(default=list)

    def send_for_review(self):
        return GrantManagementFlow.start.run(grant_application=self)

    @property
    def answers(self):
        _answers = []
        for summary in self.application_summary:
            _answers += [[row['key'], row['value']] for row in summary['summary']]
        return _answers
