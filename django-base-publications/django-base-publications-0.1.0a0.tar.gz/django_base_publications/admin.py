from urllib.parse import urlunsplit
from django.contrib import admin
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class PublicationAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'status',
        'publication_date',
        'owner',
    )
    readonly_fields = (
        'created_date',
        'last_modified_date',
        'guest_link',
        'views_count',
    )

    list_filter = [
        'status',
        'owner',
        'is_hidden',
        'publication_date',
        'created_date',
        'last_modified_date',
    ]
    search_fields = (
        'title',
        'slug',
    )

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'status',
                'publication_date',
                'is_hidden',
            ),
        }),
        (_('Additionally'), {
            'fields': (
                'owner',
                'slug',
                'guest_link',
            ),
        })
    )

    def guest_link(self, obj):
        if obj.pk:
            site = Site.objects.get(id=settings.SITE_ID)
            return urlunsplit((settings.SITE_SCHEME, site.domain, obj.absolute_url, f'token={obj.token}', ''))
        return ""

    guest_link.short_description = _('Slug')

    def save_model(self, request, obj, form, change):
        if not getattr(obj, 'owner', None):
            obj.owner = request.user
            
        super().save_model(request, obj, form, change)
