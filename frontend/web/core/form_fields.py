from django import forms


class MaxAllowedCharField(forms.CharField):

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        # Remove the maxlength attr because we want the user to be able to enter more than
        # 200 characters into the text area.
        # This allows the GOVUK GDS character count hints and messages to be displayed.
        # https://design-system.service.gov.uk/components/character-count/
        attrs.pop('maxlength', None)
        return attrs
