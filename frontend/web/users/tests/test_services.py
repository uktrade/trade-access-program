from unittest.mock import patch

from django.contrib.auth import get_user_model

from web.core.notify import NotifyService
from web.tests.helpers.testcases import BaseTestCase
from web.users import services


@patch('web.users.services.sesame_utils.get_query_string', return_value='?a-token')
@patch.object(NotifyService, 'send_email')
class TestSendMagicLink(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(email='user@test.com')

    def test_send_magic_link(self, p_send_email, p_get_query_string):
        services.send_magic_link(user=self.user, login_path='/fake/login/path')
        p_send_email.assert_called_once_with(
            email_address=self.user.email,
            template_name='magic-link',
            personalisation={
                'login_url': '/fake/login/path?a-token'
            }
        )
