from django.conf import settings

if not settings.configured:
    settings.configure()

from .functions import load_func

_DEFAULT_PAC_AUTH = {
    "ntlink": {
        "dev": {"usuario": "", "password": ""},
        "prod": {"usuario": "", "password": ""},
    },
    "dfacture": {
        "dev": {"usuario": "", "password": ""},
        "prod": {"usuario": "", "password": ""},
    },
    "prodigia": {
        "dev": {"contrato": "", "usuario": "", "password": ""},
        "prod": {"contrato": "", "usuario": "", "password": ""},
    },
}


TMP_DIR = getattr(settings, "CFDI_TMP_DIR", "/tmp/")

DFACTURE_AUTH = getattr(
    settings, "CFDI_DFACTURE_AUTH", _DEFAULT_PAC_AUTH.get("dfacture")
)

PRODIGIA_AUTH = getattr(
    settings, "CFDI_PRODIGIA_AUTH", _DEFAULT_PAC_AUTH.get("prodigia")
)

NTLINK_AUTH = getattr(
    settings, "CFDI_NTLINK_AUTH", _DEFAULT_PAC_AUTH.get("ntlink")
)

ERROR_CALLBACK = getattr(settings, "CFDI_ERROR_CALLBACK", None)
POST_TIMBRADO_CALLBACK = getattr(settings, "CFDI_POST_TIMBRADO_CALLBACK", None)

if ERROR_CALLBACK:
    ERROR_CALLBACK = load_func(ERROR_CALLBACK)

if POST_TIMBRADO_CALLBACK:
    POST_TIMBRADO_CALLBACK = load_func(POST_TIMBRADO_CALLBACK)