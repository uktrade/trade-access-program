from config.settings.base import *

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
        'loggers': {
            '': {  # 'catch all' loggers by referencing it with the empty string
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    },
}
