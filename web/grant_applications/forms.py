from django import forms

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

    is_already_committed_to_event = forms.BooleanField(
        required=True,
        widget=widgets.BooleanRadioSelect(),
        label=_('Have you already committed to attending this event?'),
    )

    is_intending_on_other_financial_support = forms.BooleanField(
        required=True,
        widget=widgets.BooleanRadioSelect(),
        label=_('Will you receive or are you applying for any other'
                'financial support for this event?')
    )


class PreviousApplicationsForm(forms.ModelForm):

    class Meta:
        model = GrantApplication
        fields = ['has_previously_applied']

    has_previously_applied = forms.BooleanField(
        required=True,
        widget=widgets.BooleanRadioSelect(),
        label=_('Is this the first time you have applied for a TAP grant?')
    )
