""" Url router for the schema viewer application
"""
from django.conf.urls import url

from core_parser_app.views.common import views as common_parser_views
from core_schema_viewer_app.views.user import views as user_views
from core_schema_viewer_app.views.user import ajax as user_ajax

urlpatterns = [
    url(r'^$', user_views.index,
        name='core_schema_viewer_index'),
    url(r'^oxygen-viewer/(?P<pk>\w+)$', user_views.oxygen_viewer,
        name='core_schema_viewer_oxygen_viewer'),
    url(r'^sandbox/(?P<pk>\w+)$', user_views.sandbox_view,
        name='core_schema_viewer_sandbox_view'),
    url(r'^generate-element/(?P<sandbox_data_structure_id>\w+)$', user_ajax.generate_element,
        name='core_schema_viewer_sandbox_generate_element'),
    url(r'^generate-choice/(?P<sandbox_data_structure_id>\w+)$', user_ajax.generate_choice,
        name='core_schema_viewer_sandbox_generate_choice'),
    url(r'^remove-element$', user_ajax.remove_element,
        name='core_schema_viewer_sandbox_remove_element'),
    url(r'^clear-fields$', user_ajax.clear_fields,
        name='core_schema_viewer_sandbox_clear_fields'),
    url(r'^download-xml/(?P<sandbox_data_structure_id>\w+)$', user_views.download_xml,
        name='core_schema_viewer_sandbox_download_xml'),
    url(r'^preview-xml/(?P<sandbox_data_structure_id>\w+)$', user_views.preview_xml,
        name='core_schema_viewer_sandbox_preview_xml'),
    url(r'^download-template$', user_views.download_template,
        name='core_schema_viewer_download_template'),
    url(r'^schema-viewer-redirect$', user_views.SchemaViewerRedirectView.as_view(),
        name='core_schema_viewer_schema_viewer_redirect'),
    url(r'^schema-viewer-tabbed/(?P<pk>\w+)$', common_parser_views.ManageModulesUserView.as_view(
            back_to_previous_url="core_schema_viewer_index",
            read_only=True,
            title="Schema Viewer"
        ),
        name='core_schema_viewer_schema_viewer_tabbed'),
]
