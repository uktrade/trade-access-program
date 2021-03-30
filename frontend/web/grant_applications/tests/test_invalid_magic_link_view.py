from unittest.mock import patch

from django.urls import reverse

from web.grant_applications.views import InvalidMagicLinkView
from web.grant_applications.services import BackofficeService
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION
from web.tests.helpers.testcases import BaseTestCase


class TestInvalidMagicLinkView(BaseTestCase):

    def setUp(self):
        self.url = reverse('grant-applications:invalid-magic-link')
        self.user_email = 'user@test.com'
        self.gal = GrantApplicationLinkFactory(
            email=self.user_email,
            backoffice_grant_application_id=FAKE_GRANT_APPLICATION['id']
        )

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, InvalidMagicLinkView.template_name)

    @patch.object(
        BackofficeService,
        'send_resume_application_email',
        return_value={}
    )
    @patch.object(
        BackofficeService,
        'get_grant_application',
        return_value=FAKE_GRANT_APPLICATION
    )
    def test_post(self, *mocks):
        response = self.client.post(
            self.url,
            data={
                'email': self.user_email
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('grant_applications:check-your-email'),
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
