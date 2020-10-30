from django import forms

from web.core.widgets import CurrencyInput

FORM_MSGS = {
    'required': 'This field is required.',
    'invalid-combination': 'The form contains an invalid combination of fields.',
    'resubmit': 'An unexpected error occurred. Please resubmit the form.',
    'invalid-choice': 'Select a valid choice. {} is not one of the available choices.',
    'positive': 'Ensure this value is greater than or equal to 0.',
    '2dp': 'Ensure that there are no more than 2 decimal places.'
}


class MaxAllowedCharField(forms.CharField):

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        # Remove the maxlength attr because we want the user to be able to enter more than
        # 200 characters into the text area.
        # This allows the GOVUK GDS character count hints and messages to be displayed.
        # https://design-system.service.gov.uk/components/character-count/
        attrs.pop('maxlength', None)
        return attrs


class CurrencyField(forms.DecimalField):

    def __init__(self, **kwargs):
        super().__init__(min_value=0, decimal_places=2, widget=CurrencyInput(), **kwargs)
