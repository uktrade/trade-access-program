from django.urls import reverse

from web.grant_applications.constants import APPLICATION_BACKOFFICE_ID_SESSION_KEY
from web.grant_applications.views import ApplicationIndexView
from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION
from web.tests.helpers.testcases import BaseTestCase


class TestApplicationIndexView(BaseTestCase):

    def setUp(self):
        self.url = reverse('grant-applications:index')
        self.attempted_application_id = FAKE_GRANT_APPLICATION['id']

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ApplicationIndexView.template_name)

    def test_get_attempted_user_email(self):
        session = self.client.session
        session[APPLICATION_BACKOFFICE_ID_SESSION_KEY] = self.attempted_application_id
        session.save()
        self.assertEqual(
            self.client.session[APPLICATION_BACKOFFICE_ID_SESSION_KEY],
            self.attempted_application_id
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get(APPLICATION_BACKOFFICE_ID_SESSION_KEY), None)
        self.assertTemplateUsed(response, ApplicationIndexView.template_name)
