def get_core_apps():
    return [
        'django_sso_app.core.apps.users',
        'django_sso_app.core.apps.groups',
        'django_sso_app.core.apps.services',
        'django_sso_app.core.apps.devices',
        'django_sso_app.core.apps.passepartout',
    ]
