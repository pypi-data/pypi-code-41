"""
Django middleware to add extra metadata on the user object attached to response.
NB: must run after your authentication has run
"""
from .models import KV
from .user import GlobalUser

def user_meta_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = get_response(request)
        logged_in_user = getattr(request, 'user')
        if logged_in_user is not None:
            request.user = GlobalUser(logged_in_user.id).as_django_user
        return response

    return middleware
