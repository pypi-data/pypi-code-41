from sanic_to_json.app_helpers import get_app_route_methods, format_request


def get_blueprints(app):
    """Returns blueprints dict."""
    return app.blueprints


def get_blueprint_routes(blueprint, routes):
    """Return routes related to a given blueprint."""
    blueprint_routes = {}
    for route in routes:
        bp_name = routes[route].name.split(".")[0]
        # match route to blueprint
        if blueprint == bp_name:
            blueprint_routes[route] = routes[route]
    return blueprint_routes


def get_blueprint_docs(blueprints, blueprint):
    """Returns doc string for blueprint."""
    doc_string = blueprints[blueprint].__doc__
    return doc_string


def populate_blueprint(
    api_json, blueprints, blueprint, routes, base_url="{{base_Url}}"
):
    """Populates endpoints for blueprint."""

    items = []
    for route in get_blueprint_routes(blueprint, routes):
        for method in get_app_route_methods(routes, route):
            items.append(format_request(routes, route, method, base_url=base_url))
    api_json["item"].append(
        {
            "name": blueprint,
            "description": get_blueprint_docs(blueprints, blueprint),
            "item": items,
        }
    )
    return api_json


def add_non_blueprint_requests(
    api_json, routes, base_url="{{base_Url}}", divider="JSON BODY\n    --------"
):
    """Add requests not added in populate_blueprints."""
    for route in routes:
        if "." not in routes[route].name:
            for method in get_app_route_methods(routes, route):
                request = format_request(routes, route, method, base_url=base_url)
                api_json["item"].append(request)
    return api_json
