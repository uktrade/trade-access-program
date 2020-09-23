from django import forms
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from web.core import widgets
from web.core.widgets import CurrencyInput
from web.grant_applications.models import GrantApplicationLink
from web.grant_applications.services import (
    BackofficeService, BackofficeServiceException, get_company_select_options,
    get_sector_select_options, get_trade_event_select_options
)


def str_to_bool(value):
    if str(value).lower() in ['true', 't', '1']:
        return True
    elif str(value).lower() in ['false', 'f', '0']:
        return False
    raise ValueError(f'Cannot convert {value} to boolean')


class SearchCompanyForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['search_term']

    search_term = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'class': 'govuk-input govuk-!-width-two-thirds',
                'placeholder': 'Search...',
            }
        )
    )


class SelectCompanyForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        search_term = getattr(kwargs.get('instance'), 'search_term', None)
        company_options = get_company_select_options(search_term)
        super().__init__(*args, **kwargs)
        self.fields['duns_number'].choices = company_options['choices']
        self.fields['duns_number'].widget.attrs['hints'] = company_options['hints']

    class Meta:
        model = GrantApplicationLink
        fields = ['duns_number']

    duns_number = forms.ChoiceField(
        label=_('Dun and Bradstreet Number'),
        widget=widgets.RadioSelect(),
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data:
            service = BackofficeService()
            try:
                company = service.get_or_create_company(
                    duns_number=self.cleaned_data['duns_number'],
                    name=dict(self.fields['duns_number'].choices)[self.cleaned_data['duns_number']]
                )
                self.backoffice_grant_application = service.create_grant_application(
                    company_id=company['id'],
                    search_term=self.instance.search_term
                )
            except BackofficeServiceException:
                raise forms.ValidationError(
                    'An unexpected error occurred. Please resubmit the form.'
                )
        return cleaned_data

    def save(self, *args, **kwargs):
        self.instance.backoffice_grant_application_id = self.backoffice_grant_application['id']
        return super().save(*args, **kwargs)


class AboutYourBusinessForm(forms.ModelForm):
    class Meta:
        model = GrantApplicationLink
        fields = []


class UpdateBackofficeGrantApplicationMixin:

    def save(self, *args, **kwargs):
        BackofficeService().update_grant_application(
            grant_application_id=str(self.instance.backoffice_grant_application_id),
            **{k: v for k, v in self.cleaned_data.items() if v is not None}
        )
        return super().save(*args, **kwargs)


class AboutYouForm(UpdateBackofficeGrantApplicationMixin, forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['applicant_full_name', 'applicant_email']

    applicant_full_name = forms.CharField(
        label=_('Your full name'),
        widget=forms.TextInput(
            attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
        )
    )
    applicant_email = forms.CharField(
        label=_('Your email address'),
        widget=forms.TextInput(
            attrs={
                'class': 'govuk-input govuk-!-width-two-thirds',
                'type': 'email',
            }
        )
    )


class AboutTheEventForm(UpdateBackofficeGrantApplicationMixin, forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = [
            'event', 'is_already_committed_to_event', 'is_intending_on_other_financial_support'
        ]

    def __init__(self, *args, **kwargs):
        trade_event_options = get_trade_event_select_options()
        super().__init__(*args, **kwargs)
        self.fields['event'].choices = trade_event_options['choices']

    is_already_committed_to_event = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_('Have you already committed to attending this event?'),
    )

    is_intending_on_other_financial_support = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_('Will you receive or are you applying for any other '
                'financial support for this event?')
    )
    event = forms.ChoiceField(
        label=_('Select event'),
        widget=forms.Select(
            attrs={
                'class': 'govuk-select govuk-!-width-two-thirds',
                'placeholder': 'Select the event...',
            }
        ),
    )


class PreviousApplicationsForm(UpdateBackofficeGrantApplicationMixin, forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['has_previously_applied', 'previous_applications']

    has_previously_applied = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_('Is this the first time you have applied for a TAP grant?')
    )

    previous_applications = forms.TypedChoiceField(
        coerce=int,
        choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, '6 or more')],
        widget=widgets.RadioSelect(),
        label=_('How many TAP grants have you received since 1 April 2009?'),
    )


class EventIntentionForm(UpdateBackofficeGrantApplicationMixin, forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['is_first_exhibit_at_event', 'number_of_times_exhibited_at_event']

    is_first_exhibit_at_event = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_("Is this the first time you intend to exhibit at {event_name}?")
    )

    number_of_times_exhibited_at_event = forms.IntegerField(
        min_value=0,
        label=_("How many times have you exhibited at this {event_name} previously?"),
        widget=forms.NumberInput(
            attrs={'class': 'govuk-input govuk-!-width-one-quarter'}
        )
    )

    def format_label(self, field_name, **kwargs):
        self[field_name].label = self[field_name].label.format(**kwargs)

    def format_field_labels(self):
        self.format_label('is_first_exhibit_at_event', event_name=self.data['event'])
        self.format_label('number_of_times_exhibited_at_event', event_name=self.data['event'])


class BusinessInformationForm(UpdateBackofficeGrantApplicationMixin, forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = [
            'goods_and_services_description', 'business_name_at_exhibit', 'number_of_employees',
            'turnover', 'sector', 'website'
        ]

    class NumberOfEmployees(TextChoices):
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

    def __init__(self, *args, **kwargs):
        sector_options = get_sector_select_options()
        super().__init__(*args, **kwargs)
        self.fields['sector'].choices = sector_options['choices']

    goods_and_services_description = forms.CharField(
        label=_('Description of goods or services, and whether they are from UK origin'),
        widget=forms.Textarea(
            attrs={'class': 'govuk-textarea govuk-!-width-two-thirds'}
        )
    )
    business_name_at_exhibit = forms.CharField(
        label=_('Business name that you will use on the stand'),
        widget=forms.TextInput(
            attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
        )
    )
    number_of_employees = forms.ChoiceField(
        choices=NumberOfEmployees.choices,
        widget=widgets.RadioSelect(),
    )
    turnover = forms.IntegerField(widget=CurrencyInput())
    sector = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class': 'govuk-select govuk-!-width-two-thirds',
                'placeholder': 'Select your sector...',
            }
        )
    )
    website = forms.URLField(
        widget=forms.URLInput(
            attrs={
                'class': 'govuk-input govuk-!-width-two-thirds',
                'type': 'text'
            }
        )
    )


class ExportExperienceForm(UpdateBackofficeGrantApplicationMixin, forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = [
            'has_exported_before', 'is_planning_to_grow_exports', 'is_seeking_export_opportunities'
        ]

    has_exported_before = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_('Have you exported before?'),
    )

    is_planning_to_grow_exports = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_('Are you planning to grow your exports in up to six countries within '
                'the European Union or beyond?')
    )

    is_seeking_export_opportunities = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_('Are you actively investigating export opportunities for your business?')
    )


class StateAidForm(UpdateBackofficeGrantApplicationMixin, forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = [
            'has_received_de_minimis_aid',
            'de_minimis_aid_public_authority', 'de_minimis_aid_date_awarded',
            'de_minimis_aid_amount', 'de_minimis_aid_description', 'de_minimis_aid_recipient',
            'de_minimis_aid_date_received'
        ]

    has_received_de_minimis_aid = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        required=True,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_(
            'Have you received any de minimis aid (whether de minimis aid from or '
            'attributable to DIT or any other public authority) during the current and two '
            'previous Fiscal Years?'
        )
    )
    de_minimis_aid_public_authority = forms.CharField(
        required=False,
        empty_value=None,
        label=_('Authority'),
        widget=forms.TextInput(
            attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
        )
    )
    de_minimis_aid_date_awarded = forms.DateField(
        required=False,
        label=_('Date awarded'),
        widget=forms.widgets.SelectDateWidget(
            attrs={'class': 'govuk-date-input__item govuk-input govuk-input--width-4'},
        )
    )
    de_minimis_aid_amount = forms.IntegerField(
        required=False,
        label=_('Total amount of aid'),
        widget=forms.NumberInput(
            attrs={'class': 'govuk-input govuk-!-width-one-quarter'}
        ),
        validators=[MinValueValidator(1)]
    )
    de_minimis_aid_description = forms.CharField(
        required=False,
        empty_value=None,
        label=_('Description of aid'),
        widget=forms.Textarea(
            attrs={'class': 'govuk-textarea govuk-!-width-two-thirds'}
        )
    )
    de_minimis_aid_recipient = forms.CharField(
        required=False,
        empty_value=None,
        label=_('Recipient'),
        widget=forms.TextInput(
            attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
        )
    )
    de_minimis_aid_date_received = forms.DateField(
        required=False,
        label=_('Date of received aid'),
        widget=forms.widgets.SelectDateWidget(
            attrs={'class': 'govuk-date-input__item govuk-input govuk-input--width-4'},
        )
    )

    def mark_fields_required(self, cleaned_data, *fields):
        """Used for conditionally marking many fields as required."""
        for field in fields:
            if cleaned_data.get(field) is None:
                msg = forms.ValidationError('This field is required.')
                self.add_error(field, msg)
        return cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        has_received_de_minimis_aid = cleaned_data.get('has_received_de_minimis_aid')

        if has_received_de_minimis_aid is True:
            cleaned_data = self.mark_fields_required(
                cleaned_data, 'de_minimis_aid_public_authority', 'de_minimis_aid_date_awarded',
                'de_minimis_aid_amount', 'de_minimis_aid_description', 'de_minimis_aid_recipient',
                'de_minimis_aid_date_received'
            )

        return cleaned_data


class ApplicationReviewForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = []
