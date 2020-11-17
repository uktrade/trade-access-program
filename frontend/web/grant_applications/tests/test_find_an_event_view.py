from unittest.mock import patch
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode

from web.grant_applications.services import BackofficeService
from web.grant_applications.views import FindAnEventView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import (
    FAKE_EVENT, FAKE_PAGINATED_LIST_EVENTS,
    FAKE_GRANT_APPLICATION, FAKE_TRADE_EVENT_AGGREGATES
)
from web.tests.helpers.testcases import BaseTestCase


@patch.object(
    BackofficeService, 'get_trade_event_aggregates', return_value=FAKE_TRADE_EVENT_AGGREGATES
)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(
    BackofficeService, 'list_trade_events', side_effect=[
        [FAKE_EVENT], [FAKE_EVENT], [FAKE_EVENT], FAKE_PAGINATED_LIST_EVENTS, [FAKE_EVENT],
        [FAKE_EVENT], [FAKE_EVENT]
    ]
)
class TestFindAnEventView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:find-an-event', args=(self.gal.pk,))

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, FindAnEventView.template_name)

    def test_back_url(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(
            back_html.attrs['href'],
            reverse('grant-applications:previous-applications', args=(self.gal.pk,))
        )

    def test_initial_filters_are_set_to_all(self, *mocks):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        # Filter by name
        self.assertNotIn('value', soup.find(id='id_filter_by_name').attrs)
        # Filter by start date
        self.assertEqual(
            soup.find(id='id_filter_by_month').find('option', selected=True).text, 'All'
        )
        # Filter by country
        self.assertEqual(
            soup.find(id='id_filter_by_country').find('option', selected=True).text, 'All'
        )
        # Filter by sector
        self.assertEqual(
            soup.find(id='id_filter_by_sector').find('option', selected=True).text, 'All'
        )

    def test_get_redirects_to_confirmation_if_application_already_sent_for_review(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['sent_for_review'] = True
        mocks[2].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_get_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_eligible'] = False
        mocks[2].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_post_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_eligible'] = False
        mocks[2].return_value = fake_grant_application
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_get_does_not_redirect_to_ineligible_if_review_page_has_been_viewed(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_eligible'] = False
        mocks[2].return_value = fake_grant_application

        self.gal.has_viewed_review_page = True
        self.gal.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, FindAnEventView.template_name)

    def test_post_redirects_to_event_page_if_application_review_page_has_been_viewed(self, *mocks):
        self.gal.has_viewed_review_page = True
        self.gal.save()
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse('grant-applications:select-an-event', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )

    def test_error_on_bad_query_param(self, *mocks):
        response = self.client.post(self.url, data={'filter_by_month': 'bad-value'})
        self.assertFormError(
            response, 'form', 'filter_by_month',
            self.form_msgs['invalid-choice'].format('bad-value')
        )

    def test_query_params_sent_on_redirect(self, *mocks):
        params = {
            'filter_by_name': 'Name 1',
            'filter_by_month': '2020-12-01:2020-12-31',
            'filter_by_country': 'Country 1',
            'filter_by_sector': 'Sector 1'
        }
        response = self.client.post(self.url, data=params)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url=reverse(
                'grant_applications:select-an-event', args=(self.gal.pk,)
            ) + f'?{urlencode(params)}'
        )
        parsed_url = urlparse(response.url)
        for k, v in parse_qs(parsed_url.query).items():
            self.assertEqual(params.get(k), v[0])

    def test_redirect_query_params_populate_redirect_form(self, *mocks):
        response = self.client.post(
            self.url,
            follow=True,
            data={
                'filter_by_name': 'Name 1',
                'filter_by_month': '2020-12-01:2020-12-31',
                'filter_by_country': 'Country 1',
                'filter_by_sector': 'Sector 1'
            }
        )
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Filter by name
        self.assertEqual(soup.find(id='id_filter_by_name').attrs['value'], 'Name 1')
        # Filter by start date
        self.assertEqual(
            soup.find(id='id_filter_by_month').find('option', selected=True).text, 'December 2020'
        )
        # Filter by country
        self.assertEqual(
            soup.find(id='id_filter_by_country').find('option', selected=True).text, 'Country 1'
        )
        # Filter by sector
        self.assertEqual(
            soup.find(id='id_filter_by_sector').find('option', selected=True).text, 'Sector 1'
        )

    def test_get_future_aggregate_trade_events_only(self, *mocks):
        response = self.client.get(self.url)
        mocks[3].assert_called_once_with(start_date_from=timezone.now().date())
        self.assertEqual(
            response.context_data['total_trade_events'],
            FAKE_TRADE_EVENT_AGGREGATES['total_trade_events']
        )
        self.assertEqual(
            response.context_data['trade_event_total_months'],
            len(FAKE_TRADE_EVENT_AGGREGATES['trade_event_months'])
        )
