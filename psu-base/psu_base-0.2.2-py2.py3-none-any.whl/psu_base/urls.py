from django.urls import path

from . import views
from django.conf.urls import url
import django_cas_ng.views as cas_views

urlpatterns = [
    # For now, use the test page as default
    path('', views.test_status, name='index'),

    # Feature Toggles
    path('features', views.feature_list, name='features'),
    path('add_feature', views.add_feature, name='add_feature'),
    path('modify_feature', views.modify_feature, name='modify_feature'),
    path('delete_feature', views.delete_feature, name='delete_feature'),

    # Admin Scripts
    path('scripts', views.script_list, name='scripts'),
    path('add_script', views.add_script, name='add_script'),
    path('modify_script', views.modify_script, name='modify_script'),
    path('delete_script', views.delete_script, name='delete_script'),

    # Audit Events
    path('audit', views.audit_list, name='audit'),

    # Email Logs
    path('emails', views.email_list, name='emails'),
    path('display_email', views.display_email, name='display_email'),
    path('resend_email', views.resend_email, name='resend_email'),

    # Testing pages
    path('test', views.test_status, name='test'),
    path('versions', views.test_versions, name='versions'),
    path('session', views.test_session, name='session'),
    path('finti', views.FintiView.as_view(), name='finti'),
    path('email', views.email_test_page, name='email'),

    # Authentication and CAS login/logout endpoints
    path('stop_impersonating', views.stop_impersonating, name='stop_impersonating'),
    path('start_impersonating', views.start_impersonating, name='start_impersonating'),
    path('stop_proxying', views.stop_proxying, name='stop_proxying'),
    path('start_proxying', views.start_proxying, name='start_proxying'),
    path('proxy_search', views.proxy_search, name='proxy_search'),
    path('initiate_auth', views.initiate_auth, name='initiate_auth'),
    url('login', cas_views.LoginView.as_view(), name='login'),
    url('logout', cas_views.LogoutView.as_view(), name='logout'),

    # Messages
    path('messages', views.messages, name='messages'),
]
