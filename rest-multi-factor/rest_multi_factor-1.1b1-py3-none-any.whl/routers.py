"""Custom routers, these are not really necessary, but look allot cleaner."""

__all__ = (
    "MultiFactorRegisterRouter",
    "MultiFactorVerifierRouter",
)

from rest_framework.routers import SimpleRouter, DynamicRoute, Route


class MultiFactorVerifierRouter(SimpleRouter):
    """
    Custom router for the MultiFactorViewSet.

    This router isn't really necessary such as the documentation
    already stated:

    'Implementing a custom router isn't something you'd need to
    do very often ...'

    But it looks much cleaner and is use full for subclassing the view.

    see:
    https://www.django-rest-framework.org/api-guide/routers/#custom-routers
    """

    routes = [
        # General routes
        Route(
            url=r"^{prefix}{trailing_slash}$",
            mapping={
                "get": "overview",
            },
            name="{basename}-overview",
            detail=False,
            initkwargs={"suffix": "List"}
        ),

        Route(
            url=r"^{prefix}/{lookup}{trailing_slash}$",
            mapping={
                "get": "retrieve",
                "post": "verify",
            },
            name="{basename}-specific",
            detail=True,
            initkwargs={"suffix": "Instance"}
        ),

        Route(
            url=r"^{prefix}/{lookup}/dispatch{trailing_slash}$",
            mapping={
                "post": "dispatch_challenge",
            },
            name="{basename}-dispatch",
            detail=True,
            initkwargs={"suffix": "Instance"}
        ),

        # Dynamically generated detail routes. Generated using
        # @action(detail=True) decorator on methods of the viewset.
        DynamicRoute(
            url=r"^{prefix}/{lookup}/{url_path}{trailing_slash}$",
            name="{basename}-{url_name}",
            detail=True,
            initkwargs={}
        ),
    ]


class MultiFactorRegisterRouter(SimpleRouter):
    """Custom router for the MultiFactorRegisterViewSet."""

    routes = [
        # General routes
        Route(
            url=r"^{prefix}{trailing_slash}$",
            mapping={
                "get": "overview",
            },
            name="{basename}-overview",
            detail=False,
            initkwargs={"suffix": "List"}
        ),

        Route(
            url=r"^{prefix}/{lookup}{trailing_slash}$",
            mapping={
                "get":  "specific",
                "post": "register",
            },
            name="{basename}",
            detail=True,
            initkwargs={"suffix": "Instance"}
        ),
    ]
