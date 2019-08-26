"""Views for handling two factor authentication."""

__all__ = (
    "MultiFactorVerifierViewSet",
    "MultiFactorRegistrationViewSet",
)

import itertools

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.decorators import throttle_classes

from rest_multi_factor.mixins import DeviceMixin
from rest_multi_factor.registry import registry
from rest_multi_factor.settings import multi_factor_settings
from rest_multi_factor.throttling import AbstractDelayingThrottle
from rest_multi_factor.serializers import DeviceSerializer, ValueSerializer
from rest_multi_factor.permissions import IsVerifiedOrNoDevice
from rest_multi_factor.permissions import IsTokenAuthenticated


class MultiFactorVerifierViewSet(DeviceMixin, ViewSet):
    """
    ViewSet for user-specific device manipulations.

    This viewset defines APIs that allow for user specific actions
    such as validating a user's device or dispatching one.
    """

    field = "value"

    lookup_field = "index"
    lookup_value_regex = r"\d+"

    backend_class = multi_factor_settings.DEFAULT_BACKEND_CLASS

    serializer_class = ValueSerializer
    permission_classes = (IsTokenAuthenticated,)

    def overview(self, request):
        """
        Serve a overview.

        Serves a overview of all available devices for
        the current user and if they are already confirmed.

        The index of the returned array will be the id to use,
        because we're not listing database records but database
        tables (in a way).

        :param request: The current used request instance
        :type request: rest_framework.request.Request

        :return: The response for this request
        :rtype: rest_framework.response.Response
        """
        devices = self.get_prepared_user_devices(request)
        return Response(data=DeviceSerializer(devices, many=True).data)

    def retrieve(self, request, **kwargs):
        """
        Serve a more detailed description of a device.

        :param request: The current request instance
        :type request: rest_framework.requests.Request

        :param kwargs: Additional keyword arguments
        :type kwargs: int

        :return: A response for the request
        :rtype: rest_framework.response.Response
        """
        device = self.get_user_device(request.user, **kwargs)
        prepared = self.prepare_specific(request, device, **kwargs)

        return Response(data=DeviceSerializer(prepared).data)

    @throttle_classes(multi_factor_settings.VERIFICATION_THROTTLING_CLASSES)
    def verify(self, request, **kwargs):
        """
        Verify a token with the submitted value.

        :param request: The current request instance
        :type request: rest_framework.requests.Request

        :param kwargs: Additional keyword arguments
        :type kwargs: int

        :return: A response for the request
        :rtype: rest_framework.response.Response
        """
        val = self.get_value(request)
        dev = self.get_user_device(request.user, **kwargs)

        instance = dev.objects.get(user=request.user)
        queryset = dev.challenge.objects.filter(device=instance)

        confirmed = False

        # Dispatchable challenges usually generate the value
        # just before dispatching. To make sure that this is
        # still respected we won't create a new challenge for
        # dispatchable challenges when they don't yet exist.
        if dev.dispatchable:
            challenge = get_object_or_404(
                queryset, token=request.auth, confirm=False
            )
            confirmed = challenge.verify(val)

        elif not queryset.filter(token=request.auth, confirm=True).exists():
            challenge = queryset.get_or_create(
                device=instance, token=request.auth, confirm=False
            )[0]
            confirmed = challenge.verify(val)

        if not confirmed:
            headers = {
                "WWW-Authenticate": "JSON realm=\"multi factor verification\""
            }
            return Response(status=401, headers=headers)

        backend = self.get_backend()
        counted = backend.verify(request.auth, self)

        self.clear_cache(self.get_throttles(), request)

        return Response({"verifications-left": counted}, status=200)

    def dispatch_challenge(self, request, **kwargs):
        """
        Dispatch a challenge for validating.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :param kwargs: The additional keyword arguments
        :type kwargs: int

        :return: The response for this request
        :rtype: rest_framework.response.Response
        """
        device = self.get_user_device(request.user, **kwargs)
        if not device.dispatchable:
            raise NotFound("The requested device could not dispatch.")

        instance = get_object_or_404(device, user=request.user)
        challenge = device.challenge.objects.get_or_create(
            device=instance, token=request.auth
        )[0]

        if challenge.confirm:
            return Response({
                "message": "The token is already verified", "code": 409
            }, 409)

        challenge.dispatch()
        return Response(status=204)

    def get_value(self, request):
        """
        Extract the value that needs to be verified from a request.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :return: The value to verify
        :rtype: str
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(True)

        return serializer.validated_data[self.get_field()]

    def get_field(self):
        """
        Retrieve the lookup field for the request.

        This can be overridden to allow different
        payload formats for different devices.

        :return: The lookup field that will be used
        :rtype: str
        """
        assert isinstance(self.field, str), (
            "'{name}' should either include attribute of type str, "
            "or override the `get_field()` method."
            "".format(name=self.__class__.__name__)
        )

        return self.field

    def get_backend(self):
        """
        Retrieve the backend class to use.

        :return: The backend class to use
        :rtype: rest_multi_factor.backends.AbstractVerificationBackend
        """
        assert self.backend_class is not None, (
            "'{0}' should either include a `backend_class` attribute, "
            "or override the `get_backend()` method."
            .format(self.__class__.__name__)
        )

        return self.backend_class()

    def get_serializer(self, *args, **kwargs):
        """
        Instantiate  the serializer for the current device.

        Returns the serializer instance that should be used for
        validating the integrity of the payload.

        :param args: The additional arguments for the serializer
        :type args: any

        :param args: The additional keyword arguments for the serializer
        :type args: any

        :return: The serializer instance to use for verification
        :rtype: rest_framework.serializers.Serializer
        """
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()

        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
            "'{0}' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            .format(self.__class__.__name__)
        )

        return self.serializer_class

    def get_serializer_context(self):
        """
        Additional context provided to the serializer class.

        :return: The additional context to provide
        :rtype: dict
        """
        return {"view": self, "request": self.request}

    def clear_cache(self, classes, request):
        """
        Clear the cache of the verification throttlers.

        :param classes: The throttle classes to clear
        :type classes: iterable

        :param request: The current request instance
        :type request: rest_framework.request.Request
        """
        throttles = (
            c for c in classes if isinstance(c, AbstractDelayingThrottle)
        )

        for klass in throttles:
            klass.clear(request)

    def get_throttles(self):
        """
        Instantiate and returns the list of throttles that this view uses.

        Overridden so action specific throttle classes are also added.

        :return: The initiated throttles
        :rtype: list
        """
        return [throttle() for throttle in self.get_throttle_classes()]

    def get_throttle_classes(self):
        """
        Get all throttle classes for the action.

        :return: The throttle classes
        :rtype: itertools.chain
        """
        handler = getattr(self, self.action)
        classes = getattr(handler, "throttle_classes", ())

        return itertools.chain(classes, self.throttle_classes)


class MultiFactorRegistrationViewSet(DeviceMixin, ViewSet):
    """Viewset for registering new devices for a user."""

    device = None

    lookup_field = "index"
    lookup_value_regex = r"\d+"

    permission_classes = (IsVerifiedOrNoDevice,)

    def register(self, request, **kwargs):
        """
        Register a device for a user.

        This view allows a user to register a device for himself.
        As a response will the new device be serialized by the
        related serializer from the register.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :return: A response with the serialized device
        :rtype: rest_framework.response.Response
        """
        self.device = self.get_device(**kwargs)

        if self.device.objects.filter(user=request.user).exists():
            return Response(status=status.HTTP_409_CONFLICT)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save(user=request.user)
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def overview(self, *_, **__):
        """
        Serve a overview of all devices that can be registered.

        :return: The current response
        :rtype: rest_framework.response.Response
        """
        devices = self.get_prepared_devices()
        content = DeviceSerializer(devices, many=True).data

        return Response(data=content)

    def get_serializer(self, *args, **kwargs):
        """
        Instantiate the serializer.

        :param args: Additional arguments to pass on
        :type args: any

        :param kwargs: Additional keywords arguments to pass on
        :type kwargs: any

        :return: The instance of the serializer to use
        :rtype: rest_framework.serializers.Serializer
        """
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        """
        Retrieve the serializer class for the current device.

        :return: The class to use for this device.
        :rtype: type of rest_framework.serializers.Serializer
        """
        return registry[self.device]

    def options(self, request, **kwargs):
        """
        Serve a options request with metadata.

        Overridden to set the device for the serializer
        as a instance attribute.

        :param request: The current request instance
        :type request: rest_framework.requests.Request


        :param kwargs: Additional keyword arguments
        :type kwargs: int

        :return: A response for the request
        :rtype: rest_framework.response.Response
        """
        if "index" in kwargs.keys():
            self.device = self.get_device(**kwargs)

        return super().options(request, **kwargs)
