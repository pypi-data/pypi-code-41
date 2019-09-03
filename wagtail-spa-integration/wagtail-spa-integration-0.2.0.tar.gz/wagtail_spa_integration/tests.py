from django.urls import reverse
from django.test import override_settings, RequestFactory
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.core.models import Page, Site
from wagtail.contrib.redirects.models import Redirect
from wagtail.tests.utils import WagtailPageTests
from rest_framework.test import APIRequestFactory
from .views import SPAExtendedPagesAPIEndpoint, RedirectViewSet, sitemap
from sandbox.models import FooPage


class WagtailSPAIntegrationTests(WagtailPageTests):
    @override_settings(PREVIEW_DRAFT_CODE="abc")
    def test_draft_api(self):
        home = Page.objects.last()
        old_title = home.title
        new_title = 'edit it'
        home.title = new_title
        home.save_revision()

        request = APIRequestFactory().get("")
        request.site = Site.objects.first()
        request.wagtailapi_router = WagtailAPIRouter('wagtailapi')
        page_detail = SPAExtendedPagesAPIEndpoint.as_view(
            {'get': 'detail_view'})
        res = page_detail(request, pk=home.pk)
        self.assertContains(res, old_title)
        self.assertNotContains(res, new_title)

        params = {'draft': 'abc'}
        request = APIRequestFactory().get("", params)
        request.site = Site.objects.first()
        request.wagtailapi_router = WagtailAPIRouter('wagtailapi')
        res = page_detail(request, pk=home.pk)
        self.assertContains(res, new_title)

    def test_sitemap_with_site(self):
        home = Page.objects.last()
        site2_hostname = "http://example.com"
        site2 = Site.objects.create(root_page=home, hostname=site2_hostname)
        params = {'site': site2.id}
        request = RequestFactory().get("sitemap.xml", params)
        res = sitemap(request)
        res.render()
        self.assertContains(res, site2_hostname)

    def test_redirect_viewset(self):
        params = {'old_path': '/lol/'}
        request = APIRequestFactory().get("", params)
        redirect_list = RedirectViewSet.as_view({'get': 'list'})
        Redirect.objects.create(
            old_path="/lol/", redirect_link="https://example.com")
        Redirect.objects.create(
            old_path="/test/", redirect_link="https://no.com")
        response = redirect_list(request)
        self.assertContains(response, "example.com")
        self.assertNotContains(response, "no.com")

    def test_exclude_type(self):
        home = Page.objects.last()
        foo = FooPage(title="foo")
        home.add_child(instance=foo)
        params = {'exclude_type': 'sandbox.FooPage'}
        request = APIRequestFactory().get("", params)
        request.site = Site.objects.first()
        request.wagtailapi_router = WagtailAPIRouter('wagtailapi')
        page_list = SPAExtendedPagesAPIEndpoint.as_view(
            {'get': 'listing_view'})
        res = page_list(request)
        self.assertNotContains(res, foo.title)
        self.assertEqual(res.data['meta']['total_count'], 1)

    def test_find_view(self):
        home = Page.objects.last()
        foo = FooPage(title="foo")
        home.add_child(instance=foo)

        url = "/api/v2/pages/find/"
        params = {"html_path": "/"}
        res = self.client.get(url, params)
        self.assertEqual(res.status_code, 302)

    def test_detail_by_path(self):
        home = Page.objects.last()

        url = "/api/v2/pages/detail_by_path/"
        params = {"html_path": "/"}
        res = self.client.get(url, params)
        self.assertContains(res, home.title)
