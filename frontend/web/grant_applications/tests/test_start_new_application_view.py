from unittest.mock import patch

from bs4 import BeautifulSoup
from django.urls import reverse

from web.grant_applications.models import GrantApplicationLink
from web.grant_applications.services import BackofficeService
from web.grant_applications.views import StartNewApplicationView
from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION
from web.tests.helpers.testcases import BaseTestCase


class TestStartNewApplicationView(BaseTestCase):

    def setUp(self):
        self.url = reverse('grant-applications:new-application-email')

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, StartNewApplicationView.template_name)

    def test_back_url(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(back_html.attrs['href'], reverse('grant-applications:before-you-start'))

    @patch.object(
        BackofficeService,
        'send_resume_application_email',
        return_value={}
    )
    @patch.object(
        BackofficeService,
        'create_grant_application',
        return_value=FAKE_GRANT_APPLICATION
    )
    def test_post_creates_backoffice_grant_application(self, *mocks):
        user_email = 'user@test.com'
        response = self.client.post(
            self.url,
            data={
                'email': user_email
            }
        )
        self.assertRedirects(
            response,
            reverse(StartNewApplicationView.success_url_name),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTrue(
            GrantApplicationLink.objects.filter(
                backoffice_grant_application_id=FAKE_GRANT_APPLICATION['id'],
                email=user_email
            ).exists()
        )
        mocks[0].assert_called_once_with()

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
