import os

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

SECRET_KEY = "fake-key"

INSTALLED_APPS = [
    "cfdi",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "workflow.context_processors.custom_context",
            ]
        },
    }
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tests',
    }
}

CFDI_ERROR_CALLBACK = "tests.cfdi_callbacks.error_callback"
CFDI_POST_TIMBRADO_CALLBACK = "tests.cfdi_callbacks.post_timbrado_callback"