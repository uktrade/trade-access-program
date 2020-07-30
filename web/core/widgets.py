from django import forms


class BooleanRadioSelect(forms.widgets.RadioSelect):
    input_type = 'radio'
    template_name = 'widgets/boolean_radio_select.html'
