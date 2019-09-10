from django.conf import settings

if settings.DJANGO_SSO_BACKEND_ENABLED:
    from django.test import TestCase
    from allauth.account.models import EmailAddress

    from ..models import User
    from ...devices.models import Device


    class UserTestCase(TestCase):
        def setUp(self):
            self.user = User.objects.create(username="pippo", email="pippo@disney.com")
            self.user_email = EmailAddress.objects.create(user=self.user,
                                                          email=self.user.email,
                                                          primary=True,
                                                          verified=True)
            self.user_device = Device.objects.create(user=self.user,
                                                     fingerprint="abc123",
                                                     apigw_jwt_id="1"
                                                     )

        def test_user_field_update_updates_rev(self):
            """
            User update updates user revision
            """
            user = self.user
            user_rev = user.sso_rev

            user.country = 'Italia'
            user.save()

            self.assertEqual(user.sso_rev, user_rev + 1)
