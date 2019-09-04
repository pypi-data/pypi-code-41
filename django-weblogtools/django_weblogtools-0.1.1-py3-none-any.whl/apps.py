from django.apps import AppConfig


class HttplogConfig(AppConfig):
    name = 'httplog'
    verbose_name = 'HTTP接口日志'

    def ready(self):
        from . import signals
