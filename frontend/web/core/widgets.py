from django import forms


class RadioSelect(forms.widgets.RadioSelect):
    input_type = 'radio'
    template_name = 'widgets/radio_select.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if 'hints' in self.attrs:
            option['hint'] = self.attrs['hints'][index][name]
        return option

    def get_details(self, attrs):
        if 'details' in attrs:
            return {
                'summary_text': attrs['details']['summary_text'],
                'text': attrs['details']['text'],
            }

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['details'] = self.get_details(attrs)
        return context


class CurrencyInput(forms.widgets.TextInput):
    template_name = 'widgets/currency_input.html'


class WrappedTextInput(forms.TextInput):
    template_name = 'widgets/wrapped_text_input.html'
