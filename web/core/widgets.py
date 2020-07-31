from django import forms


class RadioSelect(forms.widgets.RadioSelect):
    input_type = 'radio'
    template_name = 'widgets/radio_select.html'
