from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.i18n import JavaScriptCatalog
from django.utils import timezone
from django.views.decorators.http import last_modified
from django.views.static import serve
from django.views.generic import TemplateView

from django.contrib.auth.decorators import login_required

from rest_framework_swagger.views import get_swagger_view

from ..apps.groups.urls import urlpatterns as groups_urls

if settings.DJANGO_SSO_BACKEND_ENABLED:
    from .views import (ProfileView, ProfileUpdateView,
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

last_modified_date = timezone.now()

js_info_dict = {}

urlpatterns = [
    # sso
    #url(r'^$', WebpackBuiltTemplateView.as_view(), name='home'),

    # django views
    url(r'^admin/', admin.site.urls),

    url(r'^docs/$', get_swagger_view(title='API Docs'), name='api_docs'),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', last_modified(lambda req, **kw: last_modified_date)(JavaScriptCatalog.as_view()),
        js_info_dict,
        name='javascript-catalog'),
]

if settings.DJANGO_SSO_BACKEND_ENABLED:
    urlpatterns += [
        url(r'^$', ProfileView.as_view(), name='sso_profile'),

        url(r'^profile/update/$', ProfileUpdateView.as_view(), name='sso_profile_update'),

        url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            WebpackBuiltTemplateView.as_view(),
            name='restauth_password_reset_confirm'),

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

if settings.DJANGO_SSO_APP_ENABLED:
    urlpatterns += [
        url(r'^$', TemplateView.as_view(template_name="home.html"), name='profile'),
    ]
sso_auth_urlpatterns = [
    url(r'^api/v1/groups/', include((groups_urls, 'groups'), namespace="group")),
]

if settings.DJANGO_SSO_BACKEND_ENABLED:
    from ..apps.services.urls import urlpatterns as services_urls
    from ..apps.passepartout.urls import urlpatterns as passepartout_urls
    from ..apps.users.urls import urlpatterns as users_urls
    sso_auth_urlpatterns += [
        url(r'^api/v1/services/', include((services_urls, 'services'), namespace="service")),
        url(r'^api/v1/passepartout/', include((passepartout_urls, 'passepartout'), namespace="passepartout")),
        url(r'^api/v1/users/', include((users_urls, 'users'), namespace="user")),
    ]

if settings.DJANGO_SSO_APP_ENABLED:
    from django_sso_app.app.profiles.urls import urlpatterns as profiles_urls
    sso_auth_urlpatterns += [
        url(r'^api/v1/profiles/', include((profiles_urls, 'profiles'), namespace="profile")),
    ]

urlpatterns += sso_auth_urlpatterns

# mine
if settings.DEBUG:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        ] + staticfiles_urlpatterns() + urlpatterns
