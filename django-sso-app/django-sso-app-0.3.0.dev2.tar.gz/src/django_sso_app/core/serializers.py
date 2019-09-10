from rest_framework import serializers


class PartialObjectSerializer(serializers.Serializer):
    _partial = serializers.SerializerMethodField(method_name='get_partial')

    def get_partial(self, obj):
        return True


class AbsoluteUrlSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(method_name='get_absolute_url')

    def get_absolute_url(self, obj):
        if getattr(obj, 'pk', None) is not None:
            get_absolute_url = getattr(obj, 'get_absolute_url', None)
            if get_absolute_url is None:
                raise NotImplementedError('Model must provide "get_absolute_url" method.')
            else:
                request = self.context['request']
                return request.build_absolute_uri(get_absolute_url())


class UserRelatedSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = getattr(obj, 'user', None)
        if user is not None:
            profile = getattr(user, 'profile', None)
            if profile is not None:
                request = self.context['request']
                reverse_url = profile.get_absolute_url()
                return request.build_absolute_uri(reverse_url)


class DeactivableSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False)


class PublicableSerializer(serializers.Serializer):
    is_public = serializers.BooleanField(required=False)


class TimespanSerializer(serializers.Serializer):
    started_at = serializers.DateTimeField(required=False)
    ended_at = serializers.DateTimeField(required=False)


class UpdatableSerializer(serializers.Serializer):
    updated_at = serializers.DateTimeField(required=False)


class CreatedAtSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField(required=False)
