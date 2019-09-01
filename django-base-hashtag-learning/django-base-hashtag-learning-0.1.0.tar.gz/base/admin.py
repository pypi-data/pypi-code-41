from django.contrib import admin

from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from .models import QI, Theme, ThemeFeature, FeatureExemplification

class QIResource(resources.ModelResource):
    class Meta:
        model = QI


class QIAdmin(ImportExportModelAdmin):
    resource_class = QIResource


class ThemeResource(resources.ModelResource):
    qi = fields.Field(
        column_name='qi',
        attribute='qi',
        widget=ForeignKeyWidget(QI, 'qi_text')
    )

    class Meta:
        model = Theme


class ThemeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ThemeResource

    def get_list_display(self, request):
        return 'theme_number', 'theme_name',


class ThemeFeatureResource(resources.ModelResource):

    theme = fields.Field(
        column_name='theme',
        attribute='theme',
        widget=ForeignKeyWidget(Theme, 'theme_name')
    )

    class Meta:
        model = ThemeFeature


class ThemeFeatureAdmin(ImportExportModelAdmin):
    resource_class = ThemeFeatureResource
    readonly_fields = ('id',)



    list_display = ['get_theme_number', 'key_feature', 'exemplification_header', 'user_type', 'is_departmental']

    def get_theme_number(self, obj):
        return obj.theme.theme_number

    get_theme_number.admin_order_field = 'theme'
    get_theme_number.short_description = 'Theme Number'

    list_filter = ['primary_only', 'secondary_only', 'is_departmental']


# Override ForeignKeyWidget to return a match of key_feature AND user_type
# This is because there is the same key feature for Teacher and Leader
# and when importing we only want to get the correct one.
# Also need to map departmental / non-departmental
class FeatureExemplificationForeignKeyWidget(ForeignKeyWidget):
    def get_queryset(self, value, row, *args, **kwargs):
        return self.model.objects.filter(
            key_feature=row["theme_feature"],
            user_type=row["user_type"],
            is_departmental=row['is_departmental']
        )

class FeatureExemplificationResource(resources.ModelResource):

    theme_feature = fields.Field(
        column_name='theme_feature',
        attribute='theme_feature',
        widget=FeatureExemplificationForeignKeyWidget(ThemeFeature, 'key_feature')
    )

    class Meta:
        model = FeatureExemplification

class FeatureExemplificationAdmin(ImportExportModelAdmin):
    resource_class = FeatureExemplificationResource
    readonly_fields = ('id', )
    list_filter = ['user_type', 'is_departmental', 'theme_feature__key_feature',]

    list_display = ['get_theme_number', 'theme_feature', 'exemplification', 'user_type', 'is_departmental',]

    def get_theme_number(self, obj):
        return obj.theme_feature.theme.theme_number

    #get_theme_number.admin_order_field = 'theme'
    get_theme_number.short_description = 'Theme Number'



admin.site.register(QI, QIAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(ThemeFeature, ThemeFeatureAdmin)
admin.site.register(FeatureExemplification, FeatureExemplificationAdmin)