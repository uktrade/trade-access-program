from web.core.notify import NotifyService
from sesame import utils as sesame_utils


def send_magic_link(user, login_path):
    return NotifyService().send_email(
        email_address=user.email,
        template_name='magic-link',
        personalisation={
            'login_url': login_path + sesame_utils.get_query_string(user)
        }
    )
