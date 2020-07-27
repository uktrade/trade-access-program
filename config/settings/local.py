from config.settings.base import *

# This is required on mac to allow django-debug-toolbar to
# show up when django server is run inside docker.
DOCKER_NETWORK_IP = os.getenv('DOCKER_NETWORK_IP', '172.20.0.1')

ALLOWED_HOSTS = ['localhost', '0.0.0.0', '127.0.0.1']
INTERNAL_IPS = ['localhost', '0.0.0.0', '127.0.0.1', DOCKER_NETWORK_IP]

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

CAN_ELEVATE_SSO_USER_PERMISSIONS = True
CAN_CREATE_TEST_USER = True

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
            }
        },
    }
