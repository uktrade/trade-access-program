import calendar
import json
import logging
import re
from collections import defaultdict
from urllib.parse import urljoin, urlparse

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from web.core.services import SummaryListHelper

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
        self.send_user_email_url = urljoin(self.base_url, 'send-user-email/')

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

    def get_grant_application(self, grant_application_id):
        url = urljoin(self.grant_applications_url, f'{grant_application_id}/')
        response = self.session.get(url)
        return response.json()

    def send_grant_application_for_review(self, grant_application_id, application_summary):
        response = self.post(
            urljoin(self.grant_applications_url, f'{grant_application_id}/send-for-review/'),
            data={'application_summary': application_summary}
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

    def send_application_authentication_link_email(self, grant_application, auth_link):
        response = self.session.post(
            self.send_user_email_url,
            json={
                'template_name': 'application-authentication',
                'email': grant_application.email,
                'grant_application_id': grant_application.backoffice_grant_application_id,
                'email_context': {
                    'application_auth_link': auth_link
                }
            }
        )
        return response.json()


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

    address_fields = ['address_line_1', 'address_line_2', 'address_postcode', 'address_town']
    select_options = defaultdict(list)

    for c in companies:
        select_options['choices'].append(
            (c['dnb_data']['duns_number'], c['dnb_data']['primary_name'])
        )

        hints = [v for k, v in c['dnb_data'].items() if k in address_fields and v]
        if c['registration_number']:
            hints.insert(0, c['registration_number'])

        select_options['hints'].append('\n'.join(hints))

    return select_options


def _looks_like_registration_number(value):
    return bool(re.match(r'(SC|NI|[0-9]{2})[0-9]{6}', value))


def validate_registration_number(value, msg='Invalid registration_number.'):
    if not _looks_like_registration_number(value):
        raise ValidationError(_(msg))


def _looks_like_vat_number(value):
    return bool(re.match(r'([0-9]{9}([0-9]{3})?|[A-Z]{2}[0-9]{3})', value))


def validate_vat_number(value, msg='Invalid vat_number.'):
    if not _looks_like_vat_number(value):
        raise ValidationError(_(msg))


def get_companies_from_search_term(search_term):
    if not search_term:
        return None

    if _looks_like_registration_number(search_term):
        params = {'registration_numbers': [search_term]}
    else:
        params = {'primary_name': search_term}

    return BackofficeService().request_factory('search_companies', raise_exception=False, **params)


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


class ApplicationReviewService:

    def __init__(self, grant_application_link, application_data):
        self.grant_application_link = grant_application_link
        self.application_data = application_data
        self.summary_list_helper = SummaryListHelper()

    @staticmethod
    def _serialize_field(value):
        if value is True:
            return 'Yes'
        elif value is False:
            return 'No'
        return value

    def _make_row(self, url, key, value=None, field_name=None):
        if value is None:
            value = self._serialize_field(self.application_data[field_name])
        return self.summary_list_helper.make_row(key=str(key), value=value, url=url)

    def _make_rows(self, fields, url):
        rows = []

        for field in fields:
            if field.name not in self.application_data:
                continue
            rows.append(self._make_row(url=url, key=field.label, field_name=field.name))

        return rows

    def generic_summary_list(self, heading, fields, url):
        rows = self._make_rows(fields=fields, url=url)
        if rows:
            return self.summary_list_helper.make_summary_list(heading=heading, rows=rows)

    def select_an_event_summary_list(self, heading, fields, url):
        _fields = {f.name: f for f in fields}
        event = self.application_data['event']
        rows = [
            self._make_row(
                key=_fields['event'].label,
                url=url + f"?filter_by_name={event['name']}",
                value='\n'.join([
                    event['name'],
                    event['tcp'],
                    event['sector'],
                    event['sub_sector'],
                    f"{event['city']}, {event['country']}",
                    f"{event['start_date']} to {event['end_date']}",
                ])
            )
        ]
        return self.summary_list_helper.make_summary_list(heading=heading, rows=rows)

    def event_commitment_summary_list(self, heading, fields, url):
        _fields = {f.name: f for f in fields}
        label = _fields['is_already_committed_to_event'].label.format(
            event_name=self.application_data['event']['name']
        )
        _fields['is_already_committed_to_event'].label = label
        return self.generic_summary_list(heading, fields, url)

    def select_company_summary_list(self, heading, fields, url):
        company = self.application_data['company']

        if company is None:
            # User did not select a company and instead entered their details manually.
            return

        values = [
            company['name'],
            company['last_dnb_get_company_response']['company_address'],
        ]
        if company['registration_number']:
            values.insert(1, company['registration_number'])
        row = self._make_row(
            url=url + f"?search_term={company['registration_number'] or company['name']}",
            key='Business',
            value='\n'.join(values)
        )
        return self.summary_list_helper.make_summary_list(heading=heading, rows=[row])

    def manual_company_details_summary_list(self, heading, fields, url):
        if self.application_data['manual_company_type'] is None:
            # Manual company details is a conditional view. Return None if no data was entered
            return

        _fields = {f.name: f for f in fields}
        address_fields = [
            'manual_company_address_line_1', 'manual_company_address_line_2',
            'manual_company_address_town', 'manual_company_address_county',
            'manual_company_address_postcode'
        ]
        rows = [
            self._make_row(
                url=url,
                key='Business type',
                field_name='manual_company_type'
            ),
            self._make_row(
                url=url,
                key=_fields['manual_company_name'].label,
                field_name='manual_company_name'
            ),
            self._make_row(
                url=url,
                key='Business address',
                value='\n'.join([
                    self.application_data[f] for f in address_fields if self.application_data[f]
                ])
            ),
            self._make_row(
                url=url,
                key='Length of time trading in UK',
                field_name='manual_time_trading_in_uk'
            ),
            self._make_row(
                url=url,
                key=_fields['manual_registration_number'].label,
                value=self.application_data['manual_registration_number'] or '—'
            ),
            self._make_row(
                url=url,
                key=_fields['manual_vat_number'].label,
                value=self.application_data['manual_vat_number'] or '—'
            ),
            self._make_row(
                url=url,
                key=_fields['manual_website'].label,
                field_name='manual_website'
            )
        ]
        return self.summary_list_helper.make_summary_list(heading=heading, rows=rows)

    def company_trading_details_summary_list(self, heading, fields, url):
        _fields = {f.name: f for f in fields}
        rows = [
            self._make_row(
                url=url,
                key='Annual turnover for the last 3 fiscal years',
                value='\n'.join([
                    f"Last year - {self.application_data['previous_years_turnover_1']}",
                    f"Year 2 - {self.application_data['previous_years_turnover_2']}",
                    f"Year 3 - {self.application_data['previous_years_turnover_3']}"
                ])
            ),
            self._make_row(
                url=url,
                key='Annual turnover generated from exports',
                value='\n'.join([
                    f"Last year - {self.application_data['previous_years_export_turnover_1']}",
                    f"Year 2 - {self.application_data['previous_years_export_turnover_2']}",
                    f"Year 3 - {self.application_data['previous_years_export_turnover_3']}"
                ])
            ),
            self._make_row(
                url=url,
                key=_fields['other_business_names'].label,
                field_name='other_business_names'
            ),
            self._make_row(
                url=url,
                key=_fields['sector'].label,
                value=self.application_data['sector']['full_name']
            ),
            self._make_row(
                url=url,
                key=_fields['products_and_services_description'].label,
                field_name='products_and_services_description'
            ),
            self._make_row(
                url=url,
                key=_fields['products_and_services_competitors'].label,
                field_name='products_and_services_competitors'
            )
        ]
        return self.summary_list_helper.make_summary_list(heading=heading, rows=rows)

    def export_experience_summary_list(self, heading, fields, url):
        _fields = {f.name: f for f in fields}
        rows = [
            self._make_row(
                url=url,
                key=_fields['has_exported_before'].label,
                field_name='has_exported_before'
            )
        ]
        if self.application_data['has_exported_before'] is False:
            rows.append(
                self._make_row(
                    url=url,
                    key=_fields['has_product_or_service_for_export'].label,
                    field_name='has_product_or_service_for_export'
                )
            )
        return self.summary_list_helper.make_summary_list(heading=heading, rows=rows)

    def export_details_summary_list(self, heading, fields, url):
        if self.application_data['has_exported_before'] is False:
            # Export details is a conditional view. Return None if no data was entered
            return

        _fields = {f.name: f for f in fields}
        rows = [
            self._make_row(
                url=url,
                key=_fields['has_exported_in_last_12_months'].label,
                field_name='has_exported_in_last_12_months'
            ),
            self._make_row(
                url=url,
                key=_fields['export_regions'].label,
                value='\n'.join([
                    dict(_fields['export_regions'].field.choices)[c]
                    for c in self.application_data['export_regions']
                ])
            ),
            self._make_row(
                url=url,
                key=_fields['markets_intending_on_exporting_to'].label,
                value='\n'.join([
                    dict(_fields['markets_intending_on_exporting_to'].field.choices)[c]
                    for c in self.application_data['markets_intending_on_exporting_to']
                ])
            )
        ]
        if self.application_data['is_in_contact_with_dit_trade_advisor']:
            rows.append(self._make_row(
                url=url,
                key=_fields['is_in_contact_with_dit_trade_advisor'].label,
                value='\n'.join([
                    self.application_data['ita_name'],
                    self.application_data['ita_email'],
                    self.application_data['ita_mobile_number'],
                ])
            ))
        else:
            rows.append(self._make_row(
                url=url,
                key=_fields['is_in_contact_with_dit_trade_advisor'].label,
                field_name='is_in_contact_with_dit_trade_advisor'
            ))
        rows += [
            self._make_row(
                url=url,
                key=_fields['export_experience_description'].label,
                field_name='export_experience_description'
            ),
            self._make_row(
                url=url,
                key=_fields['export_strategy'].label,
                field_name='export_strategy'
            )
        ]
        return self.summary_list_helper.make_summary_list(heading=heading, rows=rows)

    def trade_event_details_summary_list(self, heading, fields, url):
        _fields = {f.name: f for f in fields}
        interest_in_event_description_label = _fields['interest_in_event_description'].label.format(
            event_name=self.application_data['event']['name']
        )
        rows = [
            self._make_row(
                url=url,
                key=interest_in_event_description_label,
                field_name='interest_in_event_description'
            )
        ]

        if self.application_data['is_in_contact_with_tcp']:
            rows.append(self._make_row(
                url=url,
                key=_fields['is_in_contact_with_tcp'].label,
                value='\n'.join([
                    self.application_data['tcp_name'],
                    self.application_data['tcp_email'],
                    self.application_data['tcp_mobile_number'],
                ])
            ))
        else:
            rows.append(self._make_row(
                url=url,
                key=_fields['is_in_contact_with_tcp'].label,
                field_name='is_in_contact_with_tcp'
            ))

        rows += [
            self._make_row(
                url=url,
                key=_fields['is_intending_to_exhibit_as_tcp_stand'].label,
                field_name='is_intending_to_exhibit_as_tcp_stand'
            ),
            self._make_row(
                url=url,
                key=_fields['stand_trade_name'].label,
                field_name='stand_trade_name'
            ),
            self._make_row(
                url=url,
                key=_fields['trade_show_experience_description'].label,
                field_name='trade_show_experience_description'
            ),
            self._make_row(
                url=url,
                key=_fields['additional_guidance'].label,
                field_name='additional_guidance'
            ),
        ]

        return self.summary_list_helper.make_summary_list(heading=heading, rows=rows)

    def state_aid_summary_summary_list(self, heading, fields, url):
        state_aids = BackofficeService().list_state_aids(
            grant_application=self.grant_application_link.backoffice_grant_application_id
        )
        row = self._make_row(
            url=url,
            key='Total aid added',
            value=f"£{sum([sa['amount'] for sa in state_aids])}"
        )
        return self.summary_list_helper.make_summary_list(heading=heading, rows=[row])


def send_authentication_email(grant_application):
    auth_link = f'{settings.BASE_URL}{grant_application.resume_url}'
    BackofficeService().send_application_authentication_link_email(grant_application, auth_link)
