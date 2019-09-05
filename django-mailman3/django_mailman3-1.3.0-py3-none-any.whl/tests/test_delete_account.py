# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2019 by the Free Software Foundation, Inc.
#
# This file is part of Django-Mailman.
#
# Django-Mailman is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Django-Mailman is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Django-Mailman.  If not, see <http://www.gnu.org/licenses/>.
#


from django.contrib.auth.models import User
from django.urls import reverse

from mock import Mock

from django_mailman3.models import Profile
from django_mailman3.tests.utils import TestCase


class AccountDeletionTests(TestCase):

    def setUp(self):
        self.mm_user = Mock()
        self.mm_user.user_id = "dummy"
        self.mailman_client.get_user.side_effect = lambda e: self.mm_user
        self.user = User.objects.create_user(
            'testuser', 'test@example.com', 'testPass',
            first_name="firstname", last_name="lastname",
            )
        self.client.login(username='testuser', password='testPass')

    def test_get_page(self):
        response = self.client.get(reverse('mm_user_account_delete'))
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        user_id = self.user.id
        self.assertTrue(Profile.objects.filter(user_id=user_id).exists())
        response = self.client.post(
            reverse('mm_user_account_delete'), {})
        self.assertEquals(response.url, '/')
        self.assertEquals(response.status_code, 302)
        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertFalse(Profile.objects.filter(user_id=user_id).exists())
        self.mm_user.delete.assert_called()
