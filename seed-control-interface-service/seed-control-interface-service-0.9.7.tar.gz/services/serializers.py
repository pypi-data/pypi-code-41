from django.contrib.auth.models import User, Group
from .models import Service, Status, UserServiceToken
from rest_hooks.models import Hook
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'groups')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        read_only_fields = ('created_at', 'updated_at')
        fields = ('id', 'name', 'url', 'token', 'up', 'metadata',
                  'created_at', 'created_by', 'updated_at', 'updated_by')


class ServiceLimitedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        read_only_fields = ('name', 'url')
        fields = ('name', 'url')


class StatusSerializer(serializers.ModelSerializer):
    service = serializers.StringRelatedField(many=False)

    class Meta:
        model = Status
        read_only_fields = ('service', 'up', 'created_at', 'result')
        fields = ('id', 'service', 'up', 'created_at', 'result')


class UserServiceTokenSerializer(serializers.ModelSerializer):
    service = ServiceLimitedSerializer(many=False)

    class Meta:
        model = UserServiceToken
        fields = ('user_id', 'email', 'service', 'token',
                  'created_at', 'updated_at')


class UserTokenRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    email = serializers.EmailField()


class HookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hook
        read_only_fields = ('user',)
        fields = "__all__"
