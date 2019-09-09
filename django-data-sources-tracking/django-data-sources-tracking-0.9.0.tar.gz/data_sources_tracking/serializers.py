# -*- coding: utf-8 -*-
from rest_framework import serializers

from . import models


class FileSerializer(serializers.ModelSerializer):
    """Serializer for Files."""

    class Meta:
        model = models.File
        fields = (
            'id', 'content', 'name', 'description', 'url', 'path',
            'type', 'relative_path', 'hash',
            'active', 'created', 'modified',
        )
