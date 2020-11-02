from django import forms
from django.conf import settings
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField

from web.core import widgets
from web.core.forms import MaxAllowedCharField, FORM_MSGS, CurrencyField
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


class EventCommitmentForm(FormatLabelMixin, forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['is_already_committed_to_event']

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
        label=_(
            'Have you already committed to purchasing exhibition space for '
            '<strong>{event_name}</strong>?'
        ),
    )


class SearchCompanyForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['search_term']

    search_term = forms.CharField(
        label=_('Full business name'),
        min_length=2,
        help_text=_("For example 'My Business Limited'"),
        widget=forms.TextInput(
            attrs={'class': 'govuk-input hmcts-search__input', 'placeholder': 'Search...'}
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
        fields = ['search_term', 'duns_number']

    search_term = forms.CharField(
        required=False,
        min_length=2,
        label=_('Full business name'),
        help_text=_("For example 'My Business Limited'"),
        widget=forms.TextInput(
            attrs={'class': 'govuk-input hmcts-search__input', 'placeholder': 'Search...'}
        )
    )
    duns_number = forms.ChoiceField(label=_(''), widget=widgets.RadioSelect())

    def clean(self):
        cleaned_data = super().clean()
        if not self.errors and 'duns_number' in cleaned_data:
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


class CompanyDetailsForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['number_of_employees', 'is_turnover_greater_than']

    class NumberOfEmployees(TextChoices):
        HAS_FEWER_THAN_10 = 'fewer-than-10', _('Fewer than 10')
        HAS_10_TO_49 = '10-to-49', _('10 to 49')
        HAS_50_TO_249 = '50-to-249', _('50 to 249')
        HAS_250_OR_MORE = '250-or-more', _('250 or More')

    number_of_employees = forms.ChoiceField(
        choices=NumberOfEmployees.choices,
        widget=widgets.RadioSelect(),
        label=_('How many UK based employees does the business currently have?')
    )
    is_turnover_greater_than = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_(
            'Was your turnover greater than €50m, or your balance sheet '
            '(or Statement of Financial Position) greater than €43m, in the last fiscal year?'
        )
    )


class ContactDetailsForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = [
            'applicant_full_name', 'applicant_email', 'applicant_mobile_number', 'job_title'
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
    job_title = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        if 'applicant_mobile_number' in cleaned_data:
            cleaned_data['applicant_mobile_number'] = \
                cleaned_data['applicant_mobile_number'].as_e164
        return cleaned_data


class CompanyTradingDetailsForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = [
            'previous_years_turnover_1', 'previous_years_turnover_2', 'previous_years_turnover_3',
            'previous_years_export_turnover_1', 'previous_years_export_turnover_2',
            'previous_years_export_turnover_3', 'sector', 'other_business_names',
            'products_and_services_description', 'products_and_services_competitors'
        ]

    def __init__(self, *args, **kwargs):
        sector_choices = get_sector_select_choices()
        super().__init__(*args, **kwargs)
        self.fields['sector'].choices = sector_choices

    previous_years_turnover_1 = CurrencyField(label=_('Last year'))
    previous_years_turnover_2 = CurrencyField(label=_('Year 2'))
    previous_years_turnover_3 = CurrencyField(label=_('Year 3'))
    previous_years_export_turnover_1 = CurrencyField(label=_('Last year'))
    previous_years_export_turnover_2 = CurrencyField(label=_('Year 2'))
    previous_years_export_turnover_3 = CurrencyField(label=_('Year 3'))
    sector = forms.ChoiceField(
        label=_('Industry sector'),
        widget=forms.Select(attrs={'class': 'govuk-select'})
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
                'class': 'govuk-input',
                'optional': True
            }
        )
    )
    products_and_services_description = MaxAllowedCharField(
        label=_('Describe your main products and services'),
        max_length=2000,
        widget=widgets.CharacterCountTextArea(
            attrs={
                'class': 'govuk-textarea govuk-js-character-count',
                'rows': 7,
                'counter': 2000
            }
        )
    )
    products_and_services_competitors = MaxAllowedCharField(
        label=_(
            'Describe any advantages your products and services offer over competitors in '
            'overseas markets'
        ),
        max_length=2000,
        widget=widgets.CharacterCountTextArea(
            attrs={
                'class': 'govuk-textarea govuk-js-character-count',
                'rows': 7,
                'counter': 2000
            }
        )
    )


class ExportExperienceForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['has_exported_before', 'has_product_or_service_for_export']

    has_exported_before = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_('Has your business exported any products or services before?'),
    )
    has_product_or_service_for_export = forms.TypedChoiceField(
        required=False,
        empty_value=None,
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_(
            'Do you have a product or service suitable for, or that could be developed for, export?'
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        has_exported_before = cleaned_data.get('has_exported_before')
        has_product_or_service_for_export = cleaned_data.get('has_product_or_service_for_export')

        if has_exported_before is False and has_product_or_service_for_export is None:
            self.add_error(
                'has_product_or_service_for_export', forms.ValidationError(FORM_MSGS['required'])
            )

        if has_exported_before is True and has_product_or_service_for_export is not None:
            cleaned_data['has_product_or_service_for_export'] = None

        return cleaned_data


class ExportDetailsForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = [
            'has_exported_in_last_12_months', 'export_regions', 'markets_intending_on_exporting_to',
            'is_in_contact_with_dit_trade_advisor', 'export_experience_description',
            'export_strategy'
        ]

    has_exported_in_last_12_months = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_('Has your business exported any products or services in the last 12 months?'),
    )
    export_regions = forms.MultipleChoiceField(
        label=_('Which region(s) has your business exported to?'),
        choices=(
            ('africa', 'Africa'),
            ('asia', 'Asia'),
            ('australasia', 'Australasia'),
            ('europe', 'Europe'),
            ('middle east', 'Middle East'),
            ('north america', 'North America'),
            ('south america', 'South America')
        ),
        widget=widgets.CheckboxSelectMultiple()
    )
    markets_intending_on_exporting_to = forms.MultipleChoiceField(
        label=_('Which markets are you intending to export to using the TAP grant?'),
        choices=(
            ('existing', 'existing markets'),
            ('new', 'new markets not exported to in the last 12 months')
        ),
        widget=widgets.CheckboxSelectMultiple()
    )
    is_in_contact_with_dit_trade_advisor = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_('Are you in contact with a DIT trade advisor?'),
    )
    export_experience_description = MaxAllowedCharField(
        label=_('Describe your experience of exporting including successes and challenges'),
        max_length=2000,
        widget=widgets.CharacterCountTextArea(
            attrs={
                'class': 'govuk-textarea govuk-js-character-count',
                'rows': 7,
                'counter': 2000
            }
        )
    )
    export_strategy = MaxAllowedCharField(
        label=_('Provide a brief summary of your export strategy'),
        help_text=_(
            'Include short term (within the next 2 years) and longer term (2–5 years) objectives'
            ' and any barriers to entry'
        ),
        max_length=2000,
        widget=widgets.CharacterCountTextArea(
            attrs={
                'class': 'govuk-textarea govuk-js-character-count',
                'rows': 7,
                'counter': 2000
            }
        )
    )


class TradeEventDetailsForm(FormatLabelMixin, forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = [
            'interest_in_event_description', 'is_in_contact_with_tcp', 'tcp_name', 'tcp_email',
            'tcp_mobile_number', 'is_intending_to_exhibit_as_tcp_stand', 'stand_trade_name',
            'trade_show_experience_description', 'additional_guidance'
        ]

    interest_in_event_description = MaxAllowedCharField(
        label=_('Why are you particularly interested in <strong>{event_name}</strong>?'),
        max_length=2000,
        widget=widgets.CharacterCountTextArea(
            attrs={
                'class': 'govuk-textarea govuk-js-character-count',
                'rows': 7,
                'counter': 2000
            }
        )
    )
    is_in_contact_with_tcp = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_('Are you in contact with a Trade Challenge Partner (TCP) about this event?')
    )
    tcp_name = forms.CharField(
        required=False,
        empty_value=None,
        label=_('TCP contact name'),
        widget=forms.TextInput(
            attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
        )
    )
    tcp_email = forms.CharField(
        required=False,
        empty_value=None,
        label=_('TCP email address'),
        widget=forms.TextInput(
            attrs={
                'class': 'govuk-input govuk-!-width-two-thirds',
                'type': 'email',
            }
        )
    )
    tcp_mobile_number = PhoneNumberField(
        required=False,
        empty_value=None,
        label=_('TCP mobile number'),
        region='GB',
        widget=forms.TextInput(
            attrs={'class': 'govuk-input govuk-input--width-10'}
        )
    )
    is_intending_to_exhibit_as_tcp_stand = forms.TypedChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        coerce=str_to_bool,
        widget=widgets.RadioSelect(),
        label=_('Are you intending to exhibit as part of a TCP organised stand?')
    )
    stand_trade_name = forms.CharField(
        label=_('Are you intending to exhibit as part of a TCP organised stand?'),
        widget=forms.TextInput(
            attrs={'class': 'govuk-input'}
        )
    )
    trade_show_experience_description = MaxAllowedCharField(
        label=_(
            'What experience do you have of trade shows and how have they benefited your business?'
        ),
        max_length=2000,
        widget=widgets.CharacterCountTextArea(
            attrs={
                'class': 'govuk-textarea govuk-js-character-count',
                'rows': 7,
                'counter': 2000
            }
        )
    )
    additional_guidance = MaxAllowedCharField(
        label=_(
            'In addition to the financial support, are there particular areas where you would like'
            ' guidance and help either before, during or after the event? '
        ),
        max_length=2000,
        widget=widgets.CharacterCountTextArea(
            attrs={
                'class': 'govuk-textarea govuk-js-character-count',
                'rows': 7,
                'counter': 2000
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        is_in_contact_with_tcp = cleaned_data.get('is_in_contact_with_tcp')
        tcp_name = cleaned_data.get('tcp_name')
        tcp_email = cleaned_data.get('tcp_email')
        tcp_mobile_number = cleaned_data.get('tcp_mobile_number')

        if is_in_contact_with_tcp is True:
            if not tcp_name and 'tcp_name' not in self.errors:
                self.add_error('tcp_name', forms.ValidationError(FORM_MSGS['required']))
            if not tcp_email and 'tcp_email' not in self.errors:
                self.add_error('tcp_email', forms.ValidationError(FORM_MSGS['required']))
            if not tcp_mobile_number and 'tcp_mobile_number' not in self.errors:
                self.add_error('tcp_mobile_number', forms.ValidationError(FORM_MSGS['required']))
        elif is_in_contact_with_tcp is False:
            cleaned_data['tcp_name'] = None
            cleaned_data['tcp_email'] = None
            cleaned_data['tcp_mobile_number'] = None

        if 'tcp_mobile_number' in cleaned_data and cleaned_data['tcp_mobile_number']:
            cleaned_data['tcp_mobile_number'] = cleaned_data['tcp_mobile_number'].as_e164

        return cleaned_data


class AddStateAidForm(forms.ModelForm):

    class Meta:
        model = GrantApplicationLink
        fields = ['authority', 'amount', 'description', 'date_received']

    authority = forms.CharField(
        label=_('Authority'),
        widget=forms.TextInput(
            attrs={'class': 'govuk-input'}
        )
    )
    amount = CurrencyField(
        label=_('Total amount of aid'),
        help_text=_('For example, 1000'),
        min_value=1
    )
    description = MaxAllowedCharField(
        label=_('Description of aid'),
        max_length=2000,
        widget=widgets.CharacterCountTextArea(
            attrs={
                'class': 'govuk-textarea govuk-js-character-count',
                'rows': 7,
                'counter': 2000
            }
        )
    )
    date_received = forms.DateField(
        label=_('Date aid received'),
        help_text=_('For example, 3 11 2020'),
        widget=widgets.DateInput()
    )


class EditStateAidForm(AddStateAidForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].required = False
            if hasattr(self.fields[field_name], 'empty_value'):
                self.fields[field_name].empty_value = None
