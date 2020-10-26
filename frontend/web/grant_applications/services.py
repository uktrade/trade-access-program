import calendar
import logging
from collections import defaultdict
from urllib.parse import urljoin, urlparse

import requests
from django.conf import settings
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
        logger.error('An error occurred', exc_info=e)
        raise BackofficeServiceException


def _log_hook(response, **kwargs):
    body = response.request.body or b'No content'
    logger.info(
        f'EXTERNAL {response.request.method} : {response.request.url} : {body.decode()}'
    )
    if not response.ok:
        logger.error(f'RESPONSE : {response.status_code} : {response.text}')


class BackofficeService:

    def __init__(self):
        # URLs
        self.base_url = settings.BACKOFFICE_API_URL
        self.grant_applications_url = urljoin(self.base_url, 'grant-applications/')
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
        response = self.session.post(self.grant_applications_url, json=data)
        return response.json()

    def update_grant_application(self, grant_application_id, **data):
        url = urljoin(self.grant_applications_url, f'{grant_application_id}/')
        response = self.session.patch(url, json=data)
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

    def request_factory(self, object_type, **request_kwargs):
        if object_type == 'trade_events':
            return self.list_trade_events(**request_kwargs.get('params', {}))
        elif object_type == 'sectors':
            return self.list_sectors()
        raise ValueError(f'Unknown object type {object_type}')


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
        'trade_events', choice_id_key=attribute, choice_name_key=attribute
    )
    backoffice_choices = list(set(backoffice_choices))  # remove duplicates
    backoffice_choices.sort(key=lambda x: x[0])  # sort chronologically
    backoffice_choices.insert(0, ('', 'All'))
    return backoffice_choices


def get_trade_event_filter_by_month_choices():
    choices = set()

    for trade_event in BackofficeService().list_trade_events():
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
        'sectors', choice_id_key='id', choice_name_key='full_name'
    )
    backoffice_choices.insert(0, ('', 'Select...'))
    backoffice_choices.append(('0', 'Choice not listed'))
    return backoffice_choices


def generate_trade_event_select_options(trade_events):
    if not trade_events or not trade_events['results']:
        return None

    select_options = defaultdict(list)

    for te in trade_events['results']:
        select_options['choices'].append((te['id'], te['name']))
        select_options['hints'].append('\n'.join([
            te['tcp'], te['sector'], te['sub_sector'], te['country'],
            f"{te['start_date']} to {te['end_date']}"
        ]))

    return select_options


def get_company_select_options(search_term):
    select_options = defaultdict(list)
    try:
        response = BackofficeService().search_companies(search_term=search_term)
    except BackofficeServiceException:
        select_options = {'choices': [], 'hints': []}
    else:
        for c in response:
            select_options['choices'].append(
                (c['dnb_data']['duns_number'], c['dnb_data']['primary_name'])
            )
            select_options['hints'].append(c['registration_number'])
    return select_options


def _serialize_field(value):
    if value is True:
        return 'Yes'
    elif value is False:
        return 'No'
    return value


def generate_grant_application_summary(form_class, grant_application, url=None):
    form_data = BackofficeService().get_grant_application(
        str(grant_application.backoffice_grant_application_id),
        flatten_map={
            'event': 'event.name',
            'sector': 'sector.full_name',
            'duns_number': 'company.duns_number',
            'company': 'company.name',
        }
    )
    data_form = form_class(data=form_data)

    summary = []

    for field_name in data_form.fields:
        if hasattr(data_form, 'format_field_labels'):
            data_form.format_field_labels()

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
