from datetime import date

from django import forms


class RadioSelect(forms.widgets.RadioSelect):
    input_type = 'radio'
    template_name = 'widgets/radio_select.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if 'hints' in self.attrs:
            option['hint'] = self.attrs['hints'][index]
        return option


class DatePartInput(forms.TextInput):
    template_name = 'widgets/date_part_input.html'


class DateInput(forms.MultiWidget):
    template_name = 'widgets/date_input.html'

    def __init__(self, attrs=None):
        widgets = [
            DatePartInput(
                attrs={
                    'label': 'Day',
                    'class': 'govuk-date-input__item govuk-input govuk-input--width-2',
                    'pattern': '[0-9]*',
                    'inputmode': 'numeric',
                }
            ),
            DatePartInput(
                attrs={
                    'label': 'Month',
                    'class': 'govuk-date-input__item govuk-input govuk-input--width-2',
                    'pattern': '[0-9]*',
                    'inputmode': 'numeric',
                }
            ),
            DatePartInput(
                attrs={
                    'label': 'Year',
                    'class': 'govuk-date-input__item govuk-input govuk-input--width-3',
                    'pattern': '[0-9]*',
                    'inputmode': 'numeric',
                }
            ),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if isinstance(value, date):
            return [value.day, value.month, value.year]
        elif isinstance(value, str):
            year, month, day = value.split('-')
            return [day, month, year]
        return [None, None, None]

    def value_from_datadict(self, data, files, name):
        day, month, year = super().value_from_datadict(data, files, name)
        if all([day, month, year]):
            return '{}-{}-{}'.format(year, month, day)


class CheckboxSelectMultiple(forms.widgets.CheckboxSelectMultiple):
    template_name = 'widgets/checkbox_select_multiple.html'


class TextWithDetailInput(forms.TextInput):
    template_name = 'widgets/text_with_detail_input.html'


class CharacterCountTextArea(forms.Textarea):
    template_name = 'widgets/character_count_text_area.html'


class WrappedTextInput(forms.TextInput):
    template_name = 'widgets/wrapped_input.html'


class WrappedNumberInput(forms.NumberInput):
    template_name = 'widgets/wrapped_input.html'


class CurrencyInput(WrappedTextInput):
    """A special wrapped input that displays a currency symbol prefix.

       We inherit the WrappedTextInput widget (rather than the WrappedNumberInput) because of GDS
       guidelines for decimal numbers https://design-system.service.gov.uk/components/text-input/

       The currency_symbol default is '£'.
    """
    currency_symbol = '£'

    def get_context(self, name, value, attrs):
        attrs['prefix'] = self.currency_symbol
        return super().get_context(name, value, attrs)
