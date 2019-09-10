import logging

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from ..users.models import User
from ..users.serializers import UserUnsubscriptionSerializer, UserSerializer
from ..users.views import TryAuthenticateMixin
from ...backend.functions import get_request_jwt, update_response_jwt
from .models import Service
from .serializers import SubscriptionSerializer, ServiceSerializer

logger = logging.getLogger('services')


class ServiceApiViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """
    Service API viewset
    """

    serializer_class = ServiceSerializer
    permission_classes = (permissions.AllowAny, )

    def get_queryset(self):
        return Service.objects.filter(is_public=True)

    def subscribe(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        user = request.user
        service = Service.objects.get(id=pk)

        if service is None:
            raise Http404

        if user.subscriptions.filter(service=service).count() > 0:
            return Response('Already subscribed.', status=status.HTTP_409_CONFLICT)

        subscription_created = user.subscribe_to_service(service.url, update_rev=True)

        if subscription_created:
            response = Response('Subscribed.', status=status.HTTP_201_CREATED)
        else:
            return Response('Subscription error.', status=status.HTTP_500_SERVER_ERROR)


        if not settings.DEBUG:
            try:
                received_jwt = get_request_jwt(request)
                update_response_jwt(received_jwt, user, request, response)
            except KeyError as e:
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        return response


class SubscriptionApiViewSet(mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            TryAuthenticateMixin,
                            viewsets.GenericViewSet):

    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        queryset = self.request.user.subscriptions.all()
        return queryset

    def unsubscribe(self, request, *args, **kwargs):
        user_pk = self.kwargs.get('user_pk')
        pk = self.kwargs.get('pk')
        
        user = get_object_or_404(User.objects.all(), sso_id=user_pk)
        
        if user != request.user:
            return Response('Caller must be same user.', status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserUnsubscriptionSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = user.username
        email = user.email
        password = serializer.data.get('password')

        user = self.try_authenticate(username, email, password)

        subscription = self.get_queryset().filter(id=pk).first()
        logger.info('User {0} wants to unregister from service {1}'.format(user, subscription))
        user.unsubscribe_from_service(subscription, True) # user devices will be removed by User pre_save signal

        serializer = UserSerializer(user, context={'request': request})
        response = Response(serializer.data)


        if not settings.DEBUG:
          try:
              received_jwt = get_request_jwt(request)
              update_response_jwt(received_jwt, user, request, response)
          except KeyError as e:
              return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        return response

    def create(self, request, *args, **kwargs):
        user_pk = self.kwargs.get('user_pk')
        service_pk = self.kwargs.get('service_pk')

        requesting_user = request.user
        user = User.objects.get(sso_id=user_pk)
        requested_from_different_user = requesting_user != user
        
        if requested_from_different_user and not requesting_user.is_staff:
            return Response('Unauthorized.', status=status.HTTP_401_UNAUTHORIZED)

        service = Service.objects.get(id=service_pk)
        if service is None:
            raise Http404

        if user.subscriptions.filter(service=service).count() > 0:
            return Response('Already subscribed.', status=status.HTTP_409_CONFLICT)

        subscription_created = user.subscribe_to_service(service.url, update_rev=True)

        if subscription_created:
            response = Response('Subscribed.', status=status.HTTP_201_CREATED)
        else:
            return Response('Subscription error.', status=status.HTTP_500_SERVER_ERROR)

        if not requested_from_different_user:
            if not settings.DEBUG:
                try:
                    received_jwt = get_request_jwt(request)
                    update_response_jwt(received_jwt, user, request, response)
                except KeyError as e:
                    return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
        return response

