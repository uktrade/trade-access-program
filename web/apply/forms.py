from django import forms

from web.apply.models import ApplicationProcess


class SearchCompanyForm(forms.Form):

    search_term = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'govuk-input govuk-!-width-two-thirds',
            'placeholder': 'Search...',
        })
    )


class SelectCompanyForm(forms.Form):

    def __init__(self, company_choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['duns_number'].choices = company_choices

    duns_number = forms.ChoiceField(
        label='',
        widget=forms.Select(
            attrs={
                'class': 'govuk-select govuk-!-width-two-thirds',
                'placeholder': 'Select your company...',
            }
        )
    )


class SubmitApplicationForm(forms.ModelForm):

    class Meta:
        model = ApplicationProcess
        fields = [
            'applicant_full_name', 'applicant_email', 'event_name', 'event_date',
            'requested_amount'
        ]
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
            'event_name': forms.TextInput(
                attrs={'class': 'govuk-input govuk-!-width-two-thirds'}
            ),
            'event_date': forms.widgets.SelectDateWidget(
                attrs={'class': 'govuk-date-input__item govuk-input govuk-input--width-4'},
            ),
            'requested_amount': forms.TextInput(
                attrs={'class': 'govuk-input govuk-input--width-5'}
            ),
        }
