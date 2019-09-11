from django.conf import settings

if settings.DJANGO_SSO_BACKEND_ENABLED:
    import json

    import jwt
    from django.urls import reverse
    from rest_framework import status

    from ...users.tests.test_views import UserTestCase


    class TestSubscriptions(UserTestCase):

        def test_user_can_list_service_subscriptions(self):
            """
            """
            response = self.client.post(
                reverse('rest_login'),
                data=json.dumps(self.valid_login),
                content_type='application/json'
            )
            cookies = response.cookies

            response2 = self.client.get(
                reverse('users:user_subscriptions', args=(self.user.sso_id, )),
                content_type='application/json'
            )

            self.assertEqual(response2.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response2.data['results']), 1)
            self.assertEqual(response2.data['results'][0].get('service').get('url'), self.service.url)


        def test_user_can_list_user_subscriptions(self):
            response = self.client.post(
                reverse('rest_login'),
                data = json.dumps(self.valid_login),
                content_type='application/json'
            )
            cookies = response.cookies

            response2 = self.client.get(
                reverse('users:user_subscriptions', args=(self.user.sso_id, )),
                content_type='application/json'
            )

            self.assertEqual(response2.status_code, status.HTTP_200_OK)


        def test_user_can_retrieve_user_subscription(self):
            response = self.client.post(
                reverse('rest_login'),
                data = json.dumps(self.valid_login),
                content_type='application/json'
            )
            cookies = response.cookies

            response2 = self.client.get(
                reverse('users:user_subscription_detail', args=(self.user.sso_id, self.user_subscription.id,)),
                content_type='application/json'
            )

            self.assertEqual(response2.status_code, status.HTTP_200_OK)
            self.assertEqual(response2.data.get('is_unsubscribed'), False)


        def test_user_can_unsubscribe_from_service_with_rev_incremented(self):
            first_rev = self.user.sso_rev
            response = self.client.post(
                reverse('rest_login'),
                data = json.dumps(self.valid_login),
                content_type='application/json'
            )
            cookies = response.cookies

            response2 = self.client.post(
                reverse('users:user_subscription_unsubscribe', args=(self.user.sso_id, self.user_subscription.id,)),
                data = json.dumps(self.valid_unsubscription),
                content_type='application/json'
            )
            cookies2 = response2.cookies

            print('\n\nRISPOSTA', response2.json())

            self.assertEqual(response2.status_code, status.HTTP_200_OK)

            self.assertEqual(response2.data.get('subscriptions')[0].get('is_unsubscribed'), True)

            self.user.refresh_from_db()
            second_rev = self.user.sso_rev

            self.assertEqual(second_rev, first_rev+1, 'rev not incremented on service unsubscription')

            jwt_cookie = cookies2.get('jwt')
            self.assertNotEqual(jwt_cookie, None, 'no new jwt received')

            unverified_payload = jwt.decode(jwt_cookie.value, None, False)

            print('\n\n\n Unv pay', unverified_payload)

            self.assertEqual(unverified_payload.get('rev'), second_rev, 'rev NOT updated in JWT')

        def test_user_can_unsubscribe_totally_with_rev_incremented(self):
            first_rev = self.user.sso_rev
            response = self.client.post(
                reverse('rest_login'),
                data = json.dumps(self.valid_login),
                content_type='application/json'
            )
            cookies = response.cookies

            response2 = self.client.post(
                reverse('users:user_unsubscription'),
                data = json.dumps(self.valid_unsubscription),
                content_type='application/json'
            )
            cookies2 = response2.cookies
            self.assertEqual(response2.status_code, status.HTTP_200_OK)

            print('\n\nRISPOSTA', response2.data)
            self.assertEqual(response2.data.get('is_unsubscribed'), True)

            self.user.refresh_from_db()
            second_rev = self.user.sso_rev

            self.assertEqual(second_rev, first_rev+1, 'rev not incremented on service unsubscription')

            jwt_cookie = cookies2.get('jwt')
            self.assertNotEqual(jwt_cookie, None, 'no cleared jwt received')


    class TestServices(UserTestCase):

        def test_user_can_list_services(self):
            """
            """
            response = self.client.post(
                reverse('rest_login'),
                data = json.dumps(self.valid_login),
                content_type='application/json'
            )
            cookies = response.cookies

            response2 = self.client.get(
                reverse('services:services_list'),
                content_type='application/json'
            )

            self.assertEqual(response2.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response2.data['results']), 2)

        def test_user_can_retrieve_service(self):
            """
            """
            response = self.client.post(
                reverse('rest_login'),
                data = json.dumps(self.valid_login),
                content_type='application/json'
            )
            cookies = response.cookies

            response2 = self.client.get(
                reverse('services:services_detail', args=(self.service.id, )),
                content_type='application/json'
            )

            self.assertEqual(response2.status_code, status.HTTP_200_OK)
            self.assertEqual(response2.data.get('url'), self.service.url)


        def test_user_can_subscribe_to_service_with_rev_incremented_and_devices_deleted(self):
            """
            """
            first_rev = self.user.sso_rev
            response = self.client.post(
                reverse('rest_login'),
                data = json.dumps(self.valid_login),
                content_type='application/json'
            )
            cookies = response.cookies
            first_devices = self.user.devices.all()
            first_devices = [x.id for x in first_devices]

            response2 = self.client.post(
                reverse('services:services_subscription', args=(self.service2.id, )),
                content_type='application/json'
            )

            self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

            self.user.refresh_from_db()

            self.assertEqual(response2.data, 'Subscribed.')

            self.user.refresh_from_db()
            second_rev = self.user.sso_rev

            self.assertEqual(second_rev, first_rev+1, 'rev not incremented')

            response3 = self.client.get(
                reverse('services:services_list'),
                content_type='application/json'
            )

            self.assertEqual(response3.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response3.data['results']), 2)

            cookies2 = response2.cookies
            jwt_cookie2 = cookies2.get('jwt').value
            unverified_payload2 = jwt.decode(jwt_cookie2, None, False)

            print('\n\n\n Unv pay', unverified_payload2)

            self.assertEqual(unverified_payload2.get('rev'), second_rev, 'cookie rev NOT changed after login')

            second_devices = self.user.devices.all()
            second_devices = [x.id for x in second_devices]

            print('\n\n DEVICES', first_devices, second_devices)
            self.assertEqual(len(second_devices), 1)


        def test_user_can_not_subscribe_to_service_twice(self):
            """
            """
            response = self.client.post(
                reverse('rest_login'),
                data = json.dumps(self.valid_login),
                content_type='application/json'
            )
            cookies = response.cookies

            response2 = self.client.post(
                reverse('services:services_subscription', args=(self.service.id, )),
                content_type='application/json'
            )

            self.assertEqual(response2.status_code, status.HTTP_409_CONFLICT)
            self.assertEqual(response2.data, 'Already subscribed.')


        def test_user_can_subscribe_to_service_from_alternative_url_with_rev_incremented(self):
            """
            """
            first_rev = self.user.sso_rev
            response = self.client.post(
                reverse('rest_login'),
                data = json.dumps(self.valid_login),
                content_type='application/json'
            )
            cookies = response.cookies

            response2 = self.client.post(
                reverse('users:user_subscriptions_create', args=(self.user.sso_id, self.service2.id, )),
                content_type='application/json'
            )
            print('\n\n\n RISPOSTA!', response2.data)
            self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

            self.user.refresh_from_db()

            self.assertEqual(response2.data, 'Subscribed.')

            self.user.refresh_from_db()
            second_rev = self.user.sso_rev

            self.assertEqual(second_rev, first_rev+1, 'rev not incremented')

            response3 = self.client.get(
                reverse('services:services_list'),
                content_type='application/json'
            )

            self.assertEqual(response3.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response3.data['results']), 2)

            cookies2 = response2.cookies
            jwt_cookie2 = cookies2.get('jwt').value
            unverified_payload2 = jwt.decode(jwt_cookie2, None, False)

            print('\n\n\n Unv pay', unverified_payload2)

            self.assertEqual(unverified_payload2.get('rev'), second_rev, 'cookie rev NOT changed after login')



        def test_user_can_not_subscribe_to_service_from_alternative_url_if_not_same_user(self):
            """
            """
            response = self.client.post(
                reverse('rest_login'),
                data = json.dumps(self.valid_login),
                content_type='application/json'
            )
            cookies = response.cookies

            response2 = self.client.post(
                reverse('users:user_subscriptions_create', args=(self.user2.sso_id, self.service2.id, )),
                content_type='application/json'
            )

            self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)


        def test_user_not_subscribe_to_service_from_alternative_url_if_not_same_user_but_staff_rev_is_incremented(self):
            """
            """
            first_rev = self.user.sso_rev
            self.client.login(username=self.staff_user_username, password=self.staff_user_password)

            response2 = self.client.post(
                reverse('users:user_subscriptions_create', args=(self.user.sso_id, self.service2.id, )),
                content_type='application/json'
            )
            print('\n\n\n RISPOSTA!', response2.data)

            self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

            self.user.refresh_from_db()
            second_rev = self.user.sso_rev

            self.assertEqual(second_rev, first_rev+1, 'rev not incremented')

            cookies2 = response2.cookies
            jwt_cookie2 = cookies2.get('jwt')

            self.assertEqual(jwt_cookie2, None)

