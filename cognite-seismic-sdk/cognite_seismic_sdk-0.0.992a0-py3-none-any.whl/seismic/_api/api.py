import cognite.seismic.protos.types_pb2 as stypes


class API:
    def __init__(self, query, metadata):
        self.query = query
        self.metadata = metadata

    @staticmethod
    def identify(id=None, name=None):
        """
        Returns an identifier with filled with id or name. If both are filled, will prefer id.
        """
        if not id and not name:
            raise Exception("Either `name` or `id` needs to be specified")
        return stypes.Identifier(id=id) if id else stypes.Identifier(name=name)
