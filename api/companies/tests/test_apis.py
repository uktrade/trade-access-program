from rest_framework.status import HTTP_200_OK, HTTP_405_METHOD_NOT_ALLOWED
from rest_framework.reverse import reverse

from api.tests.factories.companies import CompanyFactory
from api.tests.helpers import BaseTestCase


class CompaniesApiTests(BaseTestCase):

    def setUp(self):
        super().setUpClass()
        self.company = CompanyFactory(registration_number=1)

    def test_get_company(self):
        path = reverse('companies-detail', args=(self.company.id,))
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(response, data_contains={'id': self.company.id_str})

    def test_list_companies(self):
        path = reverse('companies-list')
        response = self.client.get(path=path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(response, data_contains=[{'id': self.company.id_str}])

    def test_filter_by_company_registration_number(self):
        path = reverse('companies-list')
        company_2 = CompanyFactory(registration_number=2)
        response = self.client.get(path, {'registration_number': 2})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(response, data_contains=[{'id': company_2.id_str}])

    def test_cannot_create_company(self):
        path = reverse('companies-list')
        response = self.client.post(path=path)
        self.assertEqual(response.status_code, HTTP_405_METHOD_NOT_ALLOWED, msg=response.data)
