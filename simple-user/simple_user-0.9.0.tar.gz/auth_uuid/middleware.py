from django.contrib.auth.middleware import AuthenticationMiddleware as DjangoAuthMiddleware
from django.contrib.auth import get_user_model


class AuthenticationMiddleware(DjangoAuthMiddleware):
    def process_request(self, request):
        request.user = get_user_model(
            ).objects.retrieve_remote_user_by_cookie(
                request.COOKIES)
