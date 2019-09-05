import re

from django.conf import settings

from .faker_factory import faker


class RequestMockAccount:

    def __init__(self):
        self._requests = {}

    def reset(self):
        self._requests = {}

    def add_request(self, uuid, response):
        self._requests[uuid] = response

    def get_request(self, uuid):
        return self._requests.get(uuid)

    def update_mock(self, uuid, **kwargs):
        user_request = self.get_request(uuid)
        user_request.update(kwargs)

    def add_mock(self, user, is_consultant=False, **kwargs):
        response = {
            'uuid': str(user.uuid),
            'shortName': faker.first_name(),
            'fullName': faker.name(),
            'email': faker.email(),
            'groups': kwargs.get('groups', []),
            'consultantId': 1 if is_consultant else None,
            'profilePicture': [
                [[settings.SMALL_IMAGE_SIZE, settings.SMALL_IMAGE_SIZE], faker.image_url()],
                [[settings.MEDIUM_IMAGE_SIZE, settings.MEDIUM_IMAGE_SIZE], faker.image_url()],
                [[settings.LARGE_IMAGE_SIZE, settings.LARGE_IMAGE_SIZE], faker.image_url()],
                [[settings.DEFAULT_IMAGE_SIZE, settings.DEFAULT_IMAGE_SIZE], faker.image_url()],
            ],
            'userTitle': faker.word(),
            'profileUrl': faker.uri(),
            'bioMe': faker.text(),
            'linkedin': faker.uri(),
            'hubs': [{'_type': 'T'}] if is_consultant else [],
            'isActive': True,
            'isStaff': False,
            'isSuperuser': kwargs.get('is_superuser', False),
        }
        response.update(**kwargs)
        self.add_request(
            str(user.uuid),
            response=response)

