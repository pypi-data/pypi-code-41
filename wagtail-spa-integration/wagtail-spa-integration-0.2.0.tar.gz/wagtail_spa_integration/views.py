from django.conf import settings
from django.conf.urls import url
from django.http import Http404
from django.shortcuts import redirect
from django_filters import rest_framework as filters
from wagtail.api.v2.endpoints import PagesAPIEndpoint
from wagtail.api.v2.utils import BadRequestError, page_models_from_string
from wagtail.contrib.sitemaps.views import sitemap as wagtail_sitemap
from wagtail.contrib.redirects.models import Redirect
from wagtail.core.models import Site
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .serializers import RedirectSerializer
from .utils import exclude_page_type


class SPAExtendedPagesAPIEndpoint(PagesAPIEndpoint):
    """
    Wagtail preview doesn't work with a JS client

    This tweaked Pages API will serve the latest draft version of a page when
    `?draft=[draft_code]` is set.

    Added `site` (id) and `site_hostname` query parameters to filter by site.

    Added `exclude_type` to exclude wagtail page types
    """
    known_query_parameters = PagesAPIEndpoint.known_query_parameters.union([
        'site',
        'site_hostname',
        'exclude_type',
    ])

    def detail_view(self, request, pk):
        instance = self.get_object()
        draft_code = getattr(settings, 'PREVIEW_DRAFT_CODE', None)
        if draft_code and request.GET.get('draft') == draft_code:
            instance = instance.get_latest_revision_as_page()
        elif not instance.live:
            raise Http404
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def find_view(self, request):
        """
        Override to append preview GET param to redirect url
        """
        url = super().find_view(request).url
        draft_code = request.GET.get('draft')
        draft_code = getattr(settings, 'PREVIEW_DRAFT_CODE', None)
        if draft_code and request.GET.get('draft') == draft_code:
            url += f"?draft={draft_code}"
        return redirect(url)

    def detail_by_path_view(self, request):
        """
        This should work similar to find_view except that it returns the detail response instead
        of a redirect.
        This can be useful with node, which has complications when handling redirects in a
        different manner than a web browser.
        """
        queryset = self.get_queryset()

        try:
            obj = self.find_object(queryset, request)

            if obj is None:
                raise self.model.DoesNotExist

        except self.model.DoesNotExist:
            raise Http404("not found")

        self.kwargs['pk'] = obj.pk
        return self.detail_view(request, obj.pk)

    def get_queryset(self):
        self.filter_by_site()
        queryset = super().get_queryset()
        queryset = self.exclude_page_types(queryset)
        return queryset

    def exclude_page_types(self, queryset):
        exclude_type = self.request.GET.get('exclude_type', None)
        if exclude_type is not None:
            try:
                models = page_models_from_string(exclude_type)
            except (LookupError, ValueError):
                raise BadRequestError("type doesn't exist")
            queryset = exclude_page_type(queryset, models)
        return queryset

    def filter_by_site(self):
        """
        Allow API consumer to manually specify the request.site
        Set query parameter `site` to the site id
        or set query parameter `site_hostname` to the hostname such as www.example.com 
        """
        site_id = self.request.GET.get('site', None)
        if site_id:
            try:
                self.request.site = Site.objects.get(id=site_id)
            except Site.DoesNotExist:
                raise BadRequestError("Site not found")
        site_hostname = self.request.GET.get('site_hostname', None)
        if site_hostname:
            try:
                self.request.site = Site.objects.get(hostname=site_hostname)
            except Site.DoesNotExist:
                raise BadRequestError("Site not found")

    @classmethod
    def get_urlpatterns(cls):
        urlpatterns = super().get_urlpatterns()
        urlpatterns.append(
            url(r'^detail_by_path/$',
                cls.as_view({'get': 'detail_by_path_view'}), name='detail_by_path')
        )
        return urlpatterns


class RedirectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Redirect.objects.all()
    serializer_class = RedirectSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('old_path', 'site')


def sitemap(request, sitemaps=None, **kwargs):
    """ Extended wagtail sitemap view. Adds `site` query parameter to site site ID """
    site_id = request.GET.get('site', None)
    if site_id:
        try:
            request.site = Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            pass

    return wagtail_sitemap(request, sitemaps=sitemaps, **kwargs)
