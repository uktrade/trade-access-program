class FormatLabelMixin:

    def format_label(self, field_name, **kwargs):
        self[field_name].label = self[field_name].label.format(**kwargs)
