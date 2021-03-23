from urllib.parse import urljoin

from django.core import signing
from django.conf import settings


def encrypt_data(data):
    return signing.dumps(data, key=settings.FRONTEND_SECRET_KEY)


def decrypting_data(hashed_value, max_age=None):
    if max_age is None:
        max_age = settings.MAGIC_LINK_HASH_TTL

    return signing.loads(
        hashed_value,
        max_age=max_age,
        key=settings.FRONTEND_SECRET_KEY
    )


FRONTEND_MAGIC_LINK_VIEW_URL = '/grant-applications/resume/{hash}'


def generate_frontend_action_magic_link(data):
    encrypted_data = encrypt_data(data)
    frontend_magic_link_view_url = FRONTEND_MAGIC_LINK_VIEW_URL.format(hash=encrypted_data)
    return urljoin(settings.FRONTEND_DOMAIN, frontend_magic_link_view_url)
