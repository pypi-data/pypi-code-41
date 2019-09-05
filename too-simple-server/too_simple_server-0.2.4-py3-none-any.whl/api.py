from flask import Flask
from flask_restful import Api, Resource, reqparse

from .database import create_entity, get_all_enities, get_entity_data

SERVER = Flask("API")
API = Api(SERVER)


@SERVER.route("/")
def is_up():
    return "OK"


class MockEntity(Resource):
    """Mock for resource"""

    def __init__(self):
        self._body_parser = reqparse.RequestParser()
        self._body_parser.add_argument("data")

    def get(self, uuid):
        """Return some entity"""
        return get_entity_data(uuid)

    def post(self):
        """Create new entity"""
        data = self._body_parser.parse_args()
        if not hasattr(data, "data"):
            return "Data is missing", 400
        new_id = create_entity(data)
        return {}, 201, {"Location": f"/entity/{new_id}"}


API.add_resource(MockEntity, "/entity/<uuid:uuid>", "/entity")


class MockEntityList(Resource):
    """List of mock entities"""

    def get(self):
        """Get list of all entities"""
        return get_all_enities()


API.add_resource(MockEntityList, "/entities")
