from config.settings.base import *

ALLOWED_HOSTS = ['localhost', '0.0.0.0', '127.0.0.1', 'backoffice']
# This is required on mac to allow django-debug-toolbar to
# show up when django server is run inside docker.
INTERNAL_IPS = type(str('c'), (), {'__contains__': lambda *a: True})()

INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

CAN_ELEVATE_SSO_USER_PERMISSIONS = True
CAN_CREATE_TEST_USER = True

BASE_URL = 'http://localhost:8000'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'requests': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}

MEDIA_ROOT = os.path.join(BACKOFFICE_DIR, 'media/')
MEDIA_URL = '/media/'
