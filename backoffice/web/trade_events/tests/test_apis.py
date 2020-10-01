from django.utils.datetime_safe import date
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_405_METHOD_NOT_ALLOWED

from web.tests.factories.events import EventFactory
from web.tests.helpers import BaseAPITestCase


class TradeEventsApiTests(BaseAPITestCase):

    def test_get_trade_event(self, *mocks):
        event = EventFactory()
        path = reverse('trade-events-detail', args=(event.id,))
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(
            response,
            data_contains={
                'id': event.id_str,
                'name': event.name,
                'sector': event.sector,
                'display_name': event.display_name,
            }
        )

    def test_list_trade_events(self, *mocks):
        event = EventFactory()
        path = reverse('trade-events-list')
        response = self.client.get(path=path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(response, data_contains=[{'id': event.id_str}])

    def test_list_trade_events_with_start_date_filter(self, *mocks):
        event = EventFactory(start_date=date(year=2020, month=10, day=5))
        EventFactory(start_date=date(year=2020, month=10, day=4))
        path = reverse('trade-events-list')
        response = self.client.get(path=path, data={'start_date': '2020-10-05'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], event.id_str)

    def test_list_trade_events_with_country_filter(self, *mocks):
        event = EventFactory(country='Country 1')
        EventFactory(country='Country 2')
        path = reverse('trade-events-list')
        response = self.client.get(path=path, data={'country': 'Country 1'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], event.id_str)

    def test_list_trade_events_with_sector_filter(self, *mocks):
        event = EventFactory(sector='Sector 1')
        EventFactory(sector='Sector 2')
        path = reverse('trade-events-list')
        response = self.client.get(path=path, data={'sector': 'Sector 1'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], event.id_str)

    def test_cannot_create_trade_event(self, *mocks):
        path = reverse('trade-events-list')
        response = self.client.post(path)
        self.assertEqual(response.status_code, HTTP_405_METHOD_NOT_ALLOWED)
