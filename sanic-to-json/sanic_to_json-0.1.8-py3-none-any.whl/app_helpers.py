from sanic_to_json.schema_helpers import atomic_request
from sanic_to_json.INI_helpers import extract_ini_from_doc, add_INI_data, load_config


def get_all_routes(app):
    """Returns all routes from Sanic app, excludes duplicates."""
    all_routes = app.router.routes_all
    routes = {}
    for route in all_routes:
        if route[-1] != "/":
            routes[route] = all_routes[route]
    return routes


def get_route_name(route):
    """Returns route name."""
    # split once, take last peice
    name = route.split("/", 1)[-1]
    return name


def get_app_route_methods(routes, route):
    """Return route CRUD method (GET, POST, etc)."""
    methods = list(routes[route].methods)
    return methods


def get_route_doc_string(routes, route, method):
    """Returns doc string for embedded route functions."""
    try:
        doc = routes[route][0].handlers[method].__doc__
    except AttributeError:
        doc = routes[route][0].__doc__
    return doc


def get_url(route, base_url="{{base_Url}}"):
    """Adds base_url environment variable to url prefix."""
    url = base_url + route
    return url


def format_request(routes, route, method, base_url="{{base_Url}}"):
    """Populates atomic_request dictionary with route metatdata.

    Returns a postman formatted dictionary request item."""
    request = atomic_request()
    doc = get_route_doc_string(routes, route, method)
    name = get_route_name(route)
    url = get_url(route, base_url=base_url)
    request["name"] = name
    request["request"]["method"] = method
    request["request"]["url"]["raw"] = url
    request["request"]["url"]["host"] = [url]
    request["request"]["description"] = doc
    # check doc strings for INI add extra keys
    if "INI" in doc:
        config_string = extract_ini_from_doc(doc)
        config = load_config(config_string)
        request = add_INI_data(doc, request, config)
    return request
