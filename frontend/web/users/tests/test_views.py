from unittest.mock import patch

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from web.tests.helpers.testcases import BaseTestCase


@patch('web.users.services.send_magic_link')
class TestSendMagicLinkView(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_model = get_user_model()

    def setUp(self):
        self.url = reverse('users:magic-link')

    def test_method_not_allowed(self, *mocks):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 405)

    def test_get_html(self, *mocks):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/magic_link.html')
        self.assertIsNotNone(BeautifulSoup(response.content, 'html.parser').find(id='id_email'))

    def test_post_required_fields(self, *mocks):
        response = self.client.post(self.url)
        self.assertFormError(response, 'form', 'email', self.form_msgs['required'])
        mocks[0].assert_not_called()

    def test_post_with_bad_email(self, *mocks):
        response = self.client.post(self.url, data={'email': 'bad-email'})
        self.assertFormError(response, 'form', 'email', self.form_msgs['invalid-email'])

    def test_post_creates_user(self, *mocks):
        response = self.client.post(self.url, data={'email': 'user@test.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(get_user_model().objects.filter(email='user@test.com').exists())

    def test_post_uses_existing_user_if_already_exists(self, *mocks):
        get_user_model().objects.create(email='user@test.com')
        response = self.client.post(self.url, data={'email': 'user@test.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_user_model().objects.filter(email='user@test.com').count(), 1)

    def test_post_sends_magic_link_to_email(self, m_send_magic_link):
        response = self.client.post(self.url, data={'email': 'user@test.com'})
        self.assertEqual(response.status_code, 200)
        m_send_magic_link.assert_called_once()
        self.assertEqual(
            m_send_magic_link.call_args.kwargs['user'],
            self.user_model.objects.get(email='user@test.com')
        )
        self.assertIn(
            reverse('users:magic-link'),  # TODO: change to login
            m_send_magic_link.call_args.kwargs['login_path']
        )

    def test_post_will_logout_a_user_if_already_logged_in(self, *mocks):
        user = get_user_model().objects.create(email='user@test.com')
        self.client.force_login(user)
        response = self.client.post(self.url, data={'email': 'user@test.com'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertFalse(response.context['request'].user.is_authenticated)
        self.assertIsInstance(response.context['request'].user, AnonymousUser)

    def test_post_html(self, *mocks):
        response = self.client.post(self.url, data={'email': 'user@test.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/magic_link.html')

    def test_post_renders_email_field_hidden(self, *mocks):
        response = self.client.post(self.url, data={'email': 'user@test.com'})
        html = BeautifulSoup(response.content, 'html.parser')

        # Input html should be included in html with type=hidden
        self.assertEqual(html.find(id='id_email').attrs['type'], 'hidden')
        self.assertEqual(html.find(id='id_email').attrs['value'], 'user@test.com')

        # Hidden field should not display label or hints
        self.assertIsNone(html.find(id='id_email-label'))
        self.assertIsNone(html.find(id='id_email-hint'))

    def test_resend_email_renders_extra_copy(self, *mocks):
        response = self.client.post(self.url, data={'email': 'user@test.com'})
        self.assertTrue(response.context.get('magic_link_sent'))
        html = BeautifulSoup(response.content, 'html.parser').find(id='id_magic_link_sent')
        self.assertIsNotNone(html)
