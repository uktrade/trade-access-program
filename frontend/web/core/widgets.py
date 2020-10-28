from django import forms


class RadioSelect(forms.widgets.RadioSelect):
    input_type = 'radio'
    template_name = 'widgets/radio_select.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if 'hints' in self.attrs:
            option['hint'] = self.attrs['hints'][index]
        return option


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
