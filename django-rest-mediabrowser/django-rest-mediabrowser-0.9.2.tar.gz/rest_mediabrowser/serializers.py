from django.contrib.auth import get_user_model
from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
import logging
from .models import *


# Get an instance of a logger
logger = logging.getLogger(__name__)


class FlatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "first_name", "last_name")


class CollectionPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionPermission
        fields = ("user", "collection")


class CollectionSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    shared_with = serializers.SerializerMethodField()

    def get_shared_with(self, model):
        data = CollectionPermission.objects.filter(collection=model)
        return CollectionPermissionSerializer(data, many=True).data

    class Meta:
        model = Collection
        fields = ("id", "owner", "name", "shared_with")


class SharedCollectionSerializer(serializers.ModelSerializer):
    owner = FlatUserSerializer(read_only=True)

    class Meta:
        model = Collection
        fields = ("id", "owner", "name")


class FlatCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ("id", "name")


class ImagePermissionSerializer(serializers.ModelSerializer):
    user = FlatUserSerializer()

    class Meta:
        model = ImagePermission
        fields = ("user", "permission")


class FilePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilePermission
        fields = ("user", "permission")


class MediaImageSerializer(TaggitSerializer, serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    collection = FlatCollectionSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True)
    collection_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        required=False,
        source="collection",
        allow_null=True
        queryset=Collection.objects.all(),
    )
    tags = TagListSerializerField(required=False)
    shared_with = serializers.SerializerMethodField()

    thumbnail = serializers.SerializerMethodField()
    published_path = serializers.ReadOnlyField()

    def get_thumbnail(self, model):
        if not model.thumbnail:
            return ""
        return model.get_thumbnail_url()

    def get_shared_with(self, model):
        data = ImagePermission.objects.filter(image=model)
        return ImagePermissionSerializer(data, many=True).data

    def get_image_url(self, model):
        if not model.image:
            return ""
        # return model.image.name
        return model.get_image_url()

    def validate(self, data):
        vdata = super().validate(data)
        collection_data = vdata.get("collection", None)
        if collection_data:
            if (
                collection_data.owner == vdata["owner"]
                or CollectionPermission.objects.filter(
                    user=vdata["owner"], collection=collection_data, permission="e"
                ).exists()
            ):
                return vdata
            else:
                raise serializers.ValidationError(
                    "Not enough permission for adding to this collection"
                )
        else:
            return vdata

    class Meta:
        model = MediaImage
        fields = (
            "id",
            "owner",
            "collection",
            "image_url",
            "image",
            "description",
            "alt_text",
            "thumbnail",
            "height",
            "width",
            "shared_with",
            "published",
            "published_path",
            "collection_id",
            "tags",
        )


class SharedMediaImageSerializer(TaggitSerializer, serializers.ModelSerializer):
    owner = FlatUserSerializer(read_only=True)
    collection = FlatCollectionSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    tags = TagListSerializerField(required=False)
    permission = serializers.SerializerMethodField()

    def get_permission(self, model):
        try:
            return ImagePermission.objects.get(
                user=self.context["request"].user, image=model
            ).permission
        except:
            return ""

    def get_image_url(self, model):
        if not model.image:
            return ""
        return model.get_image_url()

    class Meta:
        model = MediaImage
        fields = (
            "owner",
            "collection",
            "image_url",
            "description",
            "alt_text",
            "height",
            "width",
            "published",
            "tags",
            "permission",
        )


class MediaFileSerializer(TaggitSerializer, serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    collection = FlatCollectionSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    file = serializers.FileField(write_only=True)
    collection_id = serializers.PrimaryKeyRelatedField(
        allow_null=True
        write_only=True,
        source="collection",
        required=False,
        queryset=Collection.objects.all(),
    )

    tags = TagListSerializerField(required=False)
    shared_with = serializers.SerializerMethodField()

    def get_shared_with(self, model):
        data = FilePermission.objects.filter(file=model)
        return FilePermissionSerializer(data, many=True).data

    def get_file_url(self, model):
        if not model.file:
            return ""
        return model.get_file_url()

    def validate(self, data):
        vdata = super().validate(data)
        collection_data = vdata.get("collection", None)
        if collection_data:
            if (
                collection_data.owner == vdata["owner"]
                or CollectionPermission.objects.filter(
                    user=vdata["owner"], collection=collection_data, permission="e"
                ).exists()
            ):
                return vdata
            else:
                raise serializers.ValidationError(
                    "Not enough permission for adding to this collection"
                )
        else:
            return vdata

    class Meta:
        model = MediaFile
        fields = (
            "id",
            "owner",
            "collection",
            "file_url",
            "file",
            "description",
            "shared_with",
            "published",
            "collection_id",
            "tags",
        )


class SharedMediaFileSerializer(TaggitSerializer, serializers.ModelSerializer):
    owner = FlatUserSerializer(read_only=True)
    collection = FlatCollectionSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    tags = TagListSerializerField()
    permission = serializers.SerializerMethodField()

    def get_permission(self, model):
        try:
            return FilePermission.objects.get(
                user=self.context["request"].user, file=model
            ).permission
        except:
            return ""

    def get_file_url(self, model):
        if not model.file:
            return ""
        return model.get_file_url()

    class Meta:
        model = MediaFile
        fields = (
            "id",
            "owner",
            "collection",
            "file_url",
            "description",
            "published",
            "tags",
            "permission",
        )
