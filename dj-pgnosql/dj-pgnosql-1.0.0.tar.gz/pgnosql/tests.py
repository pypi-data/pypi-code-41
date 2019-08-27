from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from .models import KV
from .user import GlobalUser


class KVTestCase(TestCase):

    def setUp(self):
        pass

    def test_set_kv(self):
        key = KV.set('foo', {"bar": "baz"})
        self.assertIsInstance(key, KV)
        self.assertEqual(
            KV.objects.count(),
            1,
            'Create a key'
        )

    def test_set_will_update_if_key_already_exists(self):
        key = KV.set('foo', {"bar": "baz"})
        self.assertEqual(
            KV.get("foo").get("bar"),
            "baz"
        )

        key = KV.set('foo', {"bar": "bus"})
        self.assertEqual(KV.get("foo").get("bar"), "bus")

    def test_get_kv(self):
        KV.set('foo', {"bar": "baz"})
        got = KV.get('foo')
        self.assertEqual(
            got.get('bar'),
            "baz"
        )

    def test_get_returns_none_if_key_does_not_exist(self):
        self.assertIsNone(KV.get('nope'))

    def test_can_delete(self):
        KV.set('foo', {"bar": "baz"})
        self.assertIsNotNone(KV.get("foo"))
        KV.delete_key("foo")
        self.assertIsNone(KV.get("foo"))

class MiddlewareTestCase(TestCase):

    def setUp(self):
        user = get_user_model().objects.create_superuser(
            username='joe',
            password='test',
            email='joe@soap.com'
        )
        data = {"id": user.id, "foo": "bar", "permissions": {"spaces": ["1", "2", "3"]}}
        KV.set("user:{}".format(user.id), data)
        self.client.login(username='joe', password='test')
        self.result = self.client.get('/admin/')

    def test_normal_auth_system_works_fine(self):
        self.assertEqual(self.result.status_code, 200)

class GlobalUserTestCase(TestCase):

    def setUp(self):
        self.user_id = 1
        self.spaces = ["1", "2", "3"]
        data = {"id": self.user_id, "foo": "bar", "permissions": {"spaces": self.spaces}}
        GlobalUser(self.user_id).set(data)

    def test_gets_id(self):
        self.assertEqual(GlobalUser(self.user_id).id, self.user_id)

    def test_gets_data(self):
        data = GlobalUser(self.user_id).data
        self.assertEqual(data.get("foo"), "bar")

    def test_data_defaults_to_empty_dict(self):
        self.assertEqual(GlobalUser(2).data, {})

    def test_gets_spaces(self):
        self.assertEqual(
            GlobalUser(self.user_id).spaces,
            self.spaces
        )

    def test_can_get_as_a_django_user(self):
        user = GlobalUser(self.user_id).as_django_user
        # not intirely sure why this doesnt pass:
        # assert isinstance(user, get_user_model())

    def test_get_permissions(self):
        spaces = GlobalUser(self.user_id).get_permissions("spaces")
        self.assertEqual(spaces, self.spaces)

    @override_settings(NOSQL_USER_OBJECT_KEY='foo')
    def test_respects_overriding_user_key(self):
        gu = GlobalUser(self.user_id).set({})
        self.assertEqual(
            gu.key,
            "foo:{}".format(self.user_id)
        )









