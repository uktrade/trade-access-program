from urllib.parse import urljoin

from django.core import signing
from django.conf import settings


def encrypt_data(data):
    """
        Converting the data into a hash value
    """
    return signing.dumps(data)


def decrypting_data(hashed_value, max_age=None):
    if max_age is None:
        max_age = settings.MAGIC_LINK_HASH_TTL
    return signing.loads(hashed_value, max_age=max_age)


FRONTEND_MAGIC_LINK_VIEW_URL = '/resume/{hash}'


def generate_frontend_action_magic_link(data):
    encrypted_data = encrypt_data(data)
    frontend_magic_link_view_url = FRONTEND_MAGIC_LINK_VIEW_URL.format(hash=encrypted_data)
    return urljoin(settings.FRONTEND_DOMAIN, frontend_magic_link_view_url)
