from json import dump, dumps
import configparser


def collection_json():
    """Returns JSON skeleton for Postman schema."""
    collection_json = {
        "info": {
            "name": "Test_collection",
            "description": "Generic text used for documentation.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [],
    }
    return collection_json


def atomic_request():
    """Returns an atomic Postman request dictionary."""

    request = {
        "name": "test request",
        "request": {
            "method": "GET",
            "header": [],
            "url": {
                "raw": "{{target_url}}endpoint",
                "host": ["{{target_url}}endpoint"],
            },
            "description": "This description can come from docs strings",
        },
        "response": [],
    }
    return request


def basic_JSON(collection_name, app, api_json=collection_json()):
    """Formats the Postman collection with 'collection_name' and doc string from Sanic app.

    Returns JSON dictionary."""
    api_json["info"]["name"] = collection_name
    api_json["info"]["description"] = app.__doc__
    return api_json


def get_all_routes(app):
    """Returns all routes from Sanic app, excludes duplicates."""
    all_routes = app.router.routes_all
    routes = {}
    for route in all_routes:
        if route[-1] != "/":
            routes[route] = all_routes[route]
    return routes


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


def get_route_name(route):
    """Returns route name."""
    name = route.split("/")[-1]
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


def extract_ini_from_doc(doc):
    """Extracts INI from doc strings."""
    return doc.rsplit("INI")[-1]


def load_config(ini_string):
    """Load config parse from string."""
    # Override lower case key conversion
    config = configparser.RawConfigParser()
    config.optionxform = lambda option: option
    config.read_string(ini_string)
    return config


def format_headers(config_section):
    """Returns a list of formatted header dictionaries."""
    request_header = []
    try:
        header_items = eval(config_section["header"])
        for key in header_items:
            header = {
                "key": key,
                "name": key,
                "value": header_items[key],
                "type": "text",
            }
            request_header.append(header)
    except KeyError:
        pass
    return request_header


def format_json_body(config_section):
    """formats JSON body from config as raw JSON."""
    body = {}
    body["mode"] = "raw"
    body["raw"] = {}
    try:
        body_dict = eval(config_section["body"])
        for key in body_dict:
            body["raw"][key] = body_dict[key]
        body["raw"] = dumps(body["raw"])
    except KeyError:
        pass
    return body


def add_INI_data(doc, request, config):
    """adds INI elements to atomic request. Returns altered request."""
    body = format_json_body(config["request"])
    request["request"]["body"] = body

    head = format_headers(config["request"])
    request["request"]["header"] = head

    request["protocolProfileBehavior"] = {"disableBodyPruning": True}
    return request


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
        request["response"] = add_responses(request, config)
    return request


def add_responses(request, config):
    """Response is a list of dictionary requests."""
    response = []
    for section in config.sections():
        example_request = {}
        example_request["originalRequest"] = {}
        if "example" in section:
            example_request["name"] = config[section]["name"]
            example_request["originalRequest"]["method"] = config[section]["method"]
            example_request["originalRequest"]["header"] = format_headers(
                config[section]
            )
            example_request["originalRequest"]["body"] = format_json_body(
                config[section]
            )
            example_request["originalRequest"]["url"] = request["request"]["url"].copy()
            example_request["originalRequest"]["url"]["raw"] += config[section]["query"]
            example_request["originalRequest"]["url"]["host"] = [
                example_request["originalRequest"]["url"]["raw"]
            ]

            response.append(example_request)
    return response


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


def save_as_json(collection_name, filename="postman_collection.json"):
    """Write dict to JSON file."""

    with open(filename, "w") as file:
        dump(collection_name, file, indent=4)


def generate_sanic_json(collection_name, app, filename="postman_collection.json"):
    """Generates json script from Sanic docs.

    Parameters
    ----------
    collection_name: str
        title of collection
    app: Sanic class
        Sanic app
    filename: str (optional)
        location of output file
    """
    # build basic json schema
    collection = basic_JSON(collection_name, app)

    # get routes and blueprints
    routes = get_all_routes(app)
    blueprints = get_blueprints(app)

    # populate blueprint requests
    for blueprint in blueprints:
        collection = populate_blueprint(collection, blueprints, blueprint, routes)

    # populate main app requests
    collection = add_non_blueprint_requests(collection, routes)

    # save dict to JSON file
    save_as_json(collection, filename=filename)

