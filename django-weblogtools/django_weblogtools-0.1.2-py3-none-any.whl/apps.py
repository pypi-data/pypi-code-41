from django.apps import AppConfig


class WeblogtoolsConfig(AppConfig):
    name = 'weblogtools'
    verbose_name = 'HTTP接口日志'

    def ready(self):
        from . import signals
