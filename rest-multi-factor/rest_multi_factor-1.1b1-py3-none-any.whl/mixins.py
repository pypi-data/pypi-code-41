"""Mixin classes for the multi factor viewsets."""

__all__ = (
    "DeviceMixin",
)

from functools import lru_cache


from rest_framework.exceptions import NotFound


from rest_multi_factor.utils import get_subclassed_models
from rest_multi_factor.models import Device

from rest_multi_factor.containers import GeneralDeviceContainer
from rest_multi_factor.containers import SpecificDeviceContainer


class DeviceMixin(object):
    """Mixin to handle devices."""

    def get_device(self, index):
        """
        Retrieve a device by it's identifier.

        :param index: The index of the device
        :type index: int

        :return: The requested device
        :rtype: rest_multi_factor.models.meta.DeviceMeta

        :raises rest_framework.exceptions.NotFound: When no device with the
        index was found.
        """
        index = int(index)
        devices = self.get_devices()

        if 0 <= index < len(devices):
            return devices[index]

        raise NotFound("The requested device could not be found.")

    def get_user_device(self, user, index):
        """
        Retrieve a device if it's owned by the current user.

        :param user: The current user instance
        :type user: django.contrib.auth.models.AbstractBaseUser

        :param index: The index of the device
        :type index: int

        :return: The request device
        :rtype: rest_multi_factor.models.meta.DeviceMeta

        :raises rest_framework.exceptions.NotFound: When no device with the
        index was found.
        """
        index = int(index)
        devices = self.get_user_devices(user, fill=True)

        if 0 <= index < len(devices) and devices[index] is not None:
            return devices[index]

        raise NotFound("The requested device could not be found.")

    @lru_cache(1)
    def get_devices(self):
        """
        Retrieve all available devices.

        :return: All the found devices
        :rtype: tuple of rest_multi_factor.models.meta.DeviceMeta
        """
        return get_subclassed_models(Device)

    def get_user_devices(self, user, fill=False):
        """
        Get all existing devices for this user.

        :param user: The current user instance
        :type user: django.contrib.auth.models.AbstractBaseUser

        :param fill: Whether or not to fill the gaps with 'None'
        :type fill: bool

        :return: The available devices
        :rtype: tuple
        """
        if fill:
            devices = (
                d if d.objects.filter(user=user).exists() else None
                for d in self.get_devices()
            )

        else:
            devices = (
                d for d in self.get_devices()
                if d.objects.filter(user=user).exists()
            )

        return tuple(devices)

    @lru_cache(1)
    def get_prepared_devices(self):
        """
        Get all generally prepared devices.

        :return: All Generally prepared devices.
        :rtype: tuple
        """
        devices = self.get_devices()

        return tuple(
            self.prepare_general(devices[i], i)
            for i in range(0, len(devices))
        )

    def get_prepared_user_devices(self, request):
        """
        Get all specific prepared devices.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :return: The user's devices specific prepared
        :rtype: tuple
        """
        devices = self.get_user_devices(request.user, fill=True)

        return tuple(
            self.prepare_specific(request, devices[i], i)
            for i in range(0, len(devices)) if devices[i] is not None
        )

    def prepare_specific(self, request, device, index):
        """
        Prepare a more detailed response.

        Extracts the general and user specific meta data
        from a device and put it into a container.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :param device: The model class of a device
        :type device: rest_multi_factor.models.meta.DeviceMeta

        :param index: The identifier of this device
        :type index: int

        :return: A container with the distributed info of a device
        :rtype: rest_multi_factor.containers.DeviceContainer
        """
        token = request.auth
        instance = device.objects.get(user=request.user)

        challenge = device.challenge.objects.get_or_create(
            device=instance, token=token
        )[0]
        confirmed = challenge.confirm

        return SpecificDeviceContainer(
            index, confirmed, device.verbose_name, device.dispatchable
        )

    def prepare_general(self, device, index):
        """
        Prepare a general response.

        Extract the general meta data from a device and
        put it into a container.

        :param device: The model class of a device
        :type device: rest_multi_factor.models.meta.DeviceMeta

        :param index: The identifier of this device
        :type index: int

        :return: A container with the distributed info of a device
        :rtype: rest_multi_factor.containers.DeviceContainer
        """
        return GeneralDeviceContainer(
            index, device.verbose_name, device.dispatchable
        )
