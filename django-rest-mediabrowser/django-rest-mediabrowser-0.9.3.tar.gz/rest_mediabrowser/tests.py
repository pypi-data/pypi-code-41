from django.test import TestCase
from django.core.files import File
from rest_framework.test import APIRequestFactory, APIClient, force_authenticate
from .models import *
from django.contrib.auth import get_user_model

# Create your tests here.

UM = get_user_model()


class MediaImageTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = UM.objects.create(username='user1', password="user1pass")
        self.user2 = UM.objects.create(username='user2', password="user2pass")
        self.images = []
        with open('rest_mediabrowser/testfiles/1.png', 'rb') as infile:
            img1 = MediaImage.objects.create(
                owner=self.user1)
            img1.image.save('1.png', File(infile))
            self.images.append(img1)
            img2 = MediaImage.objects.create(
                owner=self.user1)
            img2.image.save('1.png', File(infile))
            self.images.append(img2)
            img3 = MediaImage.objects.create(
                owner=self.user2)
            img3.image.save('1.png', File(infile))
            self.images.append(img3)

    def test_authentication_restriction(self):
        # Check if user can access without login
        resp = self.client.get('/mediabrowser/images/')
        self.assertNotEqual(resp.status_code, 200)

        # Check if user can access with login
        self.client.force_authenticate(user=self.user1)
        resp2 = self.client.get('/mediabrowser/images/')
        self.assertEqual(resp2.status_code, 200)
        self.client.logout()

    def test_ownership_restrictions_in_listview(self):
        self.client.force_authenticate(user=self.user1)
        resp = self.client.get('/mediabrowser/images/')
        data = resp.json()
        self.assertEqual(2, len(data))
        self.client.logout()

        self.client.force_authenticate(user=self.user2)
        resp = self.client.get('/mediabrowser/images/')
        data = resp.json()
        self.assertEqual(1, len(data))
        self.client.logout()

    def test_ownership_restrictions_in_detailview(self):
        self.client.force_authenticate(user=self.user1)
        resp = self.client.get(f'/mediabrowser/images/{self.images[-1].id}/')
        error = resp.status_code >= 400
        self.assertEqual(True, error)
        self.client.logout()

        self.client.force_authenticate(user=self.user2)
        resp = self.client.get(f'/mediabrowser/images/{self.images[-1].id}/')
        success = resp.status_code >= 200 and resp.status_code < 300
        self.assertEqual(True, success)
        self.client.logout()

    def test_ownership_restrictions_in_updateview(self):
        desc = {"description": "Cool description"}
        self.client.force_authenticate(user=self.user1)
        resp = self.client.patch(f'/mediabrowser/images/{self.images[-1].id}/',
                                 desc,
                                 format='json')
        error = resp.status_code >= 400
        self.assertEqual(True, error)
        self.client.logout()

        self.client.force_authenticate(user=self.user2)
        resp = self.client.patch(f'/mediabrowser/images/{self.images[-1].id}/',
                                 desc,
                                 format='json')
        success = resp.status_code >= 200 and resp.status_code < 300
        self.assertEqual(resp.data['description'], desc['description'])
        self.assertEqual(True, success)
        self.client.logout()

    def test_ownership_restrictions_in_deleteview(self):
        self.client.force_authenticate(user=self.user1)
        resp = self.client.delete(
            f'/mediabrowser/images/{self.images[-1].id}/')
        error = resp.status_code >= 400
        self.assertEqual(True, error)
        self.client.logout()

        self.client.force_authenticate(user=self.user2)
        resp = self.client.delete(
            f'/mediabrowser/images/{self.images[-1].id}/')
        success = resp.status_code >= 200 and resp.status_code < 300
        self.assertEqual(True, success)
        self.client.logout()

    def tearDown(self):
        for img in self.images:
            img.image.delete(False)


class SharedMediaImageTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = UM.objects.create(username='user1', password="user1pass")
        self.user2 = UM.objects.create(username='user2', password="user2pass")
        self.images = []
        with open('rest_mediabrowser/testfiles/1.png', 'rb') as infile:
            img1 = MediaImage.objects.create(
                owner=self.user1)
            img1.image.save('1.png', File(infile))
            ImagePermission.objects.create(
                image=img1, user=self.user2, permission='v')
            self.images.append(img1)
            img2 = MediaImage.objects.create(
                owner=self.user1)
            img2.image.save('1.png', File(infile))
            ImagePermission.objects.create(
                image=img2, user=self.user2, permission='e')
            self.images.append(img2)
            img3 = MediaImage.objects.create(
                owner=self.user1)
            img3.image.save('1.png', File(infile))
            self.images.append(img3)

    def test_authentication_restriction(self):
        # Check if user can access without login
        resp = self.client.get('/mediabrowser/shared/images/')
        self.assertNotEqual(resp.status_code, 200)

        # Check if user can access with login
        self.client.force_authenticate(user=self.user2)
        resp2 = self.client.get('/mediabrowser/shared/images/')
        self.assertEqual(resp2.status_code, 200)
        self.client.logout()

    def test_ownership_restrictions_in_listview(self):
        self.client.force_authenticate(user=self.user1)
        resp = self.client.get('/mediabrowser/shared/images/')
        data = resp.json()
        self.assertEqual(0, len(data))
        self.client.logout()

        self.client.force_authenticate(user=self.user2)
        resp = self.client.get('/mediabrowser/shared/images/')
        data = resp.json()
        self.assertEqual(2, len(data))
        self.client.logout()

    def test_ownership_restrictions_in_detailview(self):
        self.client.force_authenticate(user=self.user2)
        resp = self.client.get(
            f'/mediabrowser/shared/images/{self.images[-1].id}/')
        error = resp.status_code >= 400
        self.assertEqual(True, error)

        resp = self.client.get(
            f'/mediabrowser/shared/images/{self.images[0].id}/')
        success = resp.status_code >= 200 and resp.status_code < 300
        self.assertEqual(True, success)

        resp = self.client.get(
            f'/mediabrowser/shared/images/{self.images[1].id}/')
        success = resp.status_code >= 200 and resp.status_code < 300
        self.assertEqual(True, success)
        self.client.logout()

    def test_ownership_restrictions_in_updateview(self):
        desc = {"description": "Cool description"}
        self.client.force_authenticate(user=self.user2)
        resp = self.client.patch(f'/mediabrowser/shared/images/{self.images[-1].id}/',
                                 desc,
                                 format='json')
        error = resp.status_code >= 400
        self.assertEqual(True, error)

        resp = self.client.patch(f'/mediabrowser/shared/images/{self.images[0].id}/',
                                 desc,
                                 format='json')
        error = resp.status_code >= 400
        self.assertEqual(True, error)

        resp = self.client.patch(f'/mediabrowser/shared/images/{self.images[1].id}/',
                                 desc,
                                 format='json')
        success = resp.status_code >= 200 and resp.status_code < 300
        self.assertEqual(resp.data['description'], desc['description'])
        self.assertEqual(True, success)
        self.client.logout()

    def test_ownership_restrictions_in_deleteview(self):
        self.client.force_authenticate(user=self.user2)
        for image in self.images:
            resp = self.client.delete(
                f'/mediabrowser/images/{image.id}/')
            error = resp.status_code >= 400
            self.assertEqual(True, error)
        self.client.logout()


class MediaFileTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = UM.objects.create(username='user1', password="user1pass")
        self.user2 = UM.objects.create(username='user2', password="user2pass")
        self.files = []
        with open('rest_mediabrowser/testfiles/1.png', 'rb') as infile:
            file1 = MediaFile.objects.create(
                owner=self.user1)
            file1.file.save('1.png', File(infile))
            self.files.append(file1)
            file2 = MediaFile.objects.create(
                owner=self.user1)
            file2.file.save('1.png', File(infile))
            self.files.append(file2)
            file3 = MediaFile.objects.create(
                owner=self.user2)
            file3.file.save('1.png', File(infile))
            self.files.append(file3)

    def test_authentication_restriction(self):
        # Check if user can access without login
        resp = self.client.get('/mediabrowser/files/')
        self.assertNotEqual(resp.status_code, 200)

        # Check if user can access with login
        self.client.force_authenticate(user=self.user1)
        resp2 = self.client.get('/mediabrowser/files/')
        self.assertEqual(resp2.status_code, 200)
        self.client.logout()

    def test_ownership_restrictions_in_listview(self):
        self.client.force_authenticate(user=self.user1)
        resp = self.client.get('/mediabrowser/files/')
        data = resp.json()
        self.assertEqual(2, len(data))
        self.client.logout()

        self.client.force_authenticate(user=self.user2)
        resp = self.client.get('/mediabrowser/files/')
        data = resp.json()
        self.assertEqual(1, len(data))
        self.client.logout()

    def test_ownership_restrictions_in_detailview(self):
        self.client.force_authenticate(user=self.user1)
        resp = self.client.get(f'/mediabrowser/files/{self.files[-1].id}/')
        error = resp.status_code >= 400
        self.assertEqual(True, error)
        self.client.logout()

        self.client.force_authenticate(user=self.user2)
        resp = self.client.get(f'/mediabrowser/files/{self.files[-1].id}/')
        success = resp.status_code >= 200 and resp.status_code < 300
        self.assertEqual(True, success)
        self.client.logout()

    def test_ownership_restrictions_in_updateview(self):
        desc = {"description": "Cool description"}
        self.client.force_authenticate(user=self.user1)
        resp = self.client.patch(f'/mediabrowser/files/{self.files[-1].id}/',
                                 desc,
                                 format='json')
        error = resp.status_code >= 400
        self.assertEqual(True, error)
        self.client.logout()

        self.client.force_authenticate(user=self.user2)
        resp = self.client.patch(f'/mediabrowser/files/{self.files[-1].id}/',
                                 desc,
                                 format='json')
        success = resp.status_code >= 200 and resp.status_code < 300
        self.assertEqual(resp.data['description'], desc['description'])
        self.assertEqual(True, success)
        self.client.logout()

    def test_ownership_restrictions_in_deleteview(self):
        self.client.force_authenticate(user=self.user1)
        resp = self.client.delete(
            f'/mediabrowser/files/{self.files[-1].id}/')
        error = resp.status_code >= 400
        self.assertEqual(True, error)
        self.client.logout()

        self.client.force_authenticate(user=self.user2)
        resp = self.client.delete(
            f'/mediabrowser/files/{self.files[-1].id}/')
        success = resp.status_code >= 200 and resp.status_code < 300
        self.assertEqual(True, success)
        self.client.logout()

    def tearDown(self):
        for f in self.files:
            f.file.delete(False)


class SharedMediaFileTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = UM.objects.create(username='user1', password="user1pass")
        self.user2 = UM.objects.create(username='user2', password="user2pass")
        self.files = []
        with open('rest_mediabrowser/testfiles/1.png', 'rb') as infile:
            file1 = MediaFile.objects.create(
                owner=self.user1)
            file1.file.save('1.png', File(infile))
            FilePermission.objects.create(
                file=file1, user=self.user2, permission='v')
            self.files.append(file1)
            file2 = MediaFile.objects.create(
                owner=self.user1)
            file2.file.save('1.png', File(infile))
            FilePermission.objects.create(
                file=file2, user=self.user2, permission='e')
            self.files.append(file2)
            file3 = MediaFile.objects.create(
                owner=self.user1)
            file3.file.save('1.png', File(infile))
            self.files.append(file3)

    def test_authentication_restriction(self):
        # Check if user can access without login
        resp = self.client.get('/mediabrowser/shared/files/')
        self.assertNotEqual(resp.status_code, 200)

        # Check if user can access with login
        self.client.force_authenticate(user=self.user2)
        resp2 = self.client.get('/mediabrowser/shared/files/')
        self.assertEqual(resp2.status_code, 200)
        self.client.logout()

    def test_ownership_restrictions_in_listview(self):
        self.client.force_authenticate(user=self.user1)
        resp = self.client.get('/mediabrowser/shared/files/')
        data = resp.json()
        self.assertEqual(0, len(data))
        self.client.logout()

        self.client.force_authenticate(user=self.user2)
        resp = self.client.get('/mediabrowser/shared/files/')
        data = resp.json()
        self.assertEqual(2, len(data))
        self.client.logout()

    def test_ownership_restrictions_in_detailview(self):
        self.client.force_authenticate(user=self.user2)
        resp = self.client.get(
            f'/mediabrowser/shared/files/{self.files[-1].id}/')
        error = resp.status_code >= 400
        self.assertEqual(True, error)

        resp = self.client.get(
            f'/mediabrowser/shared/files/{self.files[0].id}/')
        success = resp.status_code >= 200 and resp.status_code < 300
        self.assertEqual(True, success)

        resp = self.client.get(
            f'/mediabrowser/shared/files/{self.files[1].id}/')
        success = resp.status_code >= 200 and resp.status_code < 300
        self.assertEqual(True, success)
        self.client.logout()

    def test_ownership_restrictions_in_updateview(self):
        desc = {"description": "Cool description"}
        self.client.force_authenticate(user=self.user2)
        resp = self.client.patch(f'/mediabrowser/shared/files/{self.files[-1].id}/',
                                 desc,
                                 format='json')
        error = resp.status_code >= 400
        self.assertEqual(True, error)

        resp = self.client.patch(f'/mediabrowser/shared/files/{self.files[0].id}/',
                                 desc,
                                 format='json')
        error = resp.status_code >= 400
        self.assertEqual(True, error)

        resp = self.client.patch(f'/mediabrowser/shared/files/{self.files[1].id}/',
                                 desc,
                                 format='json')
        success = resp.status_code >= 200 and resp.status_code < 300
        self.assertEqual(resp.data['description'], desc['description'])
        self.assertEqual(True, success)
        self.client.logout()

    def test_ownership_restrictions_in_deleteview(self):
        self.client.force_authenticate(user=self.user2)
        for file in self.files:
            resp = self.client.delete(
                f'/mediabrowser/files/{file.id}/')
            error = resp.status_code >= 400
            self.assertEqual(True, error)
        self.client.logout()
