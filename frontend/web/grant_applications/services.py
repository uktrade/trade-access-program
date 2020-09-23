import logging
from urllib.parse import urljoin, urlparse

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from web.core.utils import flatten_nested_dict

logger = logging.getLogger()


class BackofficeServiceException(Exception):
    pass


def _raise_for_status(response, **kwargs):
    try:
        response.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        logger.error(str(e), exc_info=e)
        raise BackofficeServiceException


def log_hook(response, **kwargs):
    body = response.request.body or b'No content'
    logger.info(
        f'EXTERNAL : REQUEST : {response.request.method} : {response.request.url} : {body.decode()}'
    )
    logger.info(f'EXTERNAL : RESPONSE : {response.status_code} : {response.text}')


class BackofficeService:

    def __init__(self):
        # URLs
        self.base_url = settings.BACKOFFICE_API_URL
        self.grant_applications_url = urljoin(self.base_url, 'grant-applications/')
        self.companies_url = urljoin(self.base_url, 'companies/')
        self.trade_events_url = urljoin(self.base_url, 'trade-events/')
        self.sectors_url = urljoin(self.base_url, 'sectors/')

        self.session = requests.Session()

        # Attach retry adapter
        retry_strategy = Retry(total=3, status_forcelist=[500], method_whitelist=['GET', 'POST'])
        retry_adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount(f'{urlparse(self.base_url).scheme}://', retry_adapter)

        # Attach response hooks
        self.session.hooks['response'] = [log_hook, _raise_for_status]

    def create_company(self, duns_number, name):
        response = self.session.post(
            self.companies_url, json={'duns_number': duns_number, 'name': name}
        )
        return response.json()

    def get_company(self, company_id):
        response = self.session.get(urljoin(self.companies_url, f'{company_id}/'))
        return response.json()

    def list_companies(self, **params):
        response = self.session.get(self.companies_url, params=params)
        return response.json()

    def get_or_create_company(self, duns_number, name):
        companies = self.list_companies(duns_number=duns_number)

        if companies and len(companies) == 1:
            company = companies[0]
        elif companies and len(companies) != 1:
            raise BackofficeServiceException('Too many companies')
        else:
            company = self.create_company(duns_number=duns_number, name=name)

        return company

    def create_grant_application(self, company_id, search_term):
        response = self.session.post(
            self.grant_applications_url,
            json={'company': company_id, 'search_term': search_term}
        )
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
            out[k] = flatten_nested_dict(out, m.split('.'))
        return out

    def send_grant_application_for_review(self, grant_application_id, application_summary):
        response = self.session.post(
            urljoin(self.grant_applications_url, f'{grant_application_id}/send-for-review/'),
            json={'application_summary': application_summary}
        )
        return response.json()

    def search_companies(self, search_term):
        url = urljoin(self.companies_url, 'search/')
        response = self.session.get(url, params={'search_term': search_term})
        return response.json()

    def list_trade_events(self):
        response = self.session.get(self.trade_events_url)
        return response.json()

    def list_sectors(self):
        response = self.session.get(self.sectors_url)
        return response.json()

    def request_factory(self, object_type, **request_kwargs):
        if object_type == 'companies':
            if not request_kwargs.get('search_term'):
                return []
            return self.search_companies(search_term=request_kwargs['search_term'])
        elif object_type == 'trade_events':
            return self.list_trade_events()
        elif object_type == 'sectors':
            return self.list_sectors()
        raise ValueError(f'Unknown object type {object_type}')


def get_backoffice_choices(object_type, choice_id, choice_name, **request_kwargs):
    try:
        backoffice_objects = BackofficeService().request_factory(object_type, **request_kwargs)
        backoffice_choices = [(c[choice_id], c[choice_name]) for c in backoffice_objects]
    except BackofficeServiceException:
        backoffice_choices = []

    choices = [('', 'Select...'), ('0', 'Choice not listed')]
    choices[1:1] = backoffice_choices

    return choices


def get_company_select_choices(search_term):
    return get_backoffice_choices(
        'companies', choice_id='duns_number', choice_name='primary_name', search_term=search_term
    )


def get_trade_event_select_choices():
    return get_backoffice_choices('trade_events', choice_id='id', choice_name='display_name')


def get_sector_select_choices():
    return get_backoffice_choices('sectors', choice_id='id', choice_name='full_name')


def _serialize_field(value):
    if value is True:
        return 'Yes'
    elif value is False:
        return 'No'
    return value


def generate_grant_application_summary(form_class, url, grant_application):
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

    summary_list = []

    for field_name in data_form.fields:
        if hasattr(data_form, 'format_field_labels'):
            data_form.format_field_labels()

        summary_list.append({
            'key': str(data_form[field_name].label),
            'value': _serialize_field(form_data.get(field_name)) or 'Not Applicable',
            'action': {
                'text': 'Change',
                'url': url,
            }
        })

    return summary_list
