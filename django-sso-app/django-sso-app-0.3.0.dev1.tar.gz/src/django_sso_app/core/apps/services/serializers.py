import logging

from rest_framework import serializers

from .models import Service, Subscription

logger = logging.getLogger('services')


class ServiceSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(required=False)
    is_unsubscribed = serializers.SerializerMethodField(required=False)
    tos = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Service
        read_only_fields = ('id', 'is_subscribed', 'picture', 'is_unsubscribed')
        fields = read_only_fields + ('url', 'name',
                                     'role', 'cookie_domain',
                                     'redirect_wait',
                                     'tos',
                                     'subscription_required')

    def get_is_subscribed(self, instance):
        request = self.context.get("request")
        user = request.user
        if user.is_anonymous:
            return False
        return request.user.subscriptions.filter(service=instance).count() > 0

    def get_is_unsubscribed(self, instance):
        request = self.context.get("request")
        user = request.user
        if user.is_anonymous:
            return False
        subscription = request.user.subscriptions.filter(service=instance).first()
        if subscription is not None:
            return subscription.unsubscribed_at is not None
        return False

    def get_tos(self, instance):
        request = self.context.get('request')
        language = request.LANGUAGE_CODE
        tos = instance.get_tos(language)

        if tos is None:
            instance.get_tos('en')

        if tos is None:
            return None
        return tos.text


class SubscriptionSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()

    class Meta:
        model = Subscription
        fields = ('id', 'service', 'created_at', 'is_unsubscribed')

