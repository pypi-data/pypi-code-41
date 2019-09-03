from .models import (UserDashboard, Dashboard,
                     Widget, WidgetData, Definition)
from rest_framework import serializers


class WidgetDataSerializer(serializers.ModelSerializer):
    service = serializers.StringRelatedField(many=False)

    class Meta:
        model = WidgetData
        fields = ('id', 'title', 'key', 'service')


class WidgetSerializer(serializers.ModelSerializer):
    data = WidgetDataSerializer(many=True, read_only=True)

    class Meta:
        model = Widget
        fields = ('id', 'title', 'type_of', 'data_from', 'interval',
                  'nulls', 'data')


class DashboardSerializer(serializers.ModelSerializer):
    widgets = WidgetSerializer(many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = ('id', 'name', 'widgets')


class DashboardMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dashboard
        fields = ('id', 'name')


class UserDashboardSerializer(serializers.ModelSerializer):
    dashboards = DashboardMinimalSerializer(
        many=True, read_only=True)
    default_dashboard = DashboardMinimalSerializer(
        many=False, read_only=True)

    class Meta:
        model = UserDashboard
        fields = ('user_id', 'dashboards', 'default_dashboard')


class DefinitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Definition
        fields = ('id', 'title', 'description')
