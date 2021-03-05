from unittest.mock import patch

from bs4 import BeautifulSoup
from django.urls import reverse

from web.grant_applications.services import BackofficeService, BackofficeServiceException
from web.grant_applications.views import BeforeYouStartView
from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION
from web.tests.helpers.testcases import BaseTestCase


@patch.object(BackofficeService, 'create_grant_application', return_value=FAKE_GRANT_APPLICATION)
class TestBeforeYouStartView(BaseTestCase):

    def setUp(self):
        self.url = reverse('grant-applications:before-you-start')

    def test_get(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, BeforeYouStartView.template_name)

    def test_back_url(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        back_html = BeautifulSoup(response.content, 'html.parser').find(id='id_back_link')
        self.assertEqual(back_html.attrs['href'], reverse('grant-applications:index'))

    def test_form_error_on_create_ga_backoffice_exception(self, *mocks):
        mocks[0].side_effect = BackofficeServiceException
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
