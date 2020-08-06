from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from web.core import widgets
from web.grant_applications.models import GrantApplication
from web.trade_events.models import Event


class SearchCompanyForm(forms.Form):

    search_term = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'govuk-input govuk-!-width-two-thirds',
            'placeholder': 'Search...',
        })
    )


class SelectCompanyForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        company_choices = kwargs.pop('company_choices')
        super().__init__(*args, **kwargs)
        self.fields['duns_number'] = forms.ChoiceField(
            label='',
            widget=forms.Select(
                attrs={
                    'class': 'govuk-select govuk-!-width-two-thirds',
                    'placeholder': 'Select your company...',
                }
            ),
            choices=company_choices
        )

    class Meta:
        model = GrantApplication
        fields = ['duns_number']


class AboutYourBusinessForm(forms.ModelForm):
    class Meta:
        model = GrantApplication
        fields = []


class AboutYouForm(forms.ModelForm):

    class Meta:
        model = GrantApplication
        fields = ['applicant_full_name', 'applicant_email']
        labels = {
            'applicant_full_name': _('Your full name'),
            'applicant_email': _('Your email address'),
        }
        widgets = {
            'applicant_full_name': forms.TextInput(
                attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
            ),
            'applicant_email': forms.TextInput(
                attrs={
                    'class': 'govuk-input govuk-!-width-two-thirds',
                    'type': 'email',
                }
            ),
        }


class EventChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.display_name


class AboutTheEventForm(forms.ModelForm):

    class Meta:
        model = GrantApplication
        fields = [
            'event', 'is_already_committed_to_event', 'is_intending_on_other_financial_support'
        ]

    event = EventChoiceField(
        queryset=Event.objects.all().order_by('country', 'city'),
        empty_label='Select the event...',
        widget=forms.Select(
            attrs={'class': 'govuk-select govuk-!-width-two-thirds'}
        ),
        label=_('Select event'),
    )

    is_already_committed_to_event = forms.ChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        required=True,
        widget=widgets.RadioSelect(),
        label=_('Have you already committed to attending this event?'),
    )

    is_intending_on_other_financial_support = forms.ChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        required=True,
        widget=widgets.RadioSelect(),
        label=_('Will you receive or are you applying for any other '
                'financial support for this event?')
    )


class PreviousApplicationsForm(forms.ModelForm):

    class Meta:
        model = GrantApplication
        fields = ['has_previously_applied', 'previous_applications']

    has_previously_applied = forms.ChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        required=True,
        widget=widgets.RadioSelect(),
        label=_('Is this the first time you have applied for a TAP grant?')
    )

    previous_applications = forms.ChoiceField(
        choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, '6 or more')],
        required=True,
        widget=widgets.RadioSelect(),
        label=_('How many TAP grants have you received since 1 April 2009?'),
    )


class EventIntentionForm(forms.ModelForm):

    class Meta:
        model = GrantApplication
        fields = ['is_first_exhibit_at_event', 'number_of_times_exhibited_at_event']

    is_first_exhibit_at_event = forms.ChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        required=True,
        widget=widgets.RadioSelect(),
        label=_("Is this the first time you intend to exhibit at '{event.name}'?")
    )

    number_of_times_exhibited_at_event = forms.IntegerField(
        min_value=0,
        required=True,
        label=_("How many times have you exhibited at '{event.name}' previously?"),
        widget=forms.NumberInput(
            attrs={'class': 'govuk-input govuk-!-width-one-quarter'}
        )
    )

    def format_label(self, field_name, **kwargs):
        self[field_name].label = self[field_name].label.format(**kwargs)


class BusinessInformationForm(forms.ModelForm):

    class Meta:
        model = GrantApplication
        fields = [
            'goods_and_services_description', 'business_name_at_exhibit', 'turnover',
            'number_of_employees', 'sector', 'website'
        ]
        labels = {
            'goods_and_services_description': _(
                'Description of goods or services, and whether they are from UK origin'
            ),
            'business_name_at_exhibit': _('Business name that you will use on the stand'),
        }
        widgets = {
            'goods_and_services_description': forms.Textarea(
                attrs={'class': 'govuk-textarea govuk-!-width-two-thirds'}
            ),
            'business_name_at_exhibit': forms.TextInput(
                attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
            ),
            'turnover': forms.NumberInput(
                attrs={'class': 'govuk-input govuk-!-width-one-quarter'}
            ),
            'number_of_employees': forms.NumberInput(
                attrs={'class': 'govuk-input govuk-!-width-one-quarter'}
            ),
            'sector': forms.TextInput(
                attrs={'class': 'govuk-input govuk-!-width-one-quarter'}
            ),
            'website': forms.TextInput(
                attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
            ),
        }


class ExportExperienceForm(forms.ModelForm):

    class Meta:
        model = GrantApplication
        fields = [
            'has_exported_before', 'is_planning_to_grow_exports', 'is_seeking_export_opportunities'
        ]

    has_exported_before = forms.ChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        required=True,
        widget=widgets.RadioSelect(),
        label=_('Have you exported before?'),
    )

    is_planning_to_grow_exports = forms.ChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        required=True,
        widget=widgets.RadioSelect(),
        label=_('Are you planning to grow your exports in up to six countries within '
                'the European Union or beyond?')
    )

    is_seeking_export_opportunities = forms.ChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        required=True,
        widget=widgets.RadioSelect(),
        label=_('Are you actively investigating export opportunities for your business?')
    )


class StateAidForm(forms.ModelForm):

    class Meta:
        model = GrantApplication
        fields = [
            'has_received_de_minimis_aid', 'de_minimis_aid_public_authority',
            'de_minimis_aid_date_awarded', 'de_minimis_aid_amount', 'de_minimis_aid_description',
            'de_minimis_aid_recipient', 'de_minimis_aid_date_received'
        ]
        labels = {
            'de_minimis_aid_public_authority': _('Authority'),
            'de_minimis_aid_date_awarded': _('Date awarded'),
            'de_minimis_aid_amount': _('Total amount of aid'),
            'de_minimis_aid_description': _('Description of aid'),
            'de_minimis_aid_recipient': _('Recipient'),
            'de_minimis_aid_date_received': _('Date of received aid')
        }
        widgets = {
            'de_minimis_aid_public_authority': forms.TextInput(
                attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
            ),
            'de_minimis_aid_date_awarded': forms.widgets.SelectDateWidget(
                attrs={'class': 'govuk-date-input__item govuk-input govuk-input--width-4'},
            ),
            'de_minimis_aid_amount': forms.NumberInput(
                attrs={'class': 'govuk-input govuk-!-width-one-quarter'}
            ),
            'de_minimis_aid_description': forms.Textarea(
                attrs={'class': 'govuk-textarea govuk-!-width-two-thirds'}
            ),
            'de_minimis_aid_recipient': forms.TextInput(
                attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
            ),
            'de_minimis_aid_date_received': forms.widgets.SelectDateWidget(
                attrs={'class': 'govuk-date-input__item govuk-input govuk-input--width-4'},
            ),
        }

    has_received_de_minimis_aid = forms.ChoiceField(
        choices=settings.BOOLEAN_CHOICES,
        widget=widgets.RadioSelect(),
        label=_(
            'Have you received any de minimis aid (whether de minimis aid from or '
            'attributable to DIT or any other public authority) during the current and two '
            'previous Fiscal Years?'
        )
    )


class ApplicationReviewForm(forms.ModelForm):

    class Meta:
        model = GrantApplication
        fields = []
