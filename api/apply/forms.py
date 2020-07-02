from decimal import Decimal

from django import forms


class StartApplicationForm(forms.Form):
    class Meta:
        widgets = {
            'event_date': ()
        }

    full_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'govuk-input govuk-!-width-two-thirds',
        })
    )

    event_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'govuk-input govuk-!-width-two-thirds',
        })
    )

    event_date = forms.DateField(
        widget=forms.widgets.SelectDateWidget(
            attrs={
                'class': 'govuk-date-input__item govuk-input govuk-input--width-4',
            },
        )
    )

    requested_amount = forms.DecimalField(
        min_value=Decimal('500'),
        max_value=Decimal('2500'),
        decimal_places=2,
        widget=forms.TextInput(attrs={
            'class': 'govuk-input govuk-input--width-5',
        })
    )


class EligibilityForm(forms.Form):
    search_term = forms.CharField(
        label='Search your company name',
        initial="Search...",
        widget=forms.TextInput(attrs={
            'class': 'govuk-input govuk-!-width-one-third',
        })
    )

    company = forms.ChoiceField(
        choices=[],
        label="",
        widget=forms.Select(attrs={
            'class': 'govuk-select govuk-!-width-one-third',
        })
    )
