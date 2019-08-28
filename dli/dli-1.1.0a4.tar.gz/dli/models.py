import contextlib

from collections.abc import Mapping


class AttributesDict(Mapping):

    def __init__(self, *args, **kwargs):
        # recurisvely provide the rather silly attribute
        # access
        data = {}

        for arg in args:
            data.update(arg)

        data.update(**kwargs)

        for key, value in data.items():
            if isinstance(value, Mapping):
                self.__dict__[key] = AttributesDict(value)
            else:
                self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def _asdict(self, *args, **kwargs):
        return self

    def __repr__(self):
        attributes = ' '.join([
            '{}={}'.format(k, v) for k,v in self.__dict__.items()
        ])

        return "{}({})".format(self.__class__.__name__, attributes)


class SampleData:
    def __init__(self, parent):
        self._parent = parent
        self._client = parent._client.client
        self._urls = parent._client.urls

    def schema(self):
        """
        Returns the schema data and first rows of sample data.

        :returns: attributes dictionary
        """
        response = self._client.session.get(
            self._urls.v2_sample_data_schema.format(id=self._parent.id)
        )

        return AttributesDict(**response.json()['data']['attributes'])

    @contextlib.contextmanager
    def file(self):
        """
        Provides a file like object containing sample data.

        Example usage:

        .. code-block:: python

            dataset = self.client.get_dataset(dataset_id)
            with dataset.sample_data.file() as f:
                dataframe = pandas.read_csv(f)
        
        """
        response = self._client.session.get(
            self._urls.v2_sample_data_file.format(id=self._parent.id),
            stream=True
        )
        yield response.raw
        response.close()


class DatasetModel(AttributesDict):

    @property
    def sample_data(self):
        return SampleData(self)

    @property
    def id(self):
        return self.dataset_id

    def __init__(self, json, client=None):
        self._client = client

        location = json['attributes'].pop('location')

        if 's3' in location:
            location = location['s3']
        else:
            location = location['other']

        super().__init__(
            json['attributes'],
            dataset_id=json['id'],
            location=location
        )


class SchemaModel(AttributesDict):

    @property
    def id(self):
        return self.dictionary_id

    @property
    def schema_id(self):
        return self.id

    def __init__(self, json):
        super().__init__(
            json['attributes'],
            dictionary_id=json['id'],
        )
