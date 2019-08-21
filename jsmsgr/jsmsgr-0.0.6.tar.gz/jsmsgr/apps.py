from django.apps import AppConfig


class JsmsgrSdkConfig(AppConfig):
    name = "jsmsgr"

    def ready(self):
        from jsmsgr.sanity_check import sanity_check
