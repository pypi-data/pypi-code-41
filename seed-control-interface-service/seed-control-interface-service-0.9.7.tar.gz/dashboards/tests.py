from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from .models import Dashboard, UserDashboard, Definition


class APITestCase(TestCase):

    def setUp(self):
        self.adminclient = APIClient()


class AuthenticatedAPITestCase(APITestCase):

    def setUp(self):
        super(AuthenticatedAPITestCase, self).setUp()

        # Admin User setup
        self.adminusername = 'testadminuser'
        self.adminpassword = 'testadminpass'
        self.adminuser = User.objects.create_superuser(
            self.adminusername,
            'testadminuser@example.com',
            self.adminpassword)
        admintoken = Token.objects.create(user=self.adminuser)
        self.admintoken = admintoken.key
        self.adminclient.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admintoken)


class TestServicesApp(AuthenticatedAPITestCase):

    def make_dashboard(self):
        dashboard = Dashboard.objects.create(**{
            "name": "Test Dash"
        })
        return dashboard

    def make_user_dashboard(self, dashboard_id):
        user_dash = UserDashboard.objects.create(**{
            "user_id": 1,
            "default_dashboard_id": dashboard_id
        })
        return user_dash

    def make_definition(self):
        definition = Definition.objects.create(**{
            "title": "Main Definition",
            "description": "This is the main definition"
        })
        return definition

    def test_list_dashboard(self):

        self.make_dashboard()
        self.make_dashboard()

        response = self.adminclient.get('/api/v1/dashboard/')

        body = response.json()
        self.assertEqual(len(body['results']), 2)

    def test_list_userdashboard(self):
        dashboard = self.make_dashboard()

        self.make_user_dashboard(dashboard.id)
        self.make_user_dashboard(dashboard.id)

        response = self.adminclient.get('/api/v1/userdashboard/')

        body = response.json()
        self.assertEqual(len(body['results']), 2)

    def test_list_definition(self):

        self.make_definition()
        self.make_definition()

        response = self.adminclient.get('/api/v1/definition/')

        body = response.json()
        self.assertEqual(len(body['results']), 2)
