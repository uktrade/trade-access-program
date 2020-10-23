from django import forms
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField

from web.core import widgets
from web.core.forms import MaxAllowedCharField, FORM_MSGS
from web.core.utils import str_to_bool
from web.grant_applications.form_mixins import FormatLabelMixin
from web.grant_applications.models import GrantApplicationLink
from web.grant_applications.services import (
    BackofficeService, BackofficeServiceException, get_sector_select_choices,
    get_trade_event_filter_choices, get_trade_event_filter_by_month_choices,
    generate_company_select_options, generate_trade_event_select_options
)


class EmptyGrantApplicationLinkForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = []


class PreviousApplicationsForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['previous_applications']

    previous_applications = forms.TypedChoiceField(
        empty_value=None,
        coerce=int,
        choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, '6 or more')],
        widget=widgets.RadioSelect(),
        label=_('How many grants have you received from TAP since April 1st 2009?'),
    )


class SearchCompanyForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['search_term']

    search_term = forms.CharField(
        label=_('Look up your company'),
        help_text=_('Enter a company name'),
        widget=forms.TextInput(
            attrs={
                'class': 'govuk-input govuk-!-width-two-thirds',
                'placeholder': 'Search...',
            }
        )
    )


class SelectCompanyForm(forms.ModelForm):

    def __init__(self, companies, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.companies = companies
        company_options = generate_company_select_options(companies)
        self.fields['duns_number'].choices = company_options['choices']
        self.fields['duns_number'].widget.attrs['hints'] = company_options['hints']

    class Meta:
        model = GrantApplicationLink
        fields = ['duns_number']

    duns_number = forms.ChoiceField(
        label=_('We found the following matches:'),
        widget=widgets.RadioSelect(),
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data:
            searched_company = next(
                c for c in self.companies
                if c['dnb_data']['duns_number'] == self.cleaned_data['duns_number']
            )
            try:
                company = BackofficeService().get_or_create_company(
                    duns_number=self.cleaned_data['duns_number'],
                    registration_number=searched_company['registration_number'],
                    name=searched_company['dnb_data']['primary_name']
                )
                cleaned_data['company'] = company['id']
            except BackofficeServiceException:
                raise forms.ValidationError(FORM_MSGS['resubmit'])
        return cleaned_data


class BusinessDetailsForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['is_based_in_uk', 'number_of_employees', 'is_turnover_greater_than']

    class NumberOfEmployees(TextChoices):
        HAS_FEWER_THAN_10 = 'fewer-than-10', _('Fewer than 10')
        HAS_10_TO_49 = '10-to-49', _('10 to 49')
        HAS_50_TO_249 = '50-to-249', _('50 to 249')
        HAS_250_OR_MORE = '250-or-more', _('250 or More')

    is_based_in_uk = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_('Is your business based in the UK?')
    )
    number_of_employees = forms.ChoiceField(
        choices=NumberOfEmployees.choices,
        widget=widgets.RadioSelect(),
        label=_('How many employees are currently on your payroll in the UK, across all sites?')
    )
    is_turnover_greater_than = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_(
            'Was your turnover in the last fiscal year greater than €50m or your balance sheet '
            '(or Statement of Financial Position) greater than €43m?'
        )
    )


class FindAnEventForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['filter_by_name', 'filter_by_sector', 'filter_by_country', 'filter_by_month']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['filter_by_month'].choices = get_trade_event_filter_by_month_choices()
        self.fields['filter_by_country'].choices = get_trade_event_filter_choices('country')
        self.fields['filter_by_sector'].choices = get_trade_event_filter_choices('sector')

    filter_by_name = forms.CharField(
        required=False,
        label=_('Event name'),
        help_text=_('You can leave this blank if you prefer'),
        widget=forms.TextInput(
            attrs={
                'class': 'govuk-input govuk-grid-column-full',
                'placeholder': 'Search...',
            }
        )
    )
    filter_by_sector = forms.ChoiceField(
        required=False,
        label=_('Sector'),
        widget=forms.Select(
            attrs={'class': 'govuk-select govuk-grid-column-full'}
        )
    )
    filter_by_country = forms.ChoiceField(
        required=False,
        label=_('Location'),
        widget=forms.Select(
            attrs={'class': 'govuk-select govuk-grid-column-full'}
        )
    )
    filter_by_month = forms.ChoiceField(
        required=False,
        label=_('Start date'),
        widget=forms.Select(
            attrs={'class': 'govuk-select'}
        )
    )


class SelectAnEventForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = [
            'filter_by_name', 'filter_by_sector', 'filter_by_country', 'filter_by_month',
            'event'
        ]

    def __init__(self, trade_events, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['filter_by_month'].choices = get_trade_event_filter_by_month_choices()
        self.fields['filter_by_country'].choices = get_trade_event_filter_choices('country')
        self.fields['filter_by_sector'].choices = get_trade_event_filter_choices('sector')
        trade_events_options = generate_trade_event_select_options(trade_events)
        self.fields['event'].choices = trade_events_options['choices']
        self.fields['event'].widget.attrs['hints'] = trade_events_options['hints']

    filter_by_name = forms.CharField(
        required=False,
        label=_('Event name'),
        widget=forms.TextInput(
            attrs={'class': 'govuk-input govuk-grid-column-full'}
        )
    )
    filter_by_sector = forms.ChoiceField(
        required=False,
        label=_('Sector'),
        widget=forms.Select(
            attrs={'class': 'govuk-select govuk-grid-column-full'}
        )
    )
    filter_by_country = forms.ChoiceField(
        required=False,
        label=_('Location'),
        widget=forms.Select(
            attrs={'class': 'govuk-select govuk-grid-column-full'}
        )
    )
    filter_by_month = forms.ChoiceField(
        required=False,
        label=_('Start date'),
        widget=forms.Select(
            attrs={'class': 'govuk-select govuk-grid-column-full'}
        )
    )
    event = forms.ChoiceField(
        label=_('What event are you intending to exhibit at'),
        widget=widgets.RadioSelect(),
    )


class EventFinanceForm(FormatLabelMixin, forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = [
            'is_already_committed_to_event', 'is_intending_on_other_financial_support',
            'has_received_de_minimis_aid'
        ]

    is_already_committed_to_event = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(
            attrs={
                'details': {
                    'summary_text': 'What do we mean by committed?',
                    'text': 'TODO',  # TODO: Content needed
                }
            }
        ),
        label=_('Have you already committed to purchasing exhibition space for {event_name}?'),
    )
    is_intending_on_other_financial_support = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(
            attrs={
                'details': {
                    'summary_text': 'Examples of financial support and costs',
                    'text': 'TODO',  # TODO: Content needed
                }
            }
        ),
        label=_('Will you receive or are you applying for any other financial support '
                'to exhibit at this event?')
    )
    has_received_de_minimis_aid = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        required=True,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(
            attrs={
                'details': {
                    'summary_text': 'What is de minimis aid?',
                    'text': 'TODO',  # TODO: Content needed
                }
            }
        ),
        label=_('Have you received over €200,000 de minimis aid during the last 3 fiscal years?')
    )

    def format_field_labels(self):
        self.format_label('is_already_committed_to_event', event_name=self.data['event'])


class AboutYouForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = [
            'applicant_full_name', 'applicant_email', 'applicant_mobile_number',
            'applicant_position_within_business'
        ]

    applicant_full_name = forms.CharField(
        label=_('Full name'),
        widget=forms.TextInput(
            attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
        )
    )
    applicant_email = forms.CharField(
        label=_('Email address'),
        widget=forms.TextInput(
            attrs={
                'class': 'govuk-input govuk-!-width-two-thirds',
                'type': 'email',
            }
        )
    )
    applicant_mobile_number = PhoneNumberField(
        label=_('Mobile number'),
        region='GB',
        widget=forms.TextInput(
            attrs={'class': 'govuk-input govuk-input--width-10'}
        )
    )
    applicant_position_within_business = forms.ChoiceField(
        label=_('What is your position within the business?'),
        choices=[
            ('director', 'Director'), ('company-secretary', 'Company secretary'),
            ('owner', 'Owner'), ('other', 'Other')
        ],
        widget=widgets.RadioSelect()
    )

    def clean(self):
        cleaned_data = super().clean()
        if 'applicant_mobile_number' in cleaned_data:
            cleaned_data['applicant_mobile_number'] = \
                cleaned_data['applicant_mobile_number'].as_e164
        return cleaned_data


class BusinessInformationForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['goods_and_services_description', 'other_business_names', 'sector']

    def __init__(self, *args, **kwargs):
        sector_choices = get_sector_select_choices()
        super().__init__(*args, **kwargs)
        self.fields['sector'].choices = sector_choices

    goods_and_services_description = MaxAllowedCharField(
        label=_('Describe your main products and services'),
        help_text=_(
            'If possible include any advantages they offer over competitors in overseas markets'
        ),
        max_length=200,
        widget=widgets.CharacterCountTextArea(
            attrs={
                'class': 'govuk-textarea govuk-js-character-count govuk-!-width-two-thirds',
                'rows': 3,
                'counter': 200
            }
        )
    )
    other_business_names = forms.CharField(
        required=False,
        empty_value=None,
        label=_('Business names'),
        help_text=_(
            'Add any brand or trading names used in addition to the registered company name'
        ),
        widget=forms.TextInput(
            attrs={
                'class': 'govuk-input govuk-!-width-two-thirds',
                'optional': True
            }
        )
    )
    sector = forms.ChoiceField(
        label=_('Industry sector'),
        widget=forms.Select(
            attrs={'class': 'govuk-select govuk-!-width-two-thirds'}
        )
    )


class EventIntentionForm(FormatLabelMixin, forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = [
            'is_first_exhibit_at_event', 'number_of_times_exhibited_at_event',
        ]

    is_first_exhibit_at_event = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_("Is this the first time you intend to exhibit at {event_name}?")
    )

    number_of_times_exhibited_at_event = forms.IntegerField(
        required=False,
        min_value=0,
        label=_("How many times have you exhibited at this {event_name} previously?"),
        widget=forms.NumberInput(
            attrs={'class': 'govuk-input govuk-!-width-one-quarter'}
        )
    )

    def format_field_labels(self):
        self.format_label('is_first_exhibit_at_event', event_name=self.data['event'])
        self.format_label('number_of_times_exhibited_at_event', event_name=self.data['event'])

    def clean(self):
        cleaned_data = super().clean()
        is_first_exhibit_at_event = cleaned_data.get('is_first_exhibit_at_event')
        number_of_times_exhibited_at_event = cleaned_data.get('number_of_times_exhibited_at_event')

        if not is_first_exhibit_at_event and number_of_times_exhibited_at_event is None:
            self.add_error(
                'number_of_times_exhibited_at_event',
                forms.ValidationError(FORM_MSGS['required'])
            )
        return cleaned_data


class ExportExperienceForm(forms.ModelForm):

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


class StateAidForm(forms.ModelForm):

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
                msg = forms.ValidationError(FORM_MSGS['required'])
                self.add_error(field, msg)
        return cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        # TODO - Fix this view now that has_received_de_minimis_aid was moved to a previous view
        #        in a previous commit
        has_received_de_minimis_aid = cleaned_data.get('has_received_de_minimis_aid')

        if has_received_de_minimis_aid is True:
            cleaned_data = self.mark_fields_required(
                cleaned_data, 'de_minimis_aid_public_authority', 'de_minimis_aid_date_awarded',
                'de_minimis_aid_amount', 'de_minimis_aid_description', 'de_minimis_aid_recipient',
                'de_minimis_aid_date_received'
            )

        return cleaned_data
