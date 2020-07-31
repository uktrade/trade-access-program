from django import forms
from django.conf import settings

from web.grant_applications.models import GrantApplication
from web.core import widgets

from django.utils.translation import gettext_lazy as _


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


class AboutTheEventForm(forms.ModelForm):

    class Meta:
        model = GrantApplication
        fields = [
            'event', 'is_already_committed_to_event', 'is_intending_on_other_financial_support'
        ]

    event = forms.CharField(
        widget=forms.Select(
            # TODO: select event choices from db model
            choices=[('Event 1', 'Event 1'), ('Event 2', 'Event 2')],
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
        label=_('Will you receive or are you applying for any other'
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
        label=_('Is this the first time you intend to exhibit at {event}?')
    )

    number_of_times_exhibited_at_event = forms.IntegerField(
        min_value=0,
        required=True,
        label=_('How many times have you exhibited at {event} previously?'),
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
            'goods_and_services_description': forms.TextInput(
                attrs={'class': 'govuk-textarea govuk-!-width-two-thirds'}
            ),
            'business_name_at_exhibit': forms.TextInput(
                attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
            ),
            'turnover': forms.TextInput(
                attrs={'class': 'govuk-input govuk-!-width-one-quarter'}
            ),
            'number_of_employees': forms.TextInput(
                attrs={'class': 'govuk-input govuk-!-width-one-quarter'}
            ),
            'sector': forms.TextInput(
                attrs={'class': 'govuk-input govuk-!-width-one-quarter'}
            ),
            'website': forms.TextInput(
                attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
            ),
        }
