

class Component:

    def __init__(self, client):
        self.client = client


class SirenComponent(Component):

    def _get_root(self):
        return self.client.session.get_root_siren()

    @property
    def _root(self):
        raise NotImplementedError
