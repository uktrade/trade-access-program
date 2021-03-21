from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models import PROTECT
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from web.core.abstract_models import BaseMetaModel
from web.grant_management.flows import GrantManagementFlow
from web.grant_management.models import GrantManagementProcess


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

    class ExportRegions(models.TextChoices):
        AFRICA = 'africa', 'Africa'
        ASIA_PACIFIC = 'asia pacific', 'Asia-Pacific'
        CHINA = 'china', 'China'
        EASTERN_EUROPE_AND_CENTRAL_ASIA = \
            'eastern europe and central asia', 'Eastern Europe and Central Asia'
        EUROPE = 'europe', 'Europe'
        LATIN_AMERICA = 'latin america', 'Latin America'
        MIDDLE_EAST = 'middle east', 'Middle East'
        NORTH_AMERICA = 'north america', 'North America'
        SOUTH_ASIA = 'south asia', 'South Asia'

    class MarketsIntendingOnExportingTo(models.TextChoices):
        Existing = 'existing', 'existing markets'
        New = 'new', 'new markets not exported to in the last 12 months'

    class CompanyType(models.TextChoices):
        LIMITED_COMPANY = 'limited company', _('Limited company')
        PARTNERSHIP = 'partnership', _('Partnership')
        SOLE_TRADER = 'sole trader', _('Sole trader')
        OTHER = 'other', _('Other e.g. charity, university, publicly funded body')

    class TimeTradingInUk(models.TextChoices):
        LESS_THAN_1_YEAR = 'less than 1 year', _('Less than 1 year')
        TWO_TO_FIVE_YEARS = '2 to 5 years', _('2 to 5 years')
        SIX_TO_TEN_YEARS = '6 to 10 years', _('6 to 10 years')
        MORE_THAN_10_YEARS = 'more than 10 years', _('More than 10 years')

    previous_applications = models.IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(6)]
    )
    event = models.ForeignKey('trade_events.Event', on_delete=PROTECT, null=True)
    event_evidence_upload = models.ForeignKey('core.Image', on_delete=PROTECT, null=True)
    is_already_committed_to_event = models.BooleanField(null=True)
    search_term = models.CharField(max_length=500, null=True)
    company = models.ForeignKey('companies.Company', on_delete=PROTECT, null=True)
    manual_company_type = models.CharField(null=True, choices=CompanyType.choices, max_length=20)
    manual_company_name = models.CharField(null=True, max_length=500)
    manual_company_address_line_1 = models.CharField(null=True, max_length=100)
    manual_company_address_line_2 = models.CharField(null=True, max_length=100)
    manual_company_address_town = models.CharField(null=True, max_length=100)
    manual_company_address_county = models.CharField(null=True, max_length=100)
    manual_company_address_postcode = models.CharField(null=True, max_length=10)
    manual_time_trading_in_uk = models.CharField(
        null=True, choices=TimeTradingInUk.choices, max_length=20
    )
    manual_registration_number = models.CharField(
        null=True, validators=[RegexValidator(regex=r'(SC|NI|[0-9]{2})[0-9]{6}')], max_length=10
    )
    manual_vat_number = models.CharField(
        null=True, max_length=10,
        validators=[RegexValidator(regex=r'([0-9]{9}([0-9]{3})?|[A-Z]{2}[0-9]{3})')]
    )
    manual_website = models.URLField(null=True, max_length=500)
    number_of_employees = models.CharField(
        null=True, choices=NumberOfEmployees.choices, max_length=20
    )
    is_turnover_greater_than = models.BooleanField(null=True)
    applicant_full_name = models.CharField(null=True, max_length=500)
    applicant_email = models.EmailField(null=True)
    applicant_mobile_number = PhoneNumberField(null=True, region='GB')
    job_title = models.CharField(null=True, max_length=500)
    previous_years_turnover_1 = models.DecimalField(
        null=True, validators=[MinValueValidator(0)], **settings.CURRENCY_DECIMAL_PRECISION
    )
    previous_years_turnover_2 = models.DecimalField(
        null=True, validators=[MinValueValidator(0)], **settings.CURRENCY_DECIMAL_PRECISION
    )
    previous_years_turnover_3 = models.DecimalField(
        null=True, validators=[MinValueValidator(0)], **settings.CURRENCY_DECIMAL_PRECISION
    )
    previous_years_export_turnover_1 = models.DecimalField(
        null=True, validators=[MinValueValidator(0)], **settings.CURRENCY_DECIMAL_PRECISION
    )
    previous_years_export_turnover_2 = models.DecimalField(
        null=True, validators=[MinValueValidator(0)], **settings.CURRENCY_DECIMAL_PRECISION
    )
    previous_years_export_turnover_3 = models.DecimalField(
        null=True, validators=[MinValueValidator(0)], **settings.CURRENCY_DECIMAL_PRECISION
    )
    sector = models.ForeignKey('sectors.Sector', on_delete=PROTECT, null=True)
    other_business_names = models.CharField(null=True, max_length=500)
    products_and_services_description = models.TextField(null=True)
    products_and_services_competitors = models.TextField(null=True)
    has_exported_before = models.BooleanField(null=True)
    has_product_or_service_for_export = models.BooleanField(null=True)
    has_exported_in_last_12_months = models.BooleanField(null=True)
    export_regions = ArrayField(
        models.CharField(max_length=50, choices=ExportRegions.choices), null=True
    )
    markets_intending_on_exporting_to = ArrayField(
        models.CharField(max_length=10, choices=MarketsIntendingOnExportingTo.choices), null=True
    )
    is_in_contact_with_dit_trade_advisor = models.BooleanField(null=True)
    ita_name = models.CharField(null=True, max_length=500)
    ita_email = models.EmailField(null=True)
    ita_mobile_number = PhoneNumberField(null=True, region='GB')
    export_experience_description = models.TextField(null=True)
    export_strategy = models.TextField(null=True)
    interest_in_event_description = models.TextField(null=True)
    is_event_evidence_requested = models.BooleanField(default=False)
    is_event_evidence_uploaded = models.BooleanField(default=False)
    is_event_evidence_approved = models.BooleanField(default=False)
    is_in_contact_with_tcp = models.BooleanField(null=True)
    tcp_name = models.CharField(null=True, max_length=500)
    tcp_email = models.EmailField(null=True)
    tcp_mobile_number = PhoneNumberField(null=True, region='GB')
    is_intending_to_exhibit_as_tcp_stand = models.BooleanField(null=True)
    stand_trade_name = models.CharField(null=True, max_length=500)
    trade_show_experience_description = models.TextField(null=True)
    additional_guidance = models.TextField(null=True)
    application_summary = models.JSONField(default=list)

    def send_for_review(self):
        qs = GrantManagementFlow.process_class.objects.filter(grant_application=self)
        if not qs.exists():
            return GrantManagementFlow.start.run(grant_application=self)
        return qs.get()

    @property
    def is_eligible(self):
        if self.previous_applications and self.previous_applications >= 6:
            return False
        if self.is_already_committed_to_event is True:
            return False
        if self.number_of_employees == self.NumberOfEmployees.HAS_250_OR_MORE:
            return False
        if self.is_turnover_greater_than is True:
            return False
        return True

    @property
    def sent_for_review(self):
        return hasattr(self, 'grant_management_process')

    @property
    def company_name(self):
        return self.manual_company_name or self.company.name

    @property
    def flow_process(self):
        return GrantManagementProcess.objects.get(grant_application_id=self.id)


class StateAid(BaseMetaModel):
    authority = models.CharField(max_length=500)
    date_received = models.DateField()
    amount = models.IntegerField(validators=[MinValueValidator(1)])
    description = models.CharField(max_length=2000)
    grant_application = models.ForeignKey(GrantApplication, on_delete=PROTECT)
