# import datetime
import json

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from seed_control_interface_service import utils
from .models import AuditLog


class APITestCase(TestCase):

    def setUp(self):
        self.normalclient = APIClient()


class AuthenticatedAPITestCase(APITestCase):

    def setUp(self):
        super(AuthenticatedAPITestCase, self).setUp()

        # Normal User setup
        self.normalusername = 'testnormaluser'
        self.normalpassword = 'testnormalpass'
        self.normaluser = User.objects.create_user(
            self.normalusername,
            'testnormaluser@example.com',
            self.normalpassword)
        normaltoken = Token.objects.create(user=self.normaluser)
        self.normaltoken = normaltoken.key
        self.normalclient.credentials(
            HTTP_AUTHORIZATION='Token ' + self.normaltoken)


class TestAuditLogAPI(AuthenticatedAPITestCase):

    def create_audit_log(self, data={}):
        object_data = {
            "action": AuditLog.CREATE,
            "identity_id": "88d52f65-1111-4f5f-99ad-f60f8eb3fc21",
            "subscription_id": "88d52f65-2222-4f5f-99ad-f60f8eb3fc21",
            "model": "subscription",
            "detail": "created subscription",
            "action_by": self.normaluser.id
        }
        object_data.update(data)
        return AuditLog.objects.create(**object_data)

    def test_create_audit_log(self):
        """
        Posting a valid payload to the auditlog endpoint should create a
        auditlog object.
        """
        # Setup
        identity_id = "88d52f65-1111-4f5f-99ad-f60f8eb3fc21"
        subscription_id = "88d52f65-2222-4f5f-99ad-f60f8eb3fc21"

        post_data = {
            "action": "c",
            "action_by": 3,
            "identity_id": identity_id,
            "subscription_id": subscription_id,
            "model": "subscription",
            "detail": "created subscription"
        }
        # Execute
        response = self.normalclient.post(
            '/api/v1/auditlog/',
            json.dumps(post_data),
            content_type='application/json')
        # Check
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        audit = AuditLog.objects.last()
        self.assertEqual(audit.action_by, 3)
        self.assertEqual(audit.action, AuditLog.CREATE)
        self.assertEqual(str(audit.identity_id), identity_id)
        self.assertEqual(str(audit.subscription_id), subscription_id)
        self.assertEqual(audit.model, "subscription")
        self.assertEqual(audit.detail, "created subscription")

    def test_create_audit_log_display_name(self):
        """
        Posting a valid payload to the auditlog endpoint should create a
        auditlog object. The "action" field should be able to accept the
        display name as a value.
        """
        # Setup
        identity_id = "88d52f65-1111-4f5f-99ad-f60f8eb3fc21"
        subscription_id = "88d52f65-2222-4f5f-99ad-f60f8eb3fc21"

        post_data = {
            "action": "Create",
            "action_by": 3,
            "identity_id": identity_id,
            "subscription_id": subscription_id,
            "model": "subscription",
            "detail": "created subscription"
        }
        # Execute
        response = self.normalclient.post(
            '/api/v1/auditlog/',
            json.dumps(post_data),
            content_type='application/json')
        # Check
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        audit = AuditLog.objects.last()
        self.assertEqual(audit.action_by, 3)
        self.assertEqual(audit.action, AuditLog.CREATE)
        self.assertEqual(str(audit.identity_id), identity_id)
        self.assertEqual(str(audit.subscription_id), subscription_id)
        self.assertEqual(audit.model, "subscription")
        self.assertEqual(audit.detail, "created subscription")

    def test_create_audit_log_missing_data(self):
        """
        Posting a incomplete payload to the auditlog endpoint should not create
        an auditlog object and respond with a error code and message.
        """
        # Setup
        post_data = {
        }
        # Execute
        response = self.normalclient.post(
            '/api/v1/auditlog/',
            json.dumps(post_data),
            content_type='application/json')
        # Check
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(utils.json_decode(response.content),
                         {"model": ["This field is required."],
                          "action": ["This field is required."],
                          "action_by": ["This field is required."],
                          "identity_id": ["This field is required."]})

        self.assertEqual(AuditLog.objects.count(), 0)

    def test_create_audit_log_invalid_data(self):
        """
        Posting a invalid payload to the auditlog endpoint should not create a
        auditlog object and respond with a error code and message.
        """
        # Setup
        identity_id = "88d52f65-1111-4f5f-99ad-f60f8eb3fc21"
        subscription_id = "88d52f65-2222-4f5f-99ad-f60f8eb3fc21"

        post_data = {
            "action": "x",
            "identity_id": identity_id,
            "subscription_id": subscription_id,
            "model": "subscription",
            "detail": "created subscription",
            "action_by": 1
        }
        # Execute
        response = self.normalclient.post(
            '/api/v1/auditlog/',
            json.dumps(post_data),
            content_type='application/json')
        # Check
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(utils.json_decode(response.content),
                         {"action": ['"x" is not a valid choice.']})

        self.assertEqual(AuditLog.objects.count(), 0)

    def test_update_audit_log_not_allowed(self):
        """
        When a PATCH request is sent to the endpoint it should fail.
        """
        post_data = {
            "action": "x",
        }
        # Execute
        response = self.normalclient.patch(
            '/api/v1/auditlog/',
            json.dumps(post_data),
            content_type='application/json')
        # Check
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

        self.assertEqual(utils.json_decode(response.content),
                         {"detail": 'Method "PATCH" not allowed.'})

    def test_list_audit_log(self):
        """
        Doing a GET request on the auditlog endpoint should return a list of
        all auditlog records.
        """
        identity_id = "88d52f65-1111-4f5f-99ad-f60f8eb3fc21"
        subscription_id = "88d52f65-2222-4f5f-99ad-f60f8eb3fc21"
        self.create_audit_log()

        # Execute
        response = self.normalclient.get(
            '/api/v1/auditlog/',
            content_type='application/json')
        # Check
        results = utils.json_decode(response.content)["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["action_by"], self.normaluser.id)
        self.assertEqual(results[0]["action_name"], "Create")
        self.assertEqual(results[0]["identity_id"], identity_id)
        self.assertEqual(results[0]["subscription_id"], subscription_id)
        self.assertEqual(results[0]["model"], "subscription")
        self.assertEqual(results[0]["detail"], "created subscription")

    def test_list_audit_log_filter(self):
        """
        Doing a GET request with a filter on the auditlog endpoint should
        return a list of all auditlog records that match.
        """
        identity_id = "88d52f65-3333-4f5f-99ad-f60f8eb3fc21"
        subscription_id = "88d52f65-4444-4f5f-99ad-f60f8eb3fc21"
        self.create_audit_log()
        self.create_audit_log(
            {"identity_id": identity_id, "subscription_id": subscription_id})

        # Execute
        response = self.normalclient.get(
            '/api/v1/auditlog/?identity_id={}&subscription_id={}'.format(
                identity_id, subscription_id),
            content_type='application/json')
        # Check
        results = utils.json_decode(response.content)["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["action_by"], self.normaluser.id)
        self.assertEqual(results[0]["action_name"], "Create")
        self.assertEqual(results[0]["identity_id"], identity_id)
        self.assertEqual(results[0]["subscription_id"], subscription_id)
        self.assertEqual(results[0]["model"], "subscription")
        self.assertEqual(results[0]["detail"], "created subscription")
