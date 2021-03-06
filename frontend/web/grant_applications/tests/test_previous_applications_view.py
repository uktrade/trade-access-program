from unittest.mock import patch

from bs4 import BeautifulSoup
from django.urls import reverse

from web.grant_applications.services import BackofficeService, BackofficeServiceException
from web.grant_applications.views import PreviousApplicationsView
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import FAKE_SEARCH_COMPANIES, FAKE_GRANT_APPLICATION
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'search_companies', return_value=FAKE_SEARCH_COMPANIES)
@patch.object(BackofficeService, 'get_grant_application', return_value=FAKE_GRANT_APPLICATION)
@patch.object(BackofficeService, 'update_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestPreviousApplicationsView(BaseTestCase):

    def setUp(self):
        self.gal = GrantApplicationLinkFactory(
            backoffice_grant_application_id=FAKE_GRANT_APPLICATION['id']
        )
        self.url = reverse('grant-applications:previous-applications', args=(self.gal.pk,))

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, PreviousApplicationsView.template_name)

    def test_back_url(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(back_html.attrs['href'], reverse("grant-applications:before-you-start"))

    def test_heading(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        html = BeautifulSoup(response.content, 'html.parser').find(id='id_page_heading')
        self.assertEqual(html.text, PreviousApplicationsView.extra_context['page']['heading'])

    def test_get_on_get_ga_backoffice_exception(self, *mocks):
        mocks[1].side_effect = BackofficeServiceException
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, PreviousApplicationsView.template_name)

    def test_get_redirects_to_confirmation_if_application_already_sent_for_review(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['sent_for_review'] = True
        mocks[1].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(
            response, reverse('grant-applications:confirmation', args=(self.gal.pk,))
        )

    def test_get_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_eligible'] = False
        mocks[1].return_value = fake_grant_application
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('grant-applications:ineligible'))

    def test_post_redirects_to_ineligible_if_application_is_not_active(self, *mocks):
        fake_grant_application = FAKE_GRANT_APPLICATION.copy()
        fake_grant_application['is_eligible'] = False
        mocks[1].return_value = fake_grant_application
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
        self.assertTemplateUsed(response, PreviousApplicationsView.template_name)

    def test_post_redirects_to_review_page_if_application_review_page_has_been_viewed(self, *mocks):
        self.gal.has_viewed_review_page = True
        self.gal.save()
        response = self.client.post(
            self.url,
            data={'previous_applications': FAKE_GRANT_APPLICATION['previous_applications']}
        )
        self.assertRedirects(
            response,
            reverse('grant-applications:application-review', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )

    def test_post_updates_backoffice_grant_application(self, *mocks):
        response = self.client.post(
            self.url,
            data={'previous_applications': FAKE_GRANT_APPLICATION['previous_applications']}
        )
        self.assertRedirects(
            response,
            expected_url=reverse('grant-applications:find-an-event', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )
        mocks[0].assert_called_once_with(
            grant_application_id=self.gal.backoffice_grant_application_id,
            previous_applications=FAKE_GRANT_APPLICATION['previous_applications']
        )

    def test_initial_data_populated_from_grant_application_object(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        selected_radio = soup.find('input', checked=True)
        self.assertEqual(
            selected_radio.attrs['value'],
            str(FAKE_GRANT_APPLICATION['previous_applications'])
        )

    def test_previous_applications_required(self, *mocks):
        response = self.client.post(self.url)
        self.assertFormError(response, 'form', 'previous_applications', self.form_msgs['required'])

    def test_previous_applications_cannot_be_blank(self, *mocks):
        response = self.client.post(self.url, data={'previous_applications': ''})
        self.assertFormError(response, 'form', 'previous_applications', self.form_msgs['required'])

    def test_form_error_on_update_ga_backoffice_exception(self, *mocks):
        mocks[0].side_effect = BackofficeServiceException
        response = self.client.post(
            self.url,
            data={'previous_applications': FAKE_GRANT_APPLICATION['previous_applications']}
        )
        self.assertEqual(response.status_code, 200)
        mocks[0].assert_called_once_with(
            grant_application_id=FAKE_GRANT_APPLICATION['id'],
            previous_applications=FAKE_GRANT_APPLICATION['previous_applications']
        )
        self.assertFormError(response, 'form', None, self.form_msgs['resubmit'])

    def test_post_form_error_if_get_ga_backoffice_exception(self, *mocks):
        mocks[1].side_effect = BackofficeServiceException
        response = self.client.post(
            self.url,
            data={'previous_applications': FAKE_GRANT_APPLICATION['previous_applications']}
        )
        self.assertRedirects(
            response,
            reverse('grant-applications:find-an-event', args=(self.gal.pk,)),
            fetch_redirect_response=False
        )
        mocks[0].assert_called_once_with(
            grant_application_id=self.gal.backoffice_grant_application_id,
            previous_applications=FAKE_GRANT_APPLICATION['previous_applications']
        )
