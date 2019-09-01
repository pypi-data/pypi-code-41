from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "meta_consent"
    verbose_name = "META Consent"
    include_in_administration_section = True
    has_exportable_data = True
