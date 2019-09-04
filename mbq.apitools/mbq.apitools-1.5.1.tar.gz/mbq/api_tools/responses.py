from typing import Optional

from django.db.models import QuerySet
from django.http import JsonResponse

from . import pagination


class BaseResponse(JsonResponse):
    """Base response."""

    def __init__(self, data):
        super().__init__(data, safe=False)


class ListResponse(BaseResponse):
    """List response."""

    status_code = 200

    def __init__(self, objects, meta=None, pagination=None):
        if isinstance(objects, QuerySet):
            objects = list(objects)

        assert not (isinstance(objects, dict) and "objects" in objects)

        self.data = {"objects": objects}
        if meta:
            self.data["meta"] = meta
        if pagination:
            self.data["pagination"] = pagination

        super().__init__(self.data)


class PaginatedResponse(ListResponse):
    """Paginated response."""

    def __init__(self, queryset, serializer, request):
        pagination_params = request.params.pagination

        # Pagination must always exist here
        if not pagination_params:
            raise TypeError(
                f"{PaginatedResponse.__name__} can only be used with a paginated 'view', "
                f"did you mean to use {ListResponse.__name__}?"
            )

        url = request.build_absolute_uri()
        queryset, pagination_data = pagination.paginate_queryset(
            queryset, url, pagination_params
        )

        # If `serializer` is a class, assume it is a DRF serializer.
        if isinstance(serializer, type):
            data = serializer(queryset, many=True).data
        else:
            data = serializer(queryset)

        super().__init__(data, pagination=pagination_data)


class DetailResponse(BaseResponse):
    """Detailed response."""

    status_code = 200

    def __init__(self, object_=""):
        assert not isinstance(object_, list)

        self.data = object_

        super().__init__(object_)


class ErrorResponse(BaseResponse):

    status_code = NotImplemented

    error_code: Optional[str] = None
    detail: Optional[str] = None

    def __init__(
        self, error_code: Optional[str] = None, detail: Optional[str] = None, **kwargs
    ):
        error_code = error_code or self.error_code
        detail = detail or self.detail

        kwargs.update({"error_code": error_code, "detail": detail})
        self.data = kwargs
        super().__init__(self.data)


class ClientErrorResponse(ErrorResponse):
    status_code = 400


class PaginationErrorResponse(ClientErrorResponse):
    error_code = "pagination_error"


class NotFoundResponse(ErrorResponse):
    status_code = 404
    error_code = "not_found"
    detail = "Resource not found"


class UnauthenticatedResponse(ErrorResponse):
    status_code = 401
    error_code = "unauthenticated"
    detail = "Authentication credientials were not provided"


class UnauthorizedResponse(ErrorResponse):
    status_code = 403
    error_code = "unauthorized"
    detail = "Unauthorized to access this resource"


class MethodNotAllowedResponse(ErrorResponse):
    status_code = 405
    error_code = "method_not_allowed"
    detail = "This route does not support that HTTP method"


class UnsupportedMediaTypeResponse(ErrorResponse):
    status_code = 415
    error_code = "unsupported_media_type"
    detail = "This endpoint does not support that content type"


class ServerValidationErrorResponse(ErrorResponse):
    status_code = 422


class TooManyRequestsResponse(ErrorResponse):
    status_code = 429
    error_code = "too_many_requests"


class ServerErrorResponse(ErrorResponse):
    status_code = 500
    error_code = "server_error"
    detail = "An unexpected error occurred"
