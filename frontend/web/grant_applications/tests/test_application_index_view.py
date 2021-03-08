from django.urls import reverse

from web.grant_applications.constants import APPLICATION_EMAIL_SESSION_KEY
from web.grant_applications.views import ApplicationIndexView
from web.tests.helpers.testcases import BaseTestCase


class TestApplicationIndexView(BaseTestCase):

    def setUp(self):
        self.url = reverse('grant-applications:index')
        self.attempted_user_email = 'attempted@email.com'

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ApplicationIndexView.template_name)

    def test_get_attempted_user_email(self):
        session = self.client.session
        session[APPLICATION_EMAIL_SESSION_KEY] = self.attempted_user_email
        session.save()
        self.assertEqual(
            self.client.session[APPLICATION_EMAIL_SESSION_KEY],
            self.attempted_user_email
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get(APPLICATION_EMAIL_SESSION_KEY), None)
        self.assertTemplateUsed(response, ApplicationIndexView.template_name)
