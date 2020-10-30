import logging
from urllib.parse import urljoin

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter, Retry

from web.companies.models import DnbGetCompanyResponse
from web.core.exceptions import DnbServiceClientException, CompaniesHouseApiException

logger = logging.getLogger(__name__)


def _log_hook(response, **kwargs):
    body = response.request.body or 'No content'
    logger.info(f'EXTERNAL {response.request.method} : {response.request.url} : {body}')
    if not response.ok:
        logger.error(f'RESPONSE : {response.status_code} : {response.text}')


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
        self.session.hooks['response'] = [_log_hook, self._raise_for_status]

    @staticmethod
    def _raise_for_status(response, **kwargs):
        try:
            response.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            logger.error(str(e), exc_info=e)
            raise DnbServiceClientException

    def get_company(self, **params):
        results = self.search_companies(**params)
        if results and len(results) == 1:
            return results[0]
        elif len(results) > 1:
            raise DnbServiceClientException(
                f'Search parameters returned too many companies [{len(results)}]'
            )
        return None

    def search_companies(self, **params):
        response = self.session.post(self.company_url, json={'address_country': 'GB', **params})
        return response.json()['results']


def refresh_dnb_company_response_data(company):
    dnb_company_data = DnbServiceClient().get_company(duns_number=company.duns_number)
    if dnb_company_data:
        dnb_get_company_response = DnbGetCompanyResponse.objects.create(
            company=company, dnb_data=dnb_company_data
        )
        return dnb_get_company_response


class CompaniesHouseClient:

    def __init__(self):
        self.base_url = settings.COMPANIES_HOUSE_URL
        self.company_url = settings.COMPANIES_HOUSE_COMPANIES_URL

        self.session = requests.Session()
        self.session.auth = (settings.COMPANIES_HOUSE_API_KEY, "")

        # Attach retry adapter
        retry_strategy = Retry(total=3, status_forcelist=[500], method_whitelist=['GET', 'POST'])
        retry_adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount(self.base_url, retry_adapter)
        self.session.mount(self.company_url, retry_adapter)

        # Attach response hooks
        self.session.hooks['response'] = [_log_hook, self._raise_for_status]

    @staticmethod
    def _raise_for_status(response, **kwargs):
        try:
            response.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            logger.error(str(e), exc_info=e)
            raise CompaniesHouseApiException

    def search_companies(self, search_term):
        return self.session.get(self.company_url, params={'q': search_term}).json()['items']
