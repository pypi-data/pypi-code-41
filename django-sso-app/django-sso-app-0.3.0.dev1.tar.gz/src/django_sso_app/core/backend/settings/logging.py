LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s:%(name)s: %(message)s '
                      '(%(asctime)s; %(filename)s:%(lineno)d)',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'users': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'profiles': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'devices': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'services': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'passepartout': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'api_gateway': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'backend': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'django': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
