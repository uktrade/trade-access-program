from django.conf import settings
from django.urls import reverse

from web.tests.factories.users import UserFactory
from web.tests.helpers import BaseTestCase


class TestIndexView(BaseTestCase):

    def test_index_view(self):
        response = self.client.get(settings.LOGIN_URL)
        self.assertTemplateUsed(response, 'index.html')

    def test_index_view_redirects_if_user_is_authenticated(self):
        self.client.force_login(user=UserFactory())
        response = self.client.get(reverse('index'))
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)


class TestErrorViews(BaseTestCase):

    def test_404(self):
        response = self.client.get('/not-a-valid-path/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
