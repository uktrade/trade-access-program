from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_405_METHOD_NOT_ALLOWED

from web.tests.factories.events import EventFactory
from web.tests.helpers import BaseAPITestCase


class TradeEventsApiTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.event = EventFactory()

    def test_get_trade_event(self, *mocks):
        path = reverse('trade-events-detail', args=(self.event.id,))
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(
            response,
            data_contains={
                'id': self.event.id_str,
                'name': self.event.name,
                'sector': self.event.sector,
                'display_name': self.event.display_name,
            }
        )

    def test_list_trade_events(self, *mocks):
        path = reverse('trade-events-list')
        response = self.client.get(path=path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(response, data_contains=[{'id': self.event.id_str}])

    def test_cannot_create_trade_event(self, *mocks):
        path = reverse('trade-events-list')
        response = self.client.post(path)
        self.assertEqual(response.status_code, HTTP_405_METHOD_NOT_ALLOWED)
