"""
Provider for GitHub's v4 GraphQL API.
"""
import itertools
import urllib.request

import graphql

from gqlmod.helpers.urllib import UrllibJsonProvider
from gqlmod.helpers.utils import walk_query, walk_variables, unwrap_type


def find_directive(ast_node, name):
    if ast_node is None:
        return
    for d in ast_node.directives:
        if d.name.value == name:
            break
    else:
        return

    return {
        arg.name.value: graphql.value_from_ast_untyped(arg.value)
        for arg in d.arguments
    }


class GitHubProvider(UrllibJsonProvider):
    endpoint = 'https://api.github.com/graphql'

    def __init__(self, token=None):
        self.token = token

    def build_request(self, query, variables):
        req = super().build_request(query, variables)
        if '__previews' in variables:
            req.add_header('Accept', ', '.join(
                f"application/vnd.github.{p}+json"
                for p in variables['__previews']
            ))
        return req

    def modify_request(self, req, variables):
        if self.token:
            req.add_header('Authorization', f"Bearer {self.token}")

    def get_schema_str(self):
        with urllib.request.urlopen("https://developer.github.com/v4/public_schema/schema.public.graphql") as fobj:
            return fobj.read().decode('utf-8')

    def codegen_extra_kwargs(self, gast, schema):
        previews = set()
        # Find all the @preview directives and pull out their names
        for field in itertools.chain(
            (f for _, _, f in walk_query(gast, schema)),
            (f for _, f in walk_variables(gast, schema)),
        ):
            d = find_directive(field.ast_node, 'preview')
            if d and 'toggledBy' in d:
                previews.add(d['toggledBy'])

            typ, *_ = unwrap_type(field.type)
            d = find_directive(typ.ast_node, 'preview')
            if d and 'toggledBy' in d:
                previews.add(d['toggledBy'])
        return {
            '__previews': previews,
        }
