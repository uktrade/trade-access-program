from urllib.parse import urljoin

from django.conf import settings
from django.core import signing
from django.urls import reverse

from web.grant_applications.models import GrantApplicationLink
from web.grant_applications.services import BackofficeService


def encrypt_data(data):
    return signing.dumps(data)


def decrypting_data(hashed_value, max_age=None):
    if max_age is None:
        max_age = settings.MAGIC_LINK_HASH_TTL
    return signing.loads(hashed_value, max_age=max_age)


def generate_action_magic_link(data):
    encrypted_data = encrypt_data(data)
    magic_view_url = reverse('grant_applications:magic-link', args=(encrypted_data,))
    return urljoin(settings.FRONTEND_DOMAIN, magic_view_url)


RESUME_APPLICATION_ACTION = 'resume-application-link'
UPLOAD_EVENT_BOOKING_EVIDENCE_ACTION = 'upload-event-evidence'


def send_resume_application_email(grant_application):
    data = {
        'redirect-url': f'{settings.FRONTEND_DOMAIN}{grant_application.state_url}',
        'action-type': RESUME_APPLICATION_ACTION
    }
    magic_link = generate_action_magic_link(data)
    BackofficeService().send_resume_application_email(grant_application, magic_link)


def get_active_backoffice_application(email):
    grant_application_links = GrantApplicationLink.objects.filter(email__iexact=email).order_by('-updated')
    backoffice_service = BackofficeService()
    if grant_application_links.exists():
        active_grant_application_link = grant_application_links.first()
        backoffice_grant_application = backoffice_service.get_grant_application(
            active_grant_application_link.backoffice_grant_application_id
        )
        if not backoffice_grant_application.get('is_completed', False):
            return backoffice_grant_application

    return None
