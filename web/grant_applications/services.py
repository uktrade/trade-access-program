import datetime

from web.core.abstract_models import BaseMetaModel
from web.trade_events.models import Event


def _serialize_field(value):
    if isinstance(value, str):
        if value == 'True':
            return 'Yes'
        elif value == 'False':
            return 'No'

    if isinstance(value, Event):
        return value.display_name

    if isinstance(value, (datetime.date, BaseMetaModel)):
        return str(value)

    return value


def generate_summary_of_form_fields(form_class, url, grant_application):
    summary_list = []

    instance_form = form_class(instance=grant_application)
    data_form = form_class(data=instance_form.initial)
    data_form.is_valid()

    for key, value in data_form.cleaned_data.items():
        summary_list.append({
            'key': str(data_form.fields[key].label),
            'value': _serialize_field(value),
            'action': {
                'text': 'Change',
                'url': url,
            }
        })
    return summary_list
