from django.conf import settings
from django.core import signing
from django.urls import reverse

from web.grant_applications.services import BackofficeService


def encrypt_data(data):
    """
        Converting the data into a hash value
    """
    return signing.dumps(data)


def decrypting_data(hashed_value, max_age=settings.MAGIC_LINK_HASH_TTL):
    return signing.loads(hashed_value)


def generate_action_magic_link(data):
    encrypted_data = encrypt_data(data)
    magic_view_url = reverse('grant_applications:magic-link', args=(encrypted_data,))
    return f'{settings.BASE_URL}{magic_view_url}',


RESUME_APPLICATION_ACTION = 'resume-application-link'


def send_resume_application_email(grant_application):
    data = {
        'redirect-url': f'{settings.BASE_URL}{grant_application.state_url}',
        'action-type': RESUME_APPLICATION_ACTION
    }
    magic_link = generate_action_magic_link(data)
    print(f'##### {magic_link}', flush=True)
    BackofficeService().send_resume_application_email(grant_application, magic_link)
