from unittest.mock import patch

from bs4 import BeautifulSoup
from django.urls import reverse

from web.grant_applications.services import BackofficeServiceException, BackofficeService
from web.grant_applications.views import SelectCompanyView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import (
    FAKE_GRANT_APPLICATION, FAKE_COMPANY, FAKE_SEARCH_COMPANIES
)
from web.tests.helpers.testcases import BaseTestCase, LogCaptureMixin


@patch.object(BackofficeService, 'create_company', return_value=FAKE_COMPANY)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'list_companies', return_value=[FAKE_COMPANY])
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'search_companies', return_value=FAKE_SEARCH_COMPANIES)
class TestSelectCompanyView(LogCaptureMixin, BaseTestCase):

    def setUp(self):
        super().setUp()
        self.gal = GrantApplicationLinkFactory()
        self.url = reverse('grant-applications:select-company', args=(self.gal.pk,))

    def test_get_with_no_search_term_redirects_to_search_company_page(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('grant-applications:search-company', args=(self.gal.pk,))
        )

    def test_get_with_empty_search_term_redirects_to_search_company_page(self, *mocks):
        response = self.client.get(self.url, data={'search_term': ''})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('grant-applications:search-company', args=(self.gal.pk,))
        )

    def test_get_response_content(self, *mocks):
        response = self.client.get(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SelectCompanyView.template_name)
        self.assertIn(FAKE_GRANT_APPLICATION['company']['name'], response.content.decode())

    def test_html_number_of_matches(self, *mocks):
        response = self.client.get(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 200)
        html = BeautifulSoup(response.content, 'html.parser').find(id='id_matches_text')
        self.assertEqual(html.text, 'We found 1 match')

    def test_html_number_of_matches_pluralised(self, *mocks):
        mocks[0].return_value = [FAKE_SEARCH_COMPANIES[0] for _ in range(3)]
        response = self.client.get(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 200)
        html = BeautifulSoup(response.content, 'html.parser').find(id='id_matches_text')
        self.assertEqual(html.text, 'We found 3 matches')

    def test_get_with_primary_name_style_search_term(self, *mocks):
        self.client.get(self.url, data={'search_term': 'company-1'})
        mocks[0].assert_called_once_with(primary_name='company-1')

    def test_get_with_registration_number_style_search_term(self, *mocks):
        self.client.get(self.url, data={'search_term': '01234567'})
        mocks[0].assert_called_once_with(registration_numbers=['01234567'])

    def test_details_not_listed(self, *mocks):
        response = self.client.get(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 200)
        link_html = BeautifulSoup(response.content, 'html.parser').find(id='id_details_not_listed')
        self.assertEqual(
            link_html.attrs['href'],
            reverse('grant-applications:manual-company-details', args=(self.gal.pk,))
        )

    def test_html_when_no_company_found(self, *mocks):
        mocks[0].return_value = []
        response = self.client.get(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 200)
        html = BeautifulSoup(response.content, 'html.parser').find(id='id_matches_text')
        self.assertEqual(html.text, 'We found no matching businesses')

    def test_get_on_search_companies_backoffice_service_exception(self, *mocks):
        mocks[0].side_effect = BackofficeServiceException
        response = self.client.get(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(FAKE_GRANT_APPLICATION['company']['name'], response.content.decode())

    def test_post_required_fields(self, *mocks):
        response = self.client.post(self.url)
        self.assertFormError(response, 'form', 'duns_number', self.form_msgs['required'])

    def test_post_form_redirect_path(self, *mocks):
        response = self.client.post(
            self.url, data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url=reverse('grant-applications:company-details', args=(self.gal.pk,))
        )

    def test_post_creates_backoffice_company(self, m_search_companies, m_update_grant_application,
                                             m_list_companies, m_get_grant_application,
                                             m_create_company):
        # mock out that list_companies returns nothing
        # so that create_company gets called to create the company
        m_list_companies.return_value = []
        response = self.client.post(
            self.url, data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']}
        )
        self.assertEqual(response.status_code, 302)
        m_create_company.assert_called_once_with(
            duns_number=str(FAKE_GRANT_APPLICATION['company']['duns_number']),
            registration_number=FAKE_GRANT_APPLICATION['company']['registration_number'],
            name=FAKE_GRANT_APPLICATION['company']['name']
        )

    def test_post_list_companies_finds_too_many_backoffice_companies(self, m_search_companies,
                                                                     m_update_grant_application,
                                                                     m_list_companies,
                                                                     m_get_grant_application,
                                                                     m_create_company):
        # mock out that list_companies returns more than 1 companies
        m_list_companies.return_value = [FAKE_COMPANY, FAKE_COMPANY]

        response = self.client.post(
            self.url, data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']}
        )

        # This means there is a problem in the backoffice api
        self.assertFormError(response, 'form', None, self.form_msgs['resubmit'])

        m_create_company.assert_not_called()
        self.log_capture.check_present(
            ('web.grant_applications.services', 'ERROR', 'Too many companies'),
        )

    def test_post_list_companies_causes_backoffice_service_exception(self, *mocks):
        mocks[2].side_effect = BackofficeServiceException
        response = self.client.post(
            self.url,
            data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']},
            follow=True
        )
        self.assertFormError(response, 'form', None, self.form_msgs['resubmit'])

    def test_post_updates_backoffice_grant_application_company(self, m_search_companies,
                                                               m_update_grant_application,
                                                               m_list_companies,
                                                               m_get_grant_application,
                                                               m_create_company):
        response = self.client.post(
            self.url, data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']}
        )
        self.assertEqual(response.status_code, 302)
        m_search_companies.assert_called_with(
            duns_number=FAKE_GRANT_APPLICATION['company']['duns_number']
        )
        m_update_grant_application.assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            company=FAKE_COMPANY['id'],
            # Set manual company details to None in case they have previously been set
            manual_company_type=None,
            manual_company_name=None,
            manual_company_address_line_1=None,
            manual_company_address_line_2=None,
            manual_company_address_town=None,
            manual_company_address_county=None,
            manual_company_address_postcode=None,
            manual_time_trading_in_uk=None,
            manual_registration_number=None,
            manual_vat_number=None,
            manual_website=None
        )

    def test_get_redirects_to_confirmation_if_application_already_sent_for_review(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['sent_for_review'] = True
        mocks[3].return_value = fake_grant_application
        response = self.client.get(self.url, data={'search_term': 'hello'})
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_get_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_eligible'] = False
        mocks[3].return_value = fake_grant_application
        response = self.client.get(self.url, data={'search_term': 'hello'})
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_post_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_eligible'] = False
        mocks[3].return_value = fake_grant_application
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_get_does_not_redirect_to_ineligible_if_review_page_has_been_viewed(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_eligible'] = False
        mocks[1].return_value = fake_grant_application

        self.gal.has_viewed_review_page = True
        self.gal.save()

        response = self.client.get(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SelectCompanyView.template_name)

    def test_post_redirects_to_review_page_if_application_review_page_has_been_viewed(self, *mocks):
        self.gal.has_viewed_review_page = True
        self.gal.save()
        response = self.client.post(
            self.url,
            data={'duns_number': FAKE_GRANT_APPLICATION['company']['duns_number']}
        )
        self.assertRedirects(
            response,
            reverse('grant-applications:application-review', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )
