from rest_framework.serializers import ModelSerializer

from .. import models


class UserSerializer(ModelSerializer):

    class Meta:
        model = models.User
        fields = (
            'id',
            'first_name',
            'last_name',
            'external_id',
            'email',
            'is_active',
            'is_staff',
            'is_superuser',
            'subscriber_code',
            'data',
        )


class UserUpdateSerializer(UserSerializer):

    class Meta:
        model = models.User
        fields = (
            'id',
            'first_name',
            'last_name',
            'external_id',
            'email',
            'is_active',
            'is_staff',
            'is_superuser',
            'subscriber_code',
            'data',
            'password',
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False,
            }
        }

    def create(self, validated_data):
        """ If given a password set it for the user """
        user = models.User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        if validated_data.get('password'):
            user.set_password(validated_data['password'])

        user.save()

        return user
