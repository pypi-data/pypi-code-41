from django.utils.deprecation import MiddlewareMixin
from django.contrib import auth
from django.contrib.auth.models import AnonymousUser


class AuthenticationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        user = auth.authenticate(request)
        if user:
            request.user = user
            if user.is_anonymous:
                auth.login(request, user)
        else:
            request.user = AnonymousUser()
