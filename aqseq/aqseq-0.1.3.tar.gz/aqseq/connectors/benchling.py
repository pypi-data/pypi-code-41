import jdna
from aqseq.connectors.abc import Connector, Registry
from benchlingapi.exceptions import InvalidRegistryId, RegistryValidationError


class BenchlingConnector(Connector):
    def __init__(self, api, folder_id=None):
        self.api = api
        self.folder_id = folder_id
        if self.folder_id is not None:
            self.folder = self.api.Folder.find(folder_id)
            if self.folder is None:
                raise Exception("Folder id='{}' not found on server.".format(folder_id))
        else:
            self.folder = None

    def to_api(self, sequence):
        return self.api.DNASequence(**sequence.json())

    def from_api(self, api_seq):
        seq = jdna.Sequence.load(api_seq.dump())
        seq.metadata["webLink"] = api_seq.webURL
        return seq

    def push(self, sequence, folder_id=None):
        if folder_id is None:
            folder_id = self.folder_id
        api_seq = self.to_api(sequence)
        api_seq.folderId = folder_id
        api_seq.save()
        return api_seq

    def fetch(self, weblink):
        if weblink.strip() == "":
            raise ValueError("Cannot open blank weblink")
        return self.api.DNASequence.from_share_link(weblink)


class BenchlingRegistry(Registry, BenchlingConnector):
    def __init__(self, api, folder_id, registry_id, prefix, initials, schema):
        super().__init__(api, folder_id)
        self.prefix = prefix
        self.initials = initials
        self.schema = schema
        self.registry_id = registry_id
        self.registry = self.api.Registry.find(registry_id)

    def _format_uid(self, uid):
        try:
            uid = int(uid)
        except TypeError:
            raise TypeError("Unique id must be an integer not a '{}'".format(type(uid)))
        return "{prefix}{init}{uid}".format(
            prefix=self.prefix, uid=int(uid), init=self.initials
        )

    def find(self, uid):
        api_seq = self.api.DNASequence.find_in_registry(self._format_uid(uid))
        return api_seq

    def register(self, seq, uid, overwrite=True):
        seq.folderId = self.folder_id
        entity_registry_id = self._format_uid(uid)
        print("Attempting registration for id='{}'".format(entity_registry_id))
        if not hasattr(seq, "id") or seq.id is None:
            seq.save()
        try:
            seq.set_schema(self.schema)
            seq.register_with_custom_id(entity_registry_id)
            print("Registration successful.")
        except (InvalidRegistryId, RegistryValidationError) as e:
            if not overwrite:
                raise e
            print(
                "Updating existing registered sequence id='{}'".format(
                    entity_registry_id
                )
            )
            existing = self.api.DNASequence.find_in_registry(entity_registry_id)
            return self.api.DNASequence.update_model(existing.id, seq.update_json())

        print(seq.entityRegistryId)
        return seq
