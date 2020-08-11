from unittest.mock import patch

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from web.companies.views import DnbServiceClient
from web.tests.factories.companies import CompanyFactory
from web.tests.factories.users import UserFactory
from web.tests.helpers import BaseAPITestCase


class CompaniesApiTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.company = CompanyFactory(dnb_service_duns_number=1, name='fake-name')

    def test_get_company(self, *mocks):
        path = reverse('companies-detail', args=(self.company.id,))
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(
            response,
            data_contains={
                'id': self.company.id_str,
                'dnb_service_duns_number': 1,
                'name': 'fake-name'
            }
        )

    def test_list_companies(self, *mocks):
        path = reverse('companies-list')
        response = self.client.get(path=path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(response, data_contains=[{'id': self.company.id_str}])

    def test_create_new_company(self, *mocks):
        path = reverse('companies-list')
        response = self.client.post(path, {'dnb_service_duns_number': 2, 'name': 'fake-name'})
        self.assertEqual(response.status_code, HTTP_201_CREATED, msg=response.data)
        self.assert_response_data_contains(response, data_contains={'dnb_service_duns_number': 2})


@patch.object(
    DnbServiceClient,
    'search_companies',
    return_value=[{'primary_name': 'fake-name-1', 'x': 1}, {'primary_name': 'fake-name-2', 'y': 2}]
)
class SearchCompaniesApiTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.client.force_login(UserFactory())

    def test_search_company_names(self, *mocks):
        response = self.client.get(reverse('companies-search'), {'search_term': 'fake-name'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertListEqual(
            response.data,
            [{'primary_name': 'fake-name-1', 'x': 1}, {'primary_name': 'fake-name-2', 'y': 2}]
        )

    def test_search_term_required(self, *mocks):
        response = self.client.get(reverse('companies-search'))
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST, msg=response.data)
        self.assertEqual(response.data['search_term'][0].code, 'required')

    def test_cannot_use_blank_search_term(self, *mocks):
        response = self.client.get(reverse('companies-search'), {'search_term': ''})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST, msg=response.data)
        self.assertEqual(response.data['search_term'][0].code, 'blank')
