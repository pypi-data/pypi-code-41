import logging

from rest_framework import serializers
from rest_framework import viewsets

log = logging.getLogger(__name__)


def get_serializers_with_all_fields(modelClass):
    class DynamicModelSerializer(serializers.ModelSerializer):
        def get_default_field_names(self, declared_fields, model_info):
            """Return the default list of field names that will be used if the `Meta.fields` option is not specified."""
            return (
                    [self.url_field_name, 'id'] +
                    list(declared_fields.keys()) +
                    list(model_info.fields.keys()) +
                    list(model_info.forward_relations.keys())
            )

        class Meta:
            model = modelClass
            fields = '__all__'
            depth = 5

    return DynamicModelSerializer


def get_api_views_with_all_fields_readonly(models):
    dynamic_class = []
    for m in models:
        class DynamicViewSet(viewsets.ReadOnlyModelViewSet):
            queryset = m.objects.all().order_by('-id')
            serializer_class = get_serializers_with_all_fields(m)
            filter_fields = list([
                i.name for i in filter(
                    lambda x: x.__class__.__name__ != 'JSONField', [i for i in m._meta.concrete_fields]
                )]
            )

        dynamic_class.append(DynamicViewSet)
    return dynamic_class


def get_api_views_with_all_fields_create_read(models):
    dynamic_class = []
    for m in models:
        class DynamicViewSet(viewsets.ModelViewSet):
            queryset = m.objects.all().order_by('-id')
            serializer_class = get_serializers_with_all_fields(m)
            _fields = [i for i in m._meta.concrete_fields]
            filter_fields = list([
                i.name for i in filter(
                    lambda x: x.__class__.__name__ != 'JSONField', _fields)
            ])

        dynamic_class.append(DynamicViewSet)

    return dynamic_class


def register_with_router(router, views):
    # Add api where all the fields are exposed
    for v in views:
        if hasattr(v, 'api_name'):
            url = "{}/{}".format(
                v.queryset.query.model.__module__.lower().split('.models')[0],
                v.api_name)
            router.register(url, v, base_name=v.api_name)
        elif hasattr(v, 'queryset') and v.queryset is not None:
            url = "{}/{}".format(
                v.queryset.query.model.__module__.lower().split('.models')[0],
                v.queryset.query.model.__name__.lower())
            router.register(url, v)
        else:
            log.warning('View {v} can not be registered at this movement'.format(v=v))
