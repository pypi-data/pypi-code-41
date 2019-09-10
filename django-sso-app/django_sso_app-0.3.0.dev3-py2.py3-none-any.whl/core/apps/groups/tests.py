from django.conf import settings

if settings.DJANGO_SSO_BACKEND_ENABLED:
    from django.test import TestCase
    from allauth.account.models import EmailAddress

    from ..users.models import User
    from .models import Group


    class UserTestCase(TestCase):
        def setUp(self):
            self.user = User.objects.create(username="pippo", email="pippo@disney.com")
            self.user_email = EmailAddress.objects.create(user=self.user,
                                                          email=self.user.email,
                                                          primary=True,
                                                          verified=True)
            self.group = Group.objects.create(name='new_group')


        def test_add_user_to_group_updates_rev(self):
            user = self.user
            user_rev = user.sso_rev

            user.groups.add(self.group)

            print('groups', user.groups)

            self.assertEqual(user.sso_rev, user_rev + 1)
