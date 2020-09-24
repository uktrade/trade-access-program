from django import forms


class RadioSelect(forms.widgets.RadioSelect):
    input_type = 'radio'
    template_name = 'widgets/radio_select.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if 'hints' in self.attrs:
            option['hint'] = self.attrs['hints'][index][name]
        return option


class CurrencyInput(forms.widgets.TextInput):
    template_name = 'widgets/currency_input.html'
