from bs4 import BeautifulSoup
from unittest.mock import patch
from django.urls import reverse

from web.grant_applications.views import ContinueApplicationView
from web.grant_applications.services import BackofficeService
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION
from web.tests.helpers.testcases import BaseTestCase


class TestContinueApplicationView(BaseTestCase):

    def setUp(self):
        self.url = reverse('grant-applications:continue-application-email')
        self.user_email = 'user@test.com'
        self.gal = GrantApplicationLinkFactory(email=self.user_email)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ContinueApplicationView.template_name)

    def test_back_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(back_html.attrs['href'], reverse('grant-applications:index'))

    @patch.object(
        BackofficeService,
        'get_grant_application',
        return_value=FAKE_GRANT_APPLICATION
    )
    @patch.object(
        BackofficeService,
        'send_resume_application_email',
        return_value={}
    )
    def test_post_email_matching_with_grant_application(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'email': self.user_email
            }
        )
        self.assertRedirects(
            response,
            reverse(ContinueApplicationView.success_url_name),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True
        )

    def test_post_email_non_matching_with_grant_application(self):
        response = self.client.post(
            self.url,
            data={
                'email': 'no-user@test.com'
            }
        )
        self.assertRedirects(
            response,
            reverse('grant-applications:no-application-found'),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True
        )

    def test_email_form_validation(self):
        invalid_email = 'user,email@test.com'
        response = self.client.post(
            self.url,
            data={
                'email': invalid_email
            }
        )
        msg = 'Enter a valid email address.'
        self.assertFormError(response, 'form', 'email', msg)
