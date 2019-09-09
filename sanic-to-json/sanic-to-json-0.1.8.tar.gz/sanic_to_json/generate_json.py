from json import dump
from sanic_to_json.schema_helpers import basic_JSON
from sanic_to_json.app_helpers import get_all_routes
from sanic_to_json.blueprint_helpers import (
    get_blueprints,
    populate_blueprint,
    add_non_blueprint_requests,
)


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

