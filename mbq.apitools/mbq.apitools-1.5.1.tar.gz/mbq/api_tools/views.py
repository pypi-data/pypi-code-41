import json
import logging
from functools import wraps
from typing import Any, Dict, List, Optional, Tuple, Union

from django.views.decorators.csrf import csrf_exempt

from typing_extensions import Literal

from . import exceptions, fields, settings
from .responses import (
    ClientErrorResponse,
    ListResponse,
    MethodNotAllowedResponse,
    PaginatedResponse,
    UnauthorizedResponse,
    UnsupportedMediaTypeResponse,
)
from .schema import Pagination, ParamSchema, PayloadSchema, generate_schema
from .utils import first


logger = logging.getLogger(__name__)
PermissionsCollection = Union[List[Any], Tuple[Any, ...]]
HttpMethodNames = Literal["GET", "POST", "PATCH", "PUT", "DELETE"]
OnUnknownField = Literal["raise", "exclude"]


class ViewDecorator:
    def __init__(
        self,
        http_method_name: HttpMethodNames = "GET",
        permissions: PermissionsCollection = (),
        params: Optional[Dict[str, fields.Field]] = None,
        payload: Optional[Dict[str, fields.Field]] = None,
        paginated: bool = False,
        page_size: Optional[int] = None,
        on_unknown_field: Optional[OnUnknownField] = None,
        verbose_logging: bool = False,
        _method: Optional[bool] = None,
    ):
        if not permissions:
            raise TypeError("Permissions are required")

        if http_method_name in {"POST", "PATCH", "PUT"} and payload is None:
            raise TypeError(
                "A payload must be specified for POST, PATCH, and PUT endpoints (it can be empty)."
            )
        if http_method_name == "GET" and payload is not None:
            raise TypeError("Payloads cannot be specified for GET endpoints")

        self.http_method_name = http_method_name
        self.permissions = permissions
        self.params = params
        self.payload = payload
        self.on_unknown_field = on_unknown_field

        self.paginated = paginated
        self.page_size = page_size
        self.verbose_logging = verbose_logging

        if self.page_size and not self.paginated:
            raise ValueError(
                f"Defining 'page_size={self.page_size}' requires also setting 'paginated=True'."
            )

        self._method = _method

    def __call__(self, func):
        func.http_method_name = self.http_method_name
        func.permissions = self.permissions
        func.params = self.params
        func.payload = self.payload
        func.paginated = self.paginated
        func.page_size = self.page_size
        func.on_unknown_field = self.on_unknown_field
        func.verbose_logging = self.verbose_logging

        if self._method:
            return func

        @wraps(func)
        def wrapped_func(request, *args, **kwargs):
            if request.method.upper() != self.http_method_name:
                return MethodNotAllowedResponse()

            return ViewFunction(func, request)(*args, **kwargs)

        return csrf_exempt(wrapped_func)

    @classmethod
    def method(cls, *args, **kwargs):
        kwargs["_method"] = True
        return cls(*args, **kwargs)


view = ViewDecorator


class View:
    @classmethod
    def as_view(cls):
        view_function_names = [
            attr for attr in dir(cls) if hasattr(getattr(cls, attr), "http_method_name")
        ]

        if not view_function_names:
            raise TypeError(
                "View classes must have at least one method decorated with `view.method`"
            )

        @wraps(cls)
        def dispatcher(request, *args, **kwargs):
            view = cls()
            http_method = request.method.upper()

            view_functions = [
                getattr(view, func_name) for func_name in view_function_names
            ]

            view_method = first(
                view_functions, lambda x: http_method == x.http_method_name
            )

            if view_method is None:
                return MethodNotAllowedResponse()

            return ViewFunction(view_method, request, view_class=cls)(*args, **kwargs)

        return csrf_exempt(dispatcher)


class ViewFunction:
    def __init__(self, view_func, request, view_class=None):
        self.view_func = view_func
        self.request = request
        self.view_class = view_class

        self.permissions = view_func.permissions
        self.params = view_func.params or {}
        self.payload = view_func.payload or {}
        self.paginated = view_func.paginated
        self.page_size = view_func.page_size
        self.on_unknown_field = view_func.on_unknown_field
        self.verbose_logging = view_func.verbose_logging

        # Add the pagination fields to the params
        if self.paginated:
            self.params.setdefault(
                "page", fields.Int(default=Pagination.DEFAULT_PAGE, min_val=0)
            )  # Always page 1
            self.params.setdefault(
                "page_size",
                fields.Int(
                    default=self.page_size or Pagination.DEFAULT_PAGE_SIZE, min_val=1
                ),
            )

    def get_view_name(self):
        func_name = self.view_func.__name__

        if self.view_class:
            return f"{self.view_class.__name__}.{func_name}"
        else:
            return func_name

    def get_param_schema(self):
        schema_class = (
            generate_schema(ParamSchema, self.params) if self.params else ParamSchema
        )
        return schema_class(
            unknown=self.on_unknown_field
            or settings.project_settings.UNKNOWN_PARAM_FIELDS
        )

    def get_payload_schema(self):
        schema_class = (
            generate_schema(PayloadSchema, self.payload)
            if self.payload
            else PayloadSchema
        )
        return schema_class(
            unknown=self.on_unknown_field
            or settings.project_settings.UNKNOWN_PAYLOAD_FIELDS
        )

    def __call__(self, *args, **kwargs):
        # Backwards compat thing for DRF permissions
        self.args = args
        self.kwargs = kwargs
        logging_level = logging.INFO if self.verbose_logging else logging.DEBUG

        try:
            self._enrich_request()

            authorization_error = self._perform_authorization()
            if authorization_error:
                return UnauthorizedResponse()

            response = self.view_func(self.request, *args, **kwargs)
            self._check_response(response)

            return response

        except exceptions.ValidationError as e:
            logger.log(logging_level, f"ValidationError: {str(e)}")
            return ClientErrorResponse("validation_error", str(e))
        except exceptions.ImmediateResponseError as e:
            logger.log(logging_level, f"ImmediateResponseError: {str(e)}")
            return e.response

    def _enrich_request(self):
        try:
            payload = (
                json.loads(self.request.body.decode("utf-8"))
                if self.request.body
                else {}
            )
        except json.JSONDecodeError:
            raise exceptions.ImmediateResponseError(UnsupportedMediaTypeResponse())

        self.request.payload = self.get_payload_schema().load(payload)
        self.request.params = self.get_param_schema().load(self.request.GET)

    def _perform_authorization(self) -> Optional[str]:
        """Returns None if authorization succeeds, or an error message if it fails."""
        for permission in self.permissions:
            # If it is a class, assume it is a DRF permission class.
            if isinstance(permission, type):
                if permission().has_permission(self.request, self) is not True:
                    # Protecting against mocks with these type checks
                    message = getattr(permission, "message", None)
                    return (
                        message if isinstance(message, str) else "Authorization Failed"
                    )
            else:
                if permission(self.request) is not True:
                    return "Authorization Failed"

        return None

    def _check_response(self, response):
        """Checks if the response is valid.
        :raises TypeError: If the response type is incorrect
        """
        if (
            response.status_code == 200
            and self.paginated
            and not isinstance(response, PaginatedResponse)
        ):
            raise TypeError(
                f"Invalid pagination, make sure to either set a {PaginatedResponse.__name__} with "
                f"'paginated=True' in the 'view' decorator, or use a {ListResponse.__name__}."
            )
