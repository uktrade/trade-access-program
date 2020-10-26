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

    def test_get_on_get_ga_backoffice_exception(self, *mocks):
        mocks[1].side_effect = BackofficeServiceException
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, PreviousApplicationsView.template_name)

    def test_post_updates_backoffice_grant_application(self, *mocks):
        response = self.client.post(
            self.url,
            data={'previous_applications': FAKE_GRANT_APPLICATION['previous_applications']}
        )
        self.assertEqual(response.status_code, 302)
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

    def test_post_success_if_get_ga_backoffice_exception(self, *mocks):
        mocks[1].side_effect = BackofficeServiceException
        response = self.client.post(
            self.url,
            data={'previous_applications': FAKE_GRANT_APPLICATION['previous_applications']}
        )
        self.assertEqual(response.status_code, 302)
        mocks[0].assert_called_once_with(
            grant_application_id=self.gal.backoffice_grant_application_id,
            previous_applications=FAKE_GRANT_APPLICATION['previous_applications']
        )
