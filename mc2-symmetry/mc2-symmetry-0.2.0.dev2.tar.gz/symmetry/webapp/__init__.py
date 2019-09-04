import falcon


class ApiResource:
    api: falcon.API

    def __init__(self, api, prefix='/api') -> None:
        super().__init__()
        self.api = api
        self.prefix = prefix

    def on_get(self, req: falcon.Request, resp):
        resp.media = self.get_all_routes(req, self.api)

    def get_all_routes(self, req, api):
        routes_list = []

        def get_children(node):
            if len(node.children):
                for child_node in node.children:
                    get_children(child_node)
            else:
                if node.uri_template.startswith(self.prefix):
                    routes_list.append({
                        'uri': node.uri_template,
                        'type': str(type(node.resource).__name__)
                    })

        [get_children(node) for node in api._router._roots]

        routes_list.sort(key=lambda k: k['uri'])

        return routes_list
