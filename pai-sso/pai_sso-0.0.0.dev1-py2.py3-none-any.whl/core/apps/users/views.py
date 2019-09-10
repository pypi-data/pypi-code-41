import logging

from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.forms import ValidationError
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from allauth.account.models import EmailAddress

from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from ...permissions import StaffPermission, OwnerOrStaffPermission
from ...permissions import is_staff
from ...backend.functions import invalidate_cookie, get_request_jwt, update_response_jwt

from .models import User
from .serializers import (CheckUserExistenceSerializer, UserSerializer, NewUserSerializer,
                          UserUnsubscriptionSerializer, UserRevisionSerializer)

logger = logging.getLogger('users')

# Views
class TryAuthenticateMixin(object):

    def try_authenticate(self, username, email, password):
        credentials = username or email or None
        user = None

        if username is None and email is not None:
            credentials = 'email'
        if username is not None and email is None:
            credentials = 'username'

        if credentials is not None:
            user = authenticate(username=credentials, password=password)

        if user is not None:
            return user

        raise User.DoesNotExist('Check credentials.')

class CheckUserExistence(APIView):
    """
    Retrieve a "condensed" user instance {"id": ".."} by either "username" or "email" as query params.
    """

    def get_object(self, username=None, email=None):
        try:
            if username is None and email is not None:
                email_address = EmailAddress.objects.get(email=email)
                return email_address.user
            if username is not None and email is None:
                return User.objects.get(username=username)
            raise User.DoesNotExist('Either username or email must be set.')
        except (User.DoesNotExist, EmailAddress.DoesNotExist):
            raise Http404

    def get(self, *args, **kwargs):
        username = self.request.query_params.get('username', None)
        email = self.request.query_params.get('email', None)

        if username is not None or email is not None:
            item = self.get_object(username, email)
        else:
            raise Http404

        serializer = CheckUserExistenceSerializer(item)
        return Response(serializer.data)


class UserApiViewSet( mixins.UpdateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    """
    User related entrypoints
    """
    serializer_class = UserSerializer
    permission_classes = (OwnerOrStaffPermission, )

    def get_queryset(self):
        queryset = User.objects.all()
        return queryset

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        try:
            user = User.objects.get(pk=pk)
            self.check_object_permissions(self.request, user)
            return user
        except User.DoesNotExist:
            raise Http404

    def partial_update(self, request, *args, **kwargs):
        try:
            response = super(UserApiViewSet, self).partial_update(request, *args, **kwargs)
        except (IntegrityError, ValidationError) as e:
            logger.info('User {0} tried to update email with already registered one'.format(request.user))
            return Response(_('Email already registered.'), status=status.HTTP_409_CONFLICT)
        
        response_status_code = response.status_code
        logger.info('Partial_update status code is {}'.format(response_status_code))
        
        if response_status_code == 200:
            received_jwt = get_request_jwt(request)

            jwt_user = self.get_object()
            
            from_browser_as_same_user = received_jwt is not None and self.request.user == jwt_user
            # logger.info('From browser as same user? {}'. format(from_browser_as_same_user))

            if from_browser_as_same_user: # From browser as same user
                email_changed = self.request.user.email != jwt_user.email
                
                if email_changed:
                    logger.info('User {0} must confirm email'.format(jwt_user))
                else:
                    logger.info('User {0} must NOT confirm email'.format(jwt_user))
                    update_response_jwt(received_jwt, jwt_user, request, response)

        return response


class UserCreationApiViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    """
    Staff user creation entrypoint
    """

    permission_classes = (StaffPermission, )

    def get_queryset(self):
        user = self.request.user
        if is_staff(user):
            queryset = User.objects.filter(is_staff=False)
        else:
            queryset = User.objects.filter(is_staff=False, id=user.id)
        return queryset

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'POST':
            return NewUserSerializer
        else:
            return UserSerializer

    def list(self, request, *args, **kwargs):
        """
        List users
        """
        return super(UserCreationApiViewSet, self).list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = NewUserSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            created_user = serializer.save()
            created_user_serializer = UserSerializer(created_user, context={'request': request})
            return Response(created_user_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUnsubscriptionApiView(TryAuthenticateMixin, APIView):
    """
    Completely unsubscribes requesting user
    """

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = UserUnsubscriptionSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = user.username
        email = user.email
        password = serializer.data.get('password')

        has_unsubscribed = False
        user = self.try_authenticate(username, email, password)

        logger.info('User {0} wants to unregister from SSO'.format(user))

        if user == request.user:
            user.unsubscribe()
            has_unsubscribed = True
            user.refresh_from_db()
        else:
            logger.error('User {0} tried to unregister user {1} from SSO'.format(request.user, user))

        serializer = UserSerializer(user, context={'request': request})
        response = Response(serializer.data)

        if has_unsubscribed:
            invalidate_cookie(response)

        return response


class UserRevisionsApiView(generics.ListAPIView):
  """
  User revisions entrypoint
  """
  queryset = User.objects.all()
  serializer_class = UserRevisionSerializer
  permission_classes = (StaffPermission,)

  @method_decorator(cache_page(120))
  def list(self, request):
    # Note the use of `get_queryset()` instead of `self.queryset`
    queryset = self.get_queryset()
    serializer = self.serializer_class(queryset, many=True)
    return Response(serializer.data)
