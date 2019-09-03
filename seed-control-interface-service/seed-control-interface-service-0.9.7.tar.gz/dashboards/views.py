from .models import UserDashboard, Dashboard, Definition
import django_filters.rest_framework as filters
from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import CursorPagination
from .serializers import (UserDashboardSerializer, DashboardSerializer,
                          DefinitionSerializer)


class CreatedAtCursorPagination(CursorPagination):
    ordering = "-created_at"


class DashboardViewSet(viewsets.ReadOnlyModelViewSet):

    """
    API endpoint that allows dashboard to be viewed
    """
    permission_classes = (IsAuthenticated,)
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    pagination_class = CreatedAtCursorPagination


class UserDashboardViewSet(viewsets.ReadOnlyModelViewSet):

    """
    API endpoint that allows user dashboard to be viewed
    """
    permission_classes = (IsAuthenticated,)
    queryset = UserDashboard.objects.all()
    serializer_class = UserDashboardSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ('user_id', )
    pagination_class = CreatedAtCursorPagination


class DefinitionViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):

    """
    API endpoint that allows definition to be created
    retrieved, updated and deleted
    """
    permission_classes = (IsAuthenticated,)
    queryset = Definition.objects.all()
    serializer_class = DefinitionSerializer
    pagination_class = CreatedAtCursorPagination
