from unittest.mock import patch

from bs4 import BeautifulSoup
from django.urls import reverse

from web.grant_applications.services import BackofficeService, BackofficeServiceException
from web.grant_applications.views import SearchCompanyView, SelectCompanyView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import (
    FAKE_GRANT_APPLICATION, FAKE_COMPANY, FAKE_SEARCH_COMPANIES
)
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'create_company', return_value=FAKE_COMPANY)
@patch.object(BackofficeService, 'list_companies', return_value=[FAKE_COMPANY])
@patch.object(BackofficeService, 'search_companies', return_value=FAKE_SEARCH_COMPANIES)
class TestSearchCompanyView(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.gal = GrantApplicationLinkFactory()
        cls.url = reverse('grant-applications:search-company', args=(cls.gal.pk,))

    def test_search_company_get_template(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SearchCompanyView.template_name)

    def test_back_url(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(
            back_html.attrs['href'],
            reverse('grant-applications:event-commitment', args=(self.gal.pk,))
        )

    def test_manual_details_link(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(
            soup.find(id='id_manual_company_details').attrs['href'],
            reverse('grant-applications:manual-company-details', args=(self.gal.pk,))
        )

    def test_search_term_required(self, *mocks):
        response = self.client.post(self.url)
        self.assertFormError(response, 'form', 'search_term', self.form_msgs['required'])

    def test_search_company_saves_search_term(self, *mocks):
        response = self.client.post(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 302)
        mocks[4].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            search_term='company-1'
        )

    def test_form_error_on_update_ga_backoffice_exception(self, *mocks):
        mocks[4].side_effect = BackofficeServiceException
        response = self.client.post(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 200)
        mocks[4].assert_called_once_with(
            grant_application_id=str(self.gal.backoffice_grant_application_id),
            search_term='company-1'
        )
        self.assertFormError(response, 'form', None, self.form_msgs['resubmit'])

    def test_search_company_post_form_redirect_path(self, *mocks):
        response = self.client.post(self.url, data={'search_term': 'company-1'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            expected_url=reverse(
                'grant-applications:select-company', kwargs={'pk': self.gal.pk}
            ) + '?search_term=company-1'
        )

    def test_search_company_post_form_redirect_template(self, *mocks):
        response = self.client.post(self.url, data={'search_term': 'company-1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SelectCompanyView.template_name)

    def test_get_redirects_to_confirmation_if_application_already_sent_for_review(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['sent_for_review'] = True
        mocks[3].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_get_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_active'] = False
        mocks[3].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_post_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_active'] = False
        mocks[3].return_value = fake_grant_application
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))
