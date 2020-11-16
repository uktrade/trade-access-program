from unittest.mock import patch

from bs4 import BeautifulSoup
from django.urls import reverse, resolve

from web.grant_applications.forms import ExportExperienceForm
from web.grant_applications.services import BackofficeService, BackofficeServiceException
from web.grant_applications.views import (
    PreviousApplicationsView, SelectAnEventView, ManualCompanyDetailsView, CompanyDetailsView,
    EventCommitmentView, ContactDetailsView, ExportExperienceView, StateAidSummaryView,
    TradeEventDetailsView, CompanyTradingDetailsView, SelectCompanyView, ExportDetailsView
)
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import (
    FAKE_GRANT_MANAGEMENT_PROCESS,
    FAKE_GRANT_APPLICATION, FAKE_SEARCH_COMPANIES, FAKE_EVENT, FAKE_SECTOR, FAKE_STATE_AID
)
from web.tests.helpers.testcases import BaseTestCase


@patch.object(
    BackofficeService, 'send_grant_application_for_review',
    return_value=FAKE_GRANT_MANAGEMENT_PROCESS
)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'list_state_aids', return_value=[FAKE_STATE_AID, FAKE_STATE_AID])
@patch.object(BackofficeService, 'search_companies', return_value=FAKE_SEARCH_COMPANIES)
@patch.object(BackofficeService, 'list_trade_events', return_value=[FAKE_EVENT])
@patch.object(BackofficeService, 'list_sectors', return_value=[FAKE_SECTOR])
class TestApplicationReviewView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:application-review', args=(self.gal.pk,))

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('core/govt_summary_list.html', [t.name for t in response.templates])

    def test_summary_shows_correct_sections_if_company_found(self, *mocks):
        response = self.client.get(self.url)
        html = BeautifulSoup(response.content, 'html.parser')
        headings = html.find_all(id='id_summary_list_heading')
        self.assertListEqual(
            [h.text for h in headings],
            [
                PreviousApplicationsView.static_context['page']['heading'],
                SelectAnEventView.static_context['page']['heading'],
                EventCommitmentView.static_context['page']['heading'],
                SelectCompanyView.static_context['page']['heading'],
                CompanyDetailsView.static_context['page']['heading'],
                ContactDetailsView.static_context['page']['heading'],
                CompanyTradingDetailsView.static_context['page']['heading'],
                ExportExperienceView.static_context['page']['heading'],
                TradeEventDetailsView.static_context['page']['heading'],
                StateAidSummaryView.static_context['page']['heading'],
            ]
        )

    def test_summary_shows_correct_sections_on_manual_company_entry(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['company'] = None
        fake_grant_application['manual_company_type'] = 'limited company'
        fake_grant_application['manual_company_name'] = 'A Name'
        fake_grant_application['manual_company_address_line_1'] = 'Line 1'
        fake_grant_application['manual_company_address_line_2'] = 'Line 2'
        fake_grant_application['manual_company_address_town'] = 'Town 1'
        fake_grant_application['manual_company_address_county'] = 'County 1'
        fake_grant_application['manual_company_address_postcode'] = 'ZZ0 1ZZ'
        fake_grant_application['manual_time_trading_in_uk'] = '2 to 5 years'
        fake_grant_application['manual_registration_number'] = '12345678'
        fake_grant_application['manual_vat_number'] = '123456789'
        fake_grant_application['manual_website'] = 'www.test.com'
        mocks[4].return_value = fake_grant_application

        response = self.client.get(self.url)
        html = BeautifulSoup(response.content, 'html.parser')
        headings = html.find_all(id='id_summary_list_heading')
        self.assertListEqual(
            [h.text for h in headings],
            [
                PreviousApplicationsView.static_context['page']['heading'],
                SelectAnEventView.static_context['page']['heading'],
                EventCommitmentView.static_context['page']['heading'],
                ManualCompanyDetailsView.static_context['page']['heading'],
                CompanyDetailsView.static_context['page']['heading'],
                ContactDetailsView.static_context['page']['heading'],
                CompanyTradingDetailsView.static_context['page']['heading'],
                ExportExperienceView.static_context['page']['heading'],
                TradeEventDetailsView.static_context['page']['heading'],
                StateAidSummaryView.static_context['page']['heading'],
            ]
        )

    def test_summary_shows_correct_sections_on_export_details_entry(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['has_exported_before'] = True
        fake_grant_application['has_exported_in_last_12_months'] = True
        fake_grant_application['export_regions'] = ['africa']
        fake_grant_application['markets_intending_on_exporting_to'] = ['existing']
        fake_grant_application['is_in_contact_with_dit_trade_advisor'] = False
        fake_grant_application['export_experience_description'] = 'A description'
        fake_grant_application['export_strategy'] = 'A strategy'
        mocks[4].return_value = fake_grant_application

        response = self.client.get(self.url)
        html = BeautifulSoup(response.content, 'html.parser')
        headings = html.find_all(id='id_summary_list_heading')
        self.assertListEqual(
            [h.text for h in headings],
            [
                PreviousApplicationsView.static_context['page']['heading'],
                SelectAnEventView.static_context['page']['heading'],
                EventCommitmentView.static_context['page']['heading'],
                SelectCompanyView.static_context['page']['heading'],
                CompanyDetailsView.static_context['page']['heading'],
                ContactDetailsView.static_context['page']['heading'],
                CompanyTradingDetailsView.static_context['page']['heading'],
                ExportExperienceView.static_context['page']['heading'],
                ExportDetailsView.static_context['page']['heading'],
                TradeEventDetailsView.static_context['page']['heading'],
                StateAidSummaryView.static_context['page']['heading'],
            ]
        )

    def test_summary_export_experience_section_shows_single_row(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['has_exported_before'] = True
        mocks[4].return_value = fake_grant_application

        response = self.client.get(self.url)
        html = BeautifulSoup(response.content, 'html.parser').find(id='id_summary_list_7')

        rows = html.find_all(attrs={'class': 'govuk-summary-list__row'})
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            html.find(id='id_summary_list_key_0').text,
            ExportExperienceForm.base_fields['has_exported_before'].label
        )
        self.assertIsNone(html.find(id='id_summary_list_key_1'))

    def test_summary_export_experience_section_shows_all_rows(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['has_exported_before'] = False
        mocks[4].return_value = fake_grant_application

        response = self.client.get(self.url)
        html = BeautifulSoup(response.content, 'html.parser').find(id='id_summary_list_7')

        rows = html.find_all(attrs={'class': 'govuk-summary-list__row'})
        self.assertEqual(len(rows), 2)
        self.assertEqual(
            html.find(id='id_summary_list_key_0').text,
            ExportExperienceForm.base_fields['has_exported_before'].label
        )
        self.assertEqual(
            html.find(id='id_summary_list_key_1').text,
            ExportExperienceForm.base_fields['has_product_or_service_for_export'].label
        )

    def test_post_redirects(self, *mocks):
        self.client.get(self.url)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        redirect = resolve(response.url)
        self.assertEqual(redirect.kwargs['pk'], str(self.gal.id))
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_send_grant_application_for_review(self, *mocks):
        self.client.get(self.url)
        self.client.post(self.url)
        self.gal.refresh_from_db()
        self.assertIn('application_summary', self.client.session)
        mocks[5].assert_called_once_with(
            str(self.gal.backoffice_grant_application_id),
            application_summary=self.client.session['application_summary']
        )

    def test_backoffice_exception_on_send_grant_application_for_review(self, *mocks):
        mocks[5].side_effect = BackofficeServiceException
        self.client.get(self.url)
        response = self.client.post(self.url)
        self.assertFormError(response, 'form', None, self.form_msgs['resubmit'])

    def test_get_redirects_to_confirmation_if_application_already_sent_for_review(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['sent_for_review'] = True
        mocks[4].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_get_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_active'] = False
        mocks[4].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_post_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_active'] = False
        mocks[4].return_value = fake_grant_application
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))
