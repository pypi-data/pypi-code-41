from graphqlclient import GraphQLClient
import os
import logging as log
from jinja2 import Template
import json
from functools import partial
from DatastoreClient.utils import get_filename


class GraphQLQueryer:
    def __init__(self, client=None):
        if not client:
            entrance = os.environ.get("entrance", "127.0.0.1")
            self.client = GraphQLClient(
                "http://{host}/datastore/graphql".format(host=entrance)
            )
        else:
            self.client = client

    def query(self, query_template_string, **kwargs):
        query_string = Template(query_template_string).render(**kwargs)
        log.debug(query_string)
        result = self.client.execute(query_string)
        result = json.loads(result)
        err = False
        if "errors" in result:
            err = result["errors"]
            result = None
            log.debug(err, query_string)
        return err, result

    def generate_query_funcs(self, from_dir=""):
        if not os.path.isdir(from_dir):
            log.error({"Exception": "from_dir must be a dir"})
        for file in os.listdir(from_dir):
            filepath = os.path.join(from_dir, file)
            filename = get_filename(filepath)
            with open(filepath, "r") as f:
                graphql = f.read()
                func_name = filename.split(".")[0]
                setattr(self, func_name, partial(self.query, graphql))


if __name__ == "__main__":
    pass
