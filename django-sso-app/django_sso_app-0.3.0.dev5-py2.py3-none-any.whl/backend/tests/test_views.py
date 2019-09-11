from django.conf import settings

if settings.DJANGO_SSO_BACKEND_ENABLED:

    import json
    import re
    from rest_framework import status
    from django.core import mail
    from django.test import TestCase, Client
    from django.urls import reverse
    from django.contrib.auth import get_user_model
    from allauth.account.models import (
        EmailAddress,
        EmailConfirmation,
        EmailConfirmationHMAC,
    )

    from django_sso_app.core.apps.services.models import Service

    # initialize the APIClient app
    User = get_user_model()


    class TestLogin(TestCase):
        def setUp(self):
            self.client = Client()

            email = "pippo@disney.com"
            self.user = User.objects.create_user(username="pippo", email=email, password="paperina")
            self.user_email = EmailAddress.objects.create(user=self.user,
                                                          email=email,
                                                          primary=True,
                                                          verified=True)

            staff_email = 'staff@example.com'
            self.staff_user = User.objects.create_user(username="staff", email=staff_email, password="staff", is_staff=True)
            self.staff_user_email = EmailAddress.objects.create(user=self.staff_user,
                                                          email=staff_email,
                                                          primary=True,
                                                          verified=True)
            self.valid_staff_login = {
                'email': staff_email,
                'password': 'staff',
                'fingerprint': '000000'
            }

            self.valid_email_login = {
                'email': email,
                'password': 'paperina',
                'fingerprint': '123456'
            }
            self.valid_username_login = {
                'username': 'pippo',
                'password': 'paperina',
                'fingerprint': '123456'
            }
            self.invalid_login = {
                'email': 'topolino@disney.com',
                'password': ''
            }


        def test_can_login_with_email(self):
            response = self.client.post(
                reverse('rest_login'),
                data = json.dumps(self.valid_email_login),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_can_login_with_username(self):
            response = self.client.post(
                reverse('rest_login'),
                data = json.dumps(self.valid_username_login),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_login_returns_jwt_cookie(self):
            response = self.client.post(
                reverse('rest_login'),
                data = json.dumps(self.valid_email_login),
                content_type='application/json'
            )

            cookies = response.client.cookies.items()

            # print('\nRISPOSTA', response.data, '\nCookies\n', cookies, '\n')

            has_jwt_cookie = False
            for (key, val) in cookies:
                if key == "jwt":
                    has_jwt_cookie = True
                    break

            self.assertTrue(has_jwt_cookie)
        """
        def test_migrated_can_login_without_updating_rev(self):
            self.client.logout()

            migrated_user_email = 'supercacca@supercacca.com'
            hashed_password = 'pbkdf2_sha256$15000$KCmb0T1BofB7$fV4zlS1mFUC8HYhrgnAtEfvFzB1pgnyDloidsDLYVag='
            migrated_user = User.objects.create(
                username = 'supercacca',
                email = migrated_user_email,
                password = hashed_password
            )
            migrated_user_email = EmailAddress.objects.create(user=migrated_user,
                                                               email=migrated_user_email,
                                                               primary=True,
                                                               verified=True)
            valid_migrated_user_login = {
                'username': 'supercacca@supercacca.com',
                'password': 'supercacca',
                'fingerprint': '123'
            }


            previus_rev = migrated_user.sso_rev

            response = self.client.post(
                reverse('rest_login'),
                data=json.dumps(valid_migrated_user_login),
                content_type='application/json'
            )
            print('RESP', response)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            migrated_user.refresh_from_db()
            second_rev = migrated_user.sso_rev
            self.assertEqual(previus_rev, second_rev)
        """
        def test_staff_user_can_not_login(self):
            response = self.client.post(
                reverse('rest_login'),
                data=json.dumps(self.valid_staff_login),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    class TestRegister(TestCase):
        def setUp(self):
            email = "pippo@disney.com"
            self.user = User.objects.create_user(username="pippo", email=email, password="paperina")
            self.user_email = EmailAddress.objects.create(user=self.user,
                                                          email=email,
                                                          primary=True,
                                                          verified=True)
            self.valid_registration = {
                'email': 'topolino@disney.com',
                'username': 'topolino',
                'password1': 'paperina',
                'password2': 'paperina',
                'first_name': 'Mickey',
                'last_name': 'Mouse',
                'country': 'Italia',
                'latitude': 12.345,
                'longitude': 54.321,
                'referrer': 'http://example.com'
            }

            self.invalid_registration = {
                'email': 'topolino@d',
                'username': ''
            }

            self.service = Service.objects.create(name='example', url='http://example.com')

        def test_can_register(self):
            response = self.client.post(
                reverse('rest_register'),
                data = json.dumps(self.valid_registration),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            new_user = User.objects.filter(email=self.valid_registration['email']).first()

            self.assertEqual(new_user.email, self.valid_registration['email'])

            email_address = EmailAddress.objects.filter(user=new_user, email=self.valid_registration['email']).first()

            self.assertNotEqual(email_address, None)

        def test_cannot_register_on_invalid_registration_data(self):
            response = self.client.post(
                reverse('rest_register'),
                data = json.dumps(self.invalid_registration),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        def test_registration_sends_confirmation_email(self):
            response = self.client.post(
                reverse('rest_register'),
                data = json.dumps(self.valid_registration),
                content_type='application/json'
            )

            self.assertEqual(len(mail.outbox), 1)
