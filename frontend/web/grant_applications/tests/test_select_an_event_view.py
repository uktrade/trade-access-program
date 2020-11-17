import re
from unittest.mock import patch

from bs4 import BeautifulSoup
from django.urls import reverse

from web.grant_applications.services import BackofficeService, BackofficeServiceException
from web.grant_applications.views import SelectAnEventView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import (
    FAKE_PAGINATED_LIST_EVENTS, FAKE_EVENT,
    FAKE_GRANT_APPLICATION
)
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(
    BackofficeService, 'list_trade_events', side_effect=[
        FAKE_PAGINATED_LIST_EVENTS, [FAKE_EVENT], [FAKE_EVENT], [FAKE_EVENT],
        FAKE_PAGINATED_LIST_EVENTS, [FAKE_EVENT], [FAKE_EVENT], [FAKE_EVENT]
    ]
)
class TestSelectAnEventView(BaseTestCase):
    page_size = SelectAnEventView.events_page_size

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:select-an-event', args=(self.gal.pk,))

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SelectAnEventView.template_name)

    def test_back_url(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(
            back_html.attrs['href'],
            reverse('grant-applications:find-an-event', args=(self.gal.pk,))
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

    def test_get_defaults_to_event_page_1(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        mocks[0].assert_any_call(page=1, page_size=self.page_size)

    def test_get_with_event_page(self, *mocks):
        response = self.client.get(self.url, data={'page': 2})
        self.assertEqual(response.status_code, 200)
        mocks[0].assert_any_call(page=2, page_size=self.page_size)

    def test_get_request_event_initial_is_backoffice_event_if_exists(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        selected_event = soup.find(attrs={'class': 'govuk-radios__input'}, checked=True)
        self.assertEqual(selected_event.attrs['value'], FAKE_GRANT_APPLICATION['event']['id'])

    def test_get_on_list_events_backoffice_exception(self, *mocks):
        mocks[0].side_effect = BackofficeServiceException
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        html_elements = soup.find_all(id=re.compile(r'^id_no_matching_events_\d'))
        self.assertEqual(len(html_elements), 3)

    @patch.object(BackofficeService, 'get_grant_application')
    def test_initial_when_no_event_is_set(self, *mocks):
        mocks[3].return_value = FAKE_GRANT_APPLICATION.copy()
        mocks[3].return_value['event'] = None

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        all_event_radios = soup.find_all(attrs={'class': 'govuk-radios__input'})
        for event_radio in all_event_radios:
            self.assertNotIn('checked', event_radio.attrs)

    def test_post_redirects(self, *mocks):
        response = self.client.post(self.url, data={'event': FAKE_EVENT['id']})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url=reverse(SelectAnEventView.success_url_name, args=(self.gal.pk,))
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
        mocks[1].return_value = fake_grant_application

        self.gal.has_viewed_review_page = True
        self.gal.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SelectAnEventView.template_name)

    def test_post_redirects_to_review_page_if_application_review_page_has_been_viewed(self, *mocks):
        self.gal.has_viewed_review_page = True
        self.gal.save()
        response = self.client.post(self.url, data={'event': FAKE_EVENT['id']})
        self.assertRedirects(
            response,
            reverse('grant-applications:application-review', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )

    def test_event_is_saved_on_form_continue_button(self, *mocks):
        response = self.client.post(self.url, data={'event': FAKE_EVENT['id']})
        self.assertEqual(response.status_code, 302)
        mocks[1].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            event=FAKE_EVENT['id']
        )

    def test_filter_by_name(self, *mocks):
        response = self.client.get(self.url, data={'filter_by_name': 'AB'})
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.find(id='id_filter_by_name').attrs['value'], 'AB')
        # Use name filter as a search_term to the backoffice api
        mocks[0].assert_any_call(page=1, page_size=self.page_size, search='AB')

    def test_filter_by_month(self, *mocks):
        response = self.client.get(self.url, data={'filter_by_month': '2020-12-01:2020-12-31'})
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(
            soup.find(id='id_filter_by_month').find('option', selected=True).text,
            'December 2020'
        )
        mocks[0].assert_any_call(
            page=1,
            page_size=self.page_size,
            start_date_range_after='2020-12-01',
            end_date_range_before='2020-12-31'
        )

    def test_filter_by_country(self, *mocks):
        response = self.client.get(self.url, data={'filter_by_country': 'Country 1'})
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(
            soup.find(id='id_filter_by_country').find('option', selected=True).text,
            FAKE_EVENT['country']
        )
        mocks[0].assert_any_call(page=1, page_size=self.page_size, country='Country 1')

    def test_filter_by_sector(self, *mocks):
        response = self.client.get(self.url, data={'filter_by_sector': 'Sector 1'})
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(
            soup.find(id='id_filter_by_sector').find('option', selected=True).text,
            FAKE_EVENT['sector']
        )
        mocks[0].assert_any_call(page=1, page_size=self.page_size, sector='Sector 1')

    def test_no_matching_events_text_is_shown(self, *mocks):
        mocks[0].side_effect = None
        mocks[0].return_value = []
        response = self.client.get(self.url, data={'filter_by_name': 'Bla Bla Bla'})
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        html_elements = soup.find_all(id=re.compile(r'^id_no_matching_events_\d'))
        self.assertEqual(len(html_elements), 3)

    def test_event_required_on_form_button_submit(self, *mocks):
        response = self.client.post(self.url)
        self.assertFormError(response, 'form', 'event', self.form_msgs['required'])
