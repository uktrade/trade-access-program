import calendar
import json
import logging
import re
from collections import defaultdict
from urllib.parse import urljoin, urlparse

import requests
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.utils.dateparse import parse_date
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from web.core.utils import flatten_nested_dict

logger = logging.getLogger(__name__)


class BackofficeServiceException(Exception):
    pass


def _raise_for_status(response, **kwargs):
    try:
        response.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        logger.error('An error occurred', exc_info=e, extra={'response_data': response.json()})
        raise BackofficeServiceException


def _log_hook(response, **kwargs):
    body = response.request.body or 'No content'
    logger.info(f'EXTERNAL {response.request.method} : {response.request.url} : {body}')
    if not response.ok:
        logger.error(f'RESPONSE : {response.status_code} : {response.text}')


class BackofficeService:

    def __init__(self):
        # URLs
        self.base_url = settings.BACKOFFICE_API_URL
        self.grant_applications_url = urljoin(self.base_url, 'grant-applications/')
        self.state_aid_url = urljoin(self.base_url, 'state-aid/')
        self.companies_url = urljoin(self.base_url, 'companies/')
        self.trade_events_url = urljoin(self.base_url, 'trade-events/')
        self.trade_event_aggregates_url = urljoin(self.base_url, 'trade-events/aggregates/')
        self.sectors_url = urljoin(self.base_url, 'sectors/')

        self.session = requests.Session()

        # Attach retry adapter
        retry_strategy = Retry(total=3, status_forcelist=[500], method_whitelist=['GET', 'POST'])
        retry_adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount(f'{urlparse(self.base_url).scheme}://', retry_adapter)

        # Attach response hooks
        self.session.hooks['response'] = [_log_hook, _raise_for_status]

    def request(self, method, url, data):
        return self.session.request(
            method, url, json=json.loads(json.dumps(data, cls=DjangoJSONEncoder))
        )

    def post(self, url, data):
        return self.request('POST', url, data)

    def patch(self, url, data):
        return self.request('PATCH', url, data)

    def create_company(self, duns_number, registration_number, name):
        response = self.session.post(
            self.companies_url,
            json={
                'duns_number': duns_number,
                'registration_number': registration_number,
                'name': name
            }
        )
        return response.json()

    def get_company(self, company_id):
        response = self.session.get(urljoin(self.companies_url, f'{company_id}/'))
        return response.json()

    def list_companies(self, **params):
        response = self.session.get(self.companies_url, params=params)
        return response.json()

    def get_or_create_company(self, duns_number, registration_number, name):
        companies = self.list_companies(
            duns_number=duns_number, registration_number=registration_number
        )

        if companies and len(companies) == 1:
            company = companies[0]
        elif companies and len(companies) != 1:
            logger.error('Too many companies')
            raise BackofficeServiceException('Too many companies')
        else:
            company = self.create_company(
                duns_number=duns_number, registration_number=registration_number, name=name
            )

        return company

    def create_grant_application(self, **data):
        response = self.post(self.grant_applications_url, data)
        return response.json()

    def update_grant_application(self, grant_application_id, **data):
        url = urljoin(self.grant_applications_url, f'{grant_application_id}/')
        response = self.patch(url, data)
        return response.json()

    def get_grant_application(self, grant_application_id, flatten_map=None):
        flatten_map = flatten_map or {}
        url = urljoin(self.grant_applications_url, f'{grant_application_id}/')
        response = self.session.get(url)
        out = response.json()
        for k, m in flatten_map.items():
            out[k] = flatten_nested_dict(out, key_path=m.split('.'))
        return out

    def send_grant_application_for_review(self, grant_application_id, application_summary):
        response = self.session.post(
            urljoin(self.grant_applications_url, f'{grant_application_id}/send-for-review/'),
            json={'application_summary': application_summary}
        )
        return response.json()

    def create_state_aid(self, **data):
        response = self.post(self.state_aid_url, data)
        return response.json()

    def update_state_aid(self, state_aid_id, **data):
        url = urljoin(self.state_aid_url, f'{state_aid_id}/')
        response = self.patch(url, data)
        return response.json()

    def delete_state_aid(self, state_aid_id):
        self.session.delete(urljoin(self.state_aid_url, f'{state_aid_id}/'))

    def get_state_aid(self, state_aid_id):
        response = self.session.get(urljoin(self.state_aid_url, f'{state_aid_id}/'))
        return response.json()

    def list_state_aids(self, **params):
        response = self.session.get(self.state_aid_url, params=params)
        return response.json()

    def search_companies(self, **params):
        url = urljoin(self.companies_url, 'search/')
        response = self.session.get(url, params=params)
        return response.json()

    def list_trade_events(self, **params):
        response = self.session.get(self.trade_events_url, params=params)
        return response.json()

    def list_sectors(self):
        response = self.session.get(self.sectors_url)
        return response.json()

    def get_trade_event_aggregates(self, **params):
        response = self.session.get(self.trade_event_aggregates_url, params=params)
        return response.json()

    def request_factory(self, object_type, raise_exception=True, **request_params):
        try:
            if object_type == 'list_trade_events':
                return self.list_trade_events(**request_params)
            elif object_type == 'list_sectors':
                return self.list_sectors()
            elif object_type == 'search_companies':
                return self.search_companies(**request_params)
            raise ValueError(f'Unknown object type {object_type}')
        except (BackofficeServiceException, ValueError):
            if raise_exception:
                raise


def get_backoffice_choices(object_type, choice_id_key, choice_name_key, request_kwargs=None):
    request_kwargs = request_kwargs or {}
    backoffice_choices = []
    try:
        backoffice_objects = BackofficeService().request_factory(object_type, **request_kwargs)
    except BackofficeServiceException:
        return backoffice_choices
    else:
        for bo in backoffice_objects:
            backoffice_choices.append((bo[choice_id_key], bo[choice_name_key]))

    return backoffice_choices


def get_trade_event_filter_choices(attribute):
    backoffice_choices = get_backoffice_choices(
        'list_trade_events', choice_id_key=attribute, choice_name_key=attribute
    )
    backoffice_choices = list(set(backoffice_choices))  # remove duplicates
    backoffice_choices.sort(key=lambda x: x[0])  # sort chronologically
    backoffice_choices.insert(0, ('', 'All'))
    return backoffice_choices


def get_trade_event_filter_by_month_choices():
    trade_events = BackofficeService().request_factory('list_trade_events', raise_exception=False)
    if not trade_events:
        return []

    choices = set()

    for trade_event in trade_events:
        start_date = parse_date(trade_event['start_date'])
        _, last_day = calendar.monthrange(start_date.year, start_date.month)
        first_day_of_month = start_date.replace(day=1)
        last_day_of_month = start_date.replace(day=last_day)
        month_year_str = start_date.strftime('%B %Y')
        choices.add((f'{first_day_of_month}:{last_day_of_month}', month_year_str))

    choices = list(choices)
    choices.sort(key=lambda x: x[0])
    choices.insert(0, ('', 'All'))

    return choices


def get_sector_select_choices():
    backoffice_choices = get_backoffice_choices(
        'list_sectors', choice_id_key='id', choice_name_key='full_name'
    )
    backoffice_choices.insert(0, ('', 'Select...'))
    backoffice_choices.append(('0', 'Choice not listed'))
    return backoffice_choices


def generate_trade_event_select_options(trade_events):
    if not trade_events or not trade_events['results']:
        return {'choices': [], 'hints': []}

    select_options = defaultdict(list)

    for te in trade_events['results']:
        select_options['choices'].append((te['id'], te['name']))
        select_options['hints'].append('\n'.join([
            te['tcp'], te['sector'], te['sub_sector'], te['country'],
            f"{te['start_date']} to {te['end_date']}"
        ]))

    return select_options


def generate_company_select_options(companies):
    if not companies:
        return {'choices': [], 'hints': []}

    select_options = defaultdict(list)

    for c in companies:
        select_options['choices'].append(
            (c['dnb_data']['duns_number'], c['dnb_data']['primary_name'])
        )
        select_options['hints'].append(c['registration_number'])

    return select_options


def _looks_like_registration_number(search_term):
    return bool(re.match('(SC|NI|[0-9]{2})[0-9]{6}', search_term))


def get_companies_from_search_term(search_term):
    if not search_term:
        return None

    if _looks_like_registration_number(search_term):
        params = {'registration_numbers': [search_term]}
    else:
        params = {'primary_name': search_term}

    return BackofficeService().request_factory('search_companies', raise_exception=False, **params)


def _serialize_field(value):
    if value is True:
        return 'Yes'
    elif value is False:
        return 'No'
    return value


def generate_grant_application_summary(grant_application, form_class, form_kwargs, url=None):
    form_data = BackofficeService().get_grant_application(
        str(grant_application.backoffice_grant_application_id),
        flatten_map={
            'event': 'event.name',
            'sector': 'sector.full_name',
            'duns_number': 'company.duns_number',
            'company': 'company.name',
        }
    )
    data_form = form_class(data=form_data, **form_kwargs)

    summary = []

    for field_name in data_form.fields:
        row = {
            'key': str(data_form[field_name].label),
            'value': _serialize_field(form_data.get(field_name)) or 'Not Applicable',
        }
        if url:
            row['action'] = {
                'text': 'Change',
                'url': url,
            }
        summary.append(row)

    return summary


def get_state_aid_summary_table(grant_application_link, state_aid_items):
    if not state_aid_items:
        return {
            'headers': ['Authority', 'Amount', 'Description', 'Date received'],
            'rows': [['-', '-', '-', '-']]
        }

    table = {
        'cols': [
            "style=width:13%", "style=width:13%", "style=width:31%", "style=width:13%",
            "style=width:13%", "style=width:7%", "style=width:10%"
        ],
        'headers': ['Authority', 'Amount', 'Description', 'Date received', '', '', ''],
        'rows': [],
    }
    link_html = "<a class='govuk-link govuk-link--no-visited-state' href='{href}'>{text}</a>"

    for state_aid in state_aid_items:
        resolve_kwargs = {'pk': grant_application_link.pk, 'state_aid_pk': state_aid['id']}
        duplicate_href = reverse('grant-applications:duplicate-state-aid', kwargs=resolve_kwargs)
        edit_href = reverse('grant-applications:edit-state-aid', kwargs=resolve_kwargs)
        remove_href = reverse('grant-applications:delete-state-aid', kwargs=resolve_kwargs)
        table['rows'].append([
            state_aid['authority'],
            state_aid['amount'],
            state_aid['description'],
            state_aid['date_received'],
            link_html.format(text='Duplicate', href=duplicate_href),
            link_html.format(text='Edit', href=edit_href),
            link_html.format(text='Remove', href=remove_href)
        ])

    return table
