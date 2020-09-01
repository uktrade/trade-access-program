from django import forms


class RadioSelect(forms.widgets.RadioSelect):
    input_type = 'radio'
    template_name = 'widgets/radio_select.html'


class CurrencyInput(forms.widgets.TextInput):
    template_name = 'widgets/currency_input.html'
