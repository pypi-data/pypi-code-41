from psu_base.services import utility_service
from psu_base.classes.IdentityCAS import IdentityCAS
from psu_base.classes.Log import Log
from psu_base.classes.User import User

from functools import wraps
from urllib.parse import urlparse

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import resolve_url
from psu_base.services import auth_service

log = Log()


# ===                                ===
# === AUTHENTICATION & AUTHORIZATION ===
# ===                                ===


def require_authority(authority_code, redirect_url='/'):
    """
    Decorator for views that checks that the user has the required authority.

    authority_code: An authority_code, or a list of authority codes
    redirect_url: Where to send unauthorized user

    Example:
        from psu_base.decorators import require_authority

        # This will redirect unauthorized users to the status test page.
        # If no redirect_url is specified, the root url will be used ("/")
        @require_authority('fake', redirect_url='psu:test')
        def index(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            # If not logged in, redirect to login
            if not request.user.is_authenticated:
                return decorator_sso_redirect(request)

            # If has authority, render the view
            elif auth_service.has_authority(authority_code):
                return view_func(request, *args, **kwargs)

            # Otherwise, send somewhere else
            else:
                # ToDo: Notify the user that they do not have access to this
                return decorator_redirect(request, redirect_url)
        return _wrapped_view
    return decorator


def require_authentication():
    """
    Decorator for views that forces them to log in.

    Example:
        from psu_base.decorators import require_authentication

        @require_authentication()
        def index(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            # If not logged in, redirect to login
            if not request.user.is_authenticated:
                return decorator_sso_redirect(request)

            # Otherwise, render the view
            else:
                return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def require_impersonation_authority(redirect_url='/'):
    """
    Decorator for views that forces them to have access to impersonate someone else.

    Example:
        from psu_base.decorators import require_impersonation_authority

        @require_impersonation_authority()
        def index(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            # If not logged in, redirect to login
            if not request.user.is_authenticated:
                return decorator_sso_redirect(request)

            # If has authority, render the view
            elif auth_service.get_auth_object().can_impersonate():
                return view_func(request, *args, **kwargs)

            # Otherwise, send somewhere else
            else:
                # ToDo: Notify the user that they do not have access to this
                return decorator_redirect(request, redirect_url)
        return _wrapped_view
    return decorator


# ===                 ===
# === FEATURE TOGGLES ===
# ===                 ===

# ...

#
# REMAINING GENERIC CODE IS CALLED FROM THE DECORATORS ABOVE
#


def decorator_redirect(request, redirect_url):
    resolved_login_url = resolve_url(redirect_url)
    path = request.build_absolute_uri()
    from django.contrib.auth.views import redirect_to_login
    return redirect_to_login(
        path, resolved_login_url, None
    )


def decorator_sso_redirect(request):
    resolved_login_url = resolve_url('cas:login')
    path = request.build_absolute_uri()
    login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
    current_scheme, current_netloc = urlparse(path)[:2]
    if ((not login_scheme or login_scheme == current_scheme) and
            (not login_netloc or login_netloc == current_netloc)):
        path = request.get_full_path()
    from django.contrib.auth.views import redirect_to_login
    return redirect_to_login(
        path, resolved_login_url, REDIRECT_FIELD_NAME
    )
