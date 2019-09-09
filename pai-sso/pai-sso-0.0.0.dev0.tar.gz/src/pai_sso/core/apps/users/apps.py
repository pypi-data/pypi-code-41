from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'pai_sso.core.apps.users'

    def __init__(self, *args, **kwargs):
        ret = super(UsersConfig, self).__init__(*args, **kwargs)
        print('eccolo', self.label)
        return ret
