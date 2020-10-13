from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_405_METHOD_NOT_ALLOWED

from web.tests.factories.sector import SectorFactory
from web.tests.helpers import BaseAPITestCase


class SectorsApiTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.sector = SectorFactory()

    def test_get_sector(self, *mocks):
        path = reverse('sectors:sectors-detail', args=(self.sector.id,))
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(
            response,
            data_contains={
                'id': self.sector.id_str,
                'name': self.sector.name,
            }
        )

    def test_list_sectors(self, *mocks):
        path = reverse('sectors:sectors-list')
        response = self.client.get(path=path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(response, data_contains=[{'id': self.sector.id_str}])

    def test_cannot_create_sector(self, *mocks):
        path = reverse('sectors:sectors-list')
        response = self.client.post(path)
        self.assertEqual(response.status_code, HTTP_405_METHOD_NOT_ALLOWED)
