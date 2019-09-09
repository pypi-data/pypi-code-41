from django.apps import AppConfig


class DjangoTaskerGeobaseConfig(AppConfig):
    name = 'django_tasker_geobase'
    verbose_name = "Tasker geobase"

    def ready(self):
        if not self.apps.is_installed('mptt'):
            raise Exception("Add in settings.py to section INSTALLED_APPS application mptt")
