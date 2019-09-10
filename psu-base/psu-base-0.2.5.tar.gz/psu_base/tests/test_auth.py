from django.test import TestCase
from psu_base.classes.Auth import Auth
from psu_base.classes.User import User


class AuthTestCase(TestCase):
    def setUp(self):
        pass

    def test_auth_user(self):
        """Create a User from username"""
        # Lookup via Finti
        mjg = User('mjg')
        self.assertTrue(mjg.username == 'mjg', 'Incorrect username for mjg')
        self.assertTrue(type(mjg.authorities) is list, 'No authority list')

        # Restore from dict
        mjg_dict = mjg.to_dict()
        self.assertTrue(type(mjg_dict) is dict, 'mjg_dict is not a dict')
        re_mjg = User(mjg_dict)
        self.assertTrue(re_mjg.username == 'mjg', 'Incorrect username for mjg')
        self.assertTrue(re_mjg.psu_id == '988213600', 'Incorrect psu_id for mjg')
        self.assertTrue(type(re_mjg.authorities) is list, 'No authority list')

    def test_auth_impersonation(self):
        mjg = Auth('mjg')
        self.assertTrue(mjg.sso_user.username == 'mjg', 'Incorrect username for sso_user: mjg')
        self.assertTrue(type(mjg.sso_user.authorities) is list, 'No authority list for sso_user')
        self.assertTrue(mjg.impersonated_user is None, 'Impersonated should be None')
        self.assertTrue(mjg.proxied_user is None, 'Proxy should be None')
        self.assertTrue(mjg.get_user().username == 'mjg', 'SSO user should be default user')
        self.assertTrue(mjg.start_impersonating('bbras'), 'Impersonating Brandon should work')
        self.assertTrue(mjg.impersonated_user.username == 'bbras', 'Impersonated username should be Brandon')
        self.assertTrue(mjg.proxied_user is None, 'Proxy should be None')
        self.assertTrue(mjg.get_user().username == 'bbras', 'Impersonated user should be default user')
        self.assertTrue(mjg.start_impersonating(''), 'Empty search value should remove Impersonated and not be an error')
        self.assertTrue(mjg.get_user().username == 'mjg', 'SSO user should be default user')
        self.assertFalse(mjg.start_impersonating('some-non-existing-user'), 'Invalid Impersonation should be an error')
        self.assertTrue(mjg.get_user().username == 'mjg', 'SSO user should be default user')

    def test_proxy(self):
        mjg = Auth('mjg')
        mjg.set_proxy('bbras')
        self.assertTrue(mjg.impersonated_user is None, 'Impersonated should be None')
        self.assertFalse(mjg.proxied_user is None, 'Proxy should NOT be None')
        self.assertTrue(mjg.get_user().username == 'mjg', 'SSO user should be default user')
        self.assertTrue(mjg.proxied_user.psu_id == '903645048', 'Incorrect PSU ID for proxy')

    def test_authority(self):
        mjg = Auth('mjg')
        self.assertTrue(mjg.has_authority('developer'), 'mjg should be a developer')
        mjg.start_impersonating('davidsh')
        self.assertFalse(mjg.has_authority('developer'), 'mjg as davidsh should NOT be a developer')
        mjg.start_impersonating(None)
        self.assertTrue(mjg.has_authority('developer'), 'mjg should be a developer again')
