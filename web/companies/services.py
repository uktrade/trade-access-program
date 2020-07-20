from urllib.parse import urljoin

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter, Retry

from web.core.exceptions import DnbServiceClientException


def _raise_for_status(response):
    try:
        response.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        raise DnbServiceClientException


class DnbServiceClient:

    def __init__(self):
        self.base_url = settings.DNB_SERVICE_URL
        self.company_url = urljoin(self.base_url, 'companies/search/')

        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Token {settings.DNB_SERVICE_TOKEN}'})

        retry_strategy = Retry(total=3, status_forcelist=[500], method_whitelist=['GET', 'POST'])
        retry_adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount(self.base_url, retry_adapter)

    def get_company(self, duns_number):
        response = self.session.post(self.company_url, json={'duns_number': duns_number})
        _raise_for_status(response)
        return response.json()['results'][0]

    def search_companies(self, search_term):
        response = self.session.post(self.company_url, json={'search_term': search_term})
        _raise_for_status(response)
        return response.json()['results']
