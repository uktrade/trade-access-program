from django.utils.datetime_safe import date
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_405_METHOD_NOT_ALLOWED

from web.tests.factories.events import EventFactory
from web.tests.helpers import BaseAPITestCase


class TradeEventsApiTests(BaseAPITestCase):

    def test_get_trade_event(self, *mocks):
        event = EventFactory()
        path = reverse('trade-events:trade-events-detail', args=(event.id,))
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
        path = reverse('trade-events:trade-events-list')
        response = self.client.get(path=path)
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(response, data_contains=[{'id': event.id_str}])

    def test_list_trade_events_paginated(self, *mocks):
        EventFactory()
        event_2 = EventFactory()
        path = reverse('trade-events:trade-events-list')
        response = self.client.get(path=path, data={'page': 2, 'page_size': 1})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(response.data['count'], 2)  # total event count
        self.assertEqual(len(response.data['results']), 1)
        self.assert_data_contains(response.data['results'][0], {'id': event_2.id_str})

    def test_list_trade_events_with_name_search_term(self, *mocks):
        event_1 = EventFactory(name='AB')
        event_2 = EventFactory(name='ABCD')
        path = reverse('trade-events:trade-events-list')
        response = self.client.get(path=path, data={'search': 'AB'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], event_1.id_str)
        self.assertEqual(response.data[1]['id'], event_2.id_str)

    def test_list_trade_events_with_name_filter(self, *mocks):
        event = EventFactory(name='AB')
        EventFactory(name='ABCD')
        path = reverse('trade-events:trade-events-list')
        response = self.client.get(path=path, data={'name': 'AB'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], event.id_str)

    def test_list_trade_events_with_country_filter(self, *mocks):
        event = EventFactory(country='Country 1')
        EventFactory(country='Country 2')
        path = reverse('trade-events:trade-events-list')
        response = self.client.get(path=path, data={'country': 'Country 1'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], event.id_str)

    def test_list_trade_events_with_sector_filter(self, *mocks):
        event = EventFactory(sector='Sector 1')
        EventFactory(sector='Sector 2')
        path = reverse('trade-events:trade-events-list')
        response = self.client.get(path=path, data={'sector': 'Sector 1'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], event.id_str)

    def test_list_trade_events_with_start_date_exact_filter(self, *mocks):
        event = EventFactory(start_date=date(year=2020, month=10, day=5))
        EventFactory(start_date=date(year=2020, month=10, day=4))
        path = reverse('trade-events:trade-events-list')
        response = self.client.get(path=path, data={'start_date': '2020-10-05'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], event.id_str)

    def test_list_trade_events_with_start_date_after_filter(self, *mocks):
        EventFactory(start_date=date(year=2020, month=10, day=1))
        EventFactory(start_date=date(year=2020, month=10, day=2))
        EventFactory(start_date=date(year=2020, month=10, day=3))
        EventFactory(start_date=date(year=2020, month=10, day=4))
        path = reverse('trade-events:trade-events-list')
        response = self.client.get(path=path, data={'start_date_range_after': '2020-10-02'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 3)

    def test_list_trade_events_with_start_date_before_filter(self, *mocks):
        EventFactory(start_date=date(year=2020, month=10, day=1))
        EventFactory(start_date=date(year=2020, month=10, day=2))
        EventFactory(start_date=date(year=2020, month=10, day=3))
        EventFactory(start_date=date(year=2020, month=10, day=4))
        path = reverse('trade-events:trade-events-list')
        response = self.client.get(path=path, data={'start_date_range_before': '2020-10-02'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 2)

    def test_list_trade_events_with_end_date_after_filter(self, *mocks):
        EventFactory(end_date=date(year=2020, month=10, day=1))
        EventFactory(end_date=date(year=2020, month=10, day=2))
        EventFactory(end_date=date(year=2020, month=10, day=3))
        EventFactory(end_date=date(year=2020, month=10, day=4))
        path = reverse('trade-events:trade-events-list')
        response = self.client.get(path=path, data={'end_date_range_after': '2020-10-02'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 3)

    def test_list_trade_events_with_end_date_before_filter(self, *mocks):
        EventFactory(end_date=date(year=2020, month=10, day=1))
        EventFactory(end_date=date(year=2020, month=10, day=2))
        EventFactory(end_date=date(year=2020, month=10, day=3))
        EventFactory(end_date=date(year=2020, month=10, day=4))
        path = reverse('trade-events:trade-events-list')
        response = self.client.get(path=path, data={'end_date_range_before': '2020-10-02'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data), 2)

    def test_cannot_create_trade_event(self, *mocks):
        path = reverse('trade-events:trade-events-list')
        response = self.client.post(path)
        self.assertEqual(response.status_code, HTTP_405_METHOD_NOT_ALLOWED)


class TradeEventsAggregatesApiTests(BaseAPITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.events = EventFactory.create_batch(
            size=2, start_date='2020-12-10', end_date='2020-12-13'
        )
        cls.events.append(
            EventFactory(start_date='2020-10-01', end_date='2020-10-03')
        )
        cls.events.append(
            EventFactory(start_date='2021-02-28', end_date='2020-03-02')
        )
        cls.path = reverse('trade-events:aggregate')

    def test_get_trade_event_aggregate_data(self, *mocks):
        response = self.client.get(self.path, data={'start_date_from': '2020-12-01'})
        self.assertEqual(response.status_code, HTTP_200_OK, msg=response.data)
        self.assert_response_data_contains(
            response,
            data_contains={
                'total_trade_events': 3,
                'trade_event_months': [
                    'December 2020',
                    'February 2021'
                ]
            }
        )
