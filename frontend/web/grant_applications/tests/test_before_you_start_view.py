from bs4 import BeautifulSoup
from django.urls import reverse

from web.grant_applications.views import BeforeYouStartView
from web.tests.helpers.testcases import BaseTestCase


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
