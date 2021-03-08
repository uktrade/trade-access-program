import time
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse

from web.grant_applications.utils import RESUME_APPLICATION_ACTION, encrypt_data
from web.grant_applications.services import BackofficeService
from web.tests.factories.grant_application_link import GrantApplicationLinkFactory
from web.tests.helpers.testcases import BaseTestCase

from web.tests.helpers.backoffice_objects import FAKE_GRANT_APPLICATION


class TestMagicLinkHandlerView(BaseTestCase):

    @override_settings(MAGIC_LINK_HASH_TTL=1)
    def setUp(self):
        self.user_email = 'user@test.com'
        self.gal = GrantApplicationLinkFactory(email=self.user_email)
        data = {
            'redirect-url': f'{self.gal.state_url}',
            'action-type': RESUME_APPLICATION_ACTION
        }
        magic_link_hash = encrypt_data(data)
        self.url = reverse('grant-applications:magic-link', args=(magic_link_hash, ))

    @patch.object(
        BackofficeService,
        'get_grant_application',
        return_value=FAKE_GRANT_APPLICATION.copy()
    )
    def test_valid_magic_link_url(self, *mocks):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            self.gal.state_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True
        )

    def test_invalid_magic_link_url(self):
        invalid_url = f'{str(self.url)[:-5]}/'
        response = self.client.get(invalid_url)
        self.assertRedirects(
            response,
            reverse('grant_applications:invalid-magic-link'),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True
        )

    @override_settings(MAGIC_LINK_HASH_TTL=1)
    def test_expired_magic_link_url(self):
        time.sleep(2)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse('grant_applications:expired-magic-link'),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True
        )
