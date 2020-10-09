from django import forms


class RadioSelect(forms.widgets.RadioSelect):
    input_type = 'radio'
    template_name = 'widgets/radio_select.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if 'hints' in self.attrs:
            option['hint'] = self.attrs['hints'][index][name]
        return option


class CharacterCountTextArea(forms.Textarea):
    template_name = 'widgets/character_count_text_area.html'


class AutocompleteSelect(forms.Select):
    template_name = 'widgets/autocomplete_select.html'


class WrappedTextInput(forms.TextInput):
    template_name = 'widgets/wrapped_text_input.html'


class CurrencyTextInput(WrappedTextInput):

    def get_context(self, name, value, attrs):
        attrs['prefix'] = '£'
        return super().get_context(name, value, attrs)
