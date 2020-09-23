import logging
from urllib.parse import urljoin

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter, Retry

from web.companies.models import DnbGetCompanyResponse, Company
from web.core.exceptions import DnbServiceClientException

logger = logging.getLogger()


def _raise_for_status(response, **kwargs):
    try:
        response.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        logger.error(str(e), exc_info=e)
        raise DnbServiceClientException


def log_hook(response, **kwargs):
    body = response.request.body or b'No content'
    logger.info(
        f'EXTERNAL : REQUEST : {response.request.method} : {response.request.url} : {body.decode()}'
    )
    logger.info(f'EXTERNAL : RESPONSE : {response.status_code} : {response.text}')


class DnbServiceClient:

    def __init__(self):
        self.base_url = settings.DNB_SERVICE_URL
        self.company_url = urljoin(self.base_url, 'companies/search/')

        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Token {settings.DNB_SERVICE_TOKEN}'})

        # Attach retry adapter
        retry_strategy = Retry(total=3, status_forcelist=[500], method_whitelist=['GET', 'POST'])
        retry_adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount(self.base_url, retry_adapter)

        # Attach response hooks
        self.session.hooks['response'] = [log_hook, _raise_for_status]

    @staticmethod
    def _filter_gb(results):
        return [
            r for r in results
            if (r.get('registered_address_country') or r.get('address_country')) == 'GB'
        ]

    def get_company(self, duns_number):
        response = self.session.post(self.company_url, json={'duns_number': duns_number})
        results = self._filter_gb(response.json()['results'])
        if results:
            return results[0]
        return None

    def search_companies(self, search_term):
        response = self.session.post(self.company_url, json={'search_term': search_term})
        return self._filter_gb(results=response.json()['results'])


def save_company_and_dnb_response(duns_number, dnb_company_data=None):
    dnb_company_data = dnb_company_data or {}
    company, _ = Company.objects.get_or_create(
        duns_number=duns_number,
        defaults={'name': dnb_company_data.get('primary_name', 'Could not retrieve company name.')}
    )
    if dnb_company_data:
        DnbGetCompanyResponse.objects.create(company=company, data=dnb_company_data)
    return company
