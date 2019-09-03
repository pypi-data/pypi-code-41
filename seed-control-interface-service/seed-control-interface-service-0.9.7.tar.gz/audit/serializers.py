from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):

    action_name = serializers.SerializerMethodField(required=False)

    class Meta:
        model = AuditLog
        read_only_fields = ('action_at', 'action_name')
        fields = ('action_at', 'action_by', 'action', 'model', 'identity_id',
                  'subscription_id', 'detail', 'action_name')

    def get_action_name(self, obj):
        return obj.get_action_display()
