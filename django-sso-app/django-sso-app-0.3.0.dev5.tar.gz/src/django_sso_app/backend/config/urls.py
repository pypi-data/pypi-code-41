from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

if settings.DJANGO_SSO_BACKEND_ENABLED:
    from ..views import (ProfileView, ProfileUpdateView,
                         LoginAPIView, LogoutAPIView,
                         UserDetailsAPIView,
                         PasswordResetAPIView, PasswordResetConfirmAPIView, PasswordChangeAPIView,
                         RegisterAPIView, VerifyEmailAPIView,
                         LoginView, LogoutView, SignupView,
                         AccountInactiveView,
                         EmailView, ConfirmEmailView, EmailVerificationSentView,
                         PasswordResetFromKeyView, PasswordResetFromKeyDoneView,
                         PasswordResetDoneView, PasswordResetView,
                         PasswordChangeView, PasswordSetView,
                         WebpackBuiltTemplateView)

if settings.DJANGO_SSO_APP_ENABLED:
    pass

# pai
from django.utils import timezone
from django.views.decorators.http import last_modified
from django.views.i18n import JavaScriptCatalog

from ..views import SwaggerSchemaView, APIRoot, StatsView, AuthAPIRoot

from django_sso_app.core.apps.groups.urls import urlpatterns as groups_urls


last_modified_date = timezone.now()
js_info_dict = {}


urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    path("profile/", TemplateView.as_view(template_name="pages/profile.html"), name="profile"),

    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),

    # pai
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', last_modified(lambda req, **kw: last_modified_date)(JavaScriptCatalog.as_view()), js_info_dict,
        name='javascript-catalog'),
]


if settings.DJANGO_ALLAUTH_ENABLED:
    urlpatterns += [
        path("accounts/", include("allauth.urls")),
    ]

# Your stuff: custom urls includes go here
urlpatterns += []

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]

    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

rest_auth_urlpatterns = [
    # rest_auth
    url(r'^api/v1/auth/registration/$', RegisterAPIView.as_view(), name='rest_register'),
    url(r'^api/v1/auth/verify-email/$', VerifyEmailAPIView.as_view(), name='rest_verify_email'),
    # completely overrided
    # url(r'^api/v1/auth/registration/', include('rest_auth.registration.urls')),

    # rest_auth
    url(r'^api/v1/auth/login/', LoginAPIView.as_view(), name='rest_login'),
    url(r'^api/v1/auth/logout/', LogoutAPIView.as_view(), name='rest_logout'),

    url(r'^api/v1/auth/user/', UserDetailsAPIView.as_view(), name='user_helper_view'),

    url(r'^api/v1/auth/password/reset/$', PasswordResetAPIView.as_view(), name='rest_password_reset'),
    url(r'^api/v1/auth/password/reset/confirm/$', PasswordResetConfirmAPIView.as_view(),
        name='rest_password_reset_confirm'),
    url(r'^api/v1/auth/password/change/$', PasswordChangeAPIView.as_view(),
        name='rest_password_change'),
    # completely overrided
    # url(r'^api/v1/auth/', include('rest_auth.urls')),

    # url(r'^api/v1/groups/', include('django_sso_app.core.apps.groups.urls', namespace='groups')),
    # url(r'^api/v1/profiles/', include('django_sso_app.core.apps.profiles.urls', namespace='profiles')),
    # url(r'^api/v1/services/', include('django_sso_app.core.apps.services.urls', namespace='services')),
    # url(r'^api/v1/passepartout/', include('django_sso_app.core.apps.passepartout.urls', namespace='passepartout')),
]

allauth_urlpatterns = [
    url(r'^profile/update/$', ProfileUpdateView.as_view(), name='sso_profile_update'),

    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        WebpackBuiltTemplateView.as_view(),
        name='restauth_password_reset_confirm'),

    # allauth
    url(r"^signup/$", SignupView.as_view(), name="account_signup"),
    url(r"^login/$", LoginView.as_view(), name="account_login"),
    url(r"^logout/$", LogoutView.as_view(), name="account_logout"),

    url(r"^password/change/$", login_required(PasswordChangeView.as_view()),
        name="account_change_password"),
    url(r"^password/set/$", login_required(PasswordSetView.as_view()), name="account_set_password"),

    url(r"^inactive/$", AccountInactiveView.as_view(), name="account_inactive"),

    # E-mail
    url(r"^email/$", login_required(EmailView.as_view()), name="account_email"),
    url(r"^confirm-email/$", EmailVerificationSentView.as_view(),
        name="account_email_verification_sent"),
    url(r"^confirm-email/(?P<key>[-:\w]+)/$", ConfirmEmailView.as_view(),
        name="account_confirm_email"),

    # password reset
    url(r"^password/reset/$", PasswordResetView.as_view(),
        name="account_reset_password"),
    url(r"^password/reset/done/$", PasswordResetDoneView.as_view(),
        name="account_reset_password_done"),
    url(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)/(?P<key>.+)/$",
        PasswordResetFromKeyView.as_view(),
        name="account_reset_password_from_key"),
    url(r"^password/reset/key/done/$", PasswordResetFromKeyDoneView.as_view(),
        name="account_reset_password_from_key_done"),
    # completely overrided
    # url(r'^$', include('allauth.urls')),

    # catch all
    # url(r'^(?P<path>.*)/$', WebpackBuiltTemplateView.as_view(), name='fallback'),
    # url(r'^(?P<path>.*)/$', RedirectView.as_view(url='/login/')),
]

sso_auth_urlpatterns = [
    url(r'^api/v1/auth/groups/', include((groups_urls, 'groups'), namespace="group")),
]

if settings.DJANGO_SSO_BACKEND_ENABLED:
    from django_sso_app.core.apps.services.urls import urlpatterns as services_urls
    from django_sso_app.core.apps.passepartout.urls import urlpatterns as passepartout_urls
    from django_sso_app.core.apps.users.urls import urlpatterns as users_urls

    sso_auth_urlpatterns += [
        url(r'^api/v1/auth/users/', include((users_urls, 'users'), namespace="user")),
        url(r'^api/v1/services/', include((services_urls, 'services'), namespace="service")),
        url(r'^api/v1/passepartout/', include((passepartout_urls, 'passepartout'), namespace="passepartout")),
    ]
    sso_auth_urlpatterns += rest_auth_urlpatterns
    urlpatterns += allauth_urlpatterns

if settings.DJANGO_SSO_APP_ENABLED:
    from django_sso_app.core.apps.profiles.urls import urlpatterns as profiles_urls

    sso_auth_urlpatterns += [
        url(r'^api/v1/profiles/', include((profiles_urls, 'profiles'), namespace="profile")),
    ]


api_urlpatterns = sso_auth_urlpatterns + [
    url(r'^api/v1/_stats/$', StatsView.as_view(), name="stats"),

    # your api here
]

urlpatterns += api_urlpatterns

urlpatterns += [
    url(r'^api/v1/auth/', AuthAPIRoot.as_view(), name='authapi'),

    url(r'^api/v1/ui/$', APIRoot.as_view(), name="drf"),
    url(r'^api/v1/$', SwaggerSchemaView.as_view(patterns=api_urlpatterns), name="swagger")
]

