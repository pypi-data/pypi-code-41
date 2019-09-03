import django_filters.rest_framework as filters
from rest_framework import generics
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated

from .models import AuditLog
from .serializers import AuditLogSerializer


class ActionAtCursorPagination(CursorPagination):
    ordering = "-action_at"


class AuditLogFilter(filters.FilterSet):
    class Meta:
        model = AuditLog
        fields = ['identity_id', 'subscription_id']


class AuditLogList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.all()
    pagination_class = ActionAtCursorPagination
    filter_class = AuditLogFilter

    def post(self, request, *args, **kwargs):
        if 'action' in request.data:
            action_choices = dict((y, x) for x, y in AuditLog.ACTION_CHOICES)
            request.data['action'] = action_choices.get(
                request.data['action'], request.data['action'])

        return super(AuditLogList, self).post(request, *args, **kwargs)
