import datetime

from web.trade_events.models import Event


def _serialize_field(value):
    if isinstance(value, str):
        if value == 'True':
            return 'Yes'
        elif value == 'False':
            return 'No'

    if isinstance(value, Event):
        return value.display_name

    if isinstance(value, datetime.date):
        return str(value)

    return value


def _generate_summary(view_class, grant_application):
    if not hasattr(view_class, 'model') or not getattr(view_class, 'model'):
        return []

    summary_list = []

    instance_form = view_class.form_class(instance=grant_application)
    data_form = view_class.form_class(data=instance_form.initial)
    data_form.is_valid()

    for key, value in data_form.cleaned_data.items():
        summary_list.append({
            'key': key,
            'value': _serialize_field(value),
            'action': {
                'text': 'Change',
                'url': view_class(object=grant_application).get_success_url(),
            }
        })
    return summary_list


def generate_application_summary(view_classes, grant_application):
    summary_list = []

    for view_class in view_classes:
        summary_list += _generate_summary(view_class, grant_application)

    return summary_list
