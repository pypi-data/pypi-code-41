from django.urls import reverse
from django_fakery import factory
from faker import Faker
from rest_framework.test import APITestCase
from test_plus.test import TestCase

from .factories import UserFactory
from ..apis import serializers


class UserTestCase(APITestCase, TestCase):

    def setUp(self):
        self.faker = Faker()
        self.user = UserFactory()
        self.new_user = UserFactory()

    def test_user_create(self):
        url = reverse('simpl_users_api:user-list')

        obj = factory.build('simpl_users.User', make_fks=True)
        payload = serializers.UserSerializer(obj).data

        # Does this api work without auth?
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 403)

        # Does this api work with auth?
        with self.login(email=self.user.email):
            response = self.client.post(url, payload, format='json')
            self.assertEqual(response.status_code, 201)
            self.assertNotEqual(len(response.data), 0)

    def test_user_delete(self):
        url = reverse('simpl_users_api:user-detail', kwargs={'id': self.new_user.id})

        # Does this api work without auth?
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 403)

        # Does this api work with auth?
        with self.login(email=self.user.email):
            response = self.client.delete(url, format='json')
            self.assertEqual(response.status_code, 204)

            # Verify that the object is gone?
            response = self.client.delete(url, format='json')
            self.assertEqual(response.status_code, 404)

    def test_user_detail(self):
        url = reverse('simpl_users_api:user-detail', kwargs={'id': self.user.id})

        # Does this api work without auth?
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

        # Does this api work with auth?
        with self.login(email=self.user.email):
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertNotEqual(len(response.data), 0)

    def test_user_list(self):
        url = reverse('simpl_users_api:user-list')

        # Does this api work without auth?
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

        # Does this api work with auth?
        with self.login(email=self.user.email):
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertNotEqual(len(response.data), 0)

    def test_user_update(self):
        obj = self.user
        url = reverse('simpl_users_api:user-detail', kwargs={'id': obj.id})

        old_first_name = obj.first_name
        payload = serializers.UserSerializer(obj).data

        # Does this api work without auth?
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, 403)

        # Does this api work with auth?
        with self.login(email=self.user.email):
            obj.first_name = self.faker.name()
            payload = serializers.UserSerializer(obj).data

            response = self.client.put(url, payload, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.data['first_name'] != old_first_name)
