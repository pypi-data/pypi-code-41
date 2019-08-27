import json
import warnings

from requests_toolbelt.multipart.encoder import MultipartEncoder
from dli.client.builders import DatasetBuilder
from dli.client.components import SirenComponent
from dli.client.utils import ensure_count_is_valid
from dli.models import DatasetModel, SchemaModel
from dli.siren import siren_to_entity


class Dataset(SirenComponent):

    class urls:
        instance = '/__api/datasets/{id}/'
        index = '/__api/datasets/'
        datafiles = '/__api/datasets/{id}/datafiles/'
        latest_datafile = '/__api/datasets/{id}/latest-datafile/'
        keys = '/__api/datasets/{id}/keys/'
        access_keys = '/__api/request-access-keys/'

        # dli_v2
        v2_index = '/__api_v2/datasets/'
        v2_instance = '/__api_v2/datasets/{id}/'
        v2_sample_data_schema = '/__api_v2/datasets/{id}/sample_data'
        v2_sample_data_file = '/__api_v2/datasets/{id}/sample_data/static_file'

    def get_s3_access_keys_for_dataset(self, *dataset_ids):
        """
        Retrieve S3 access keys for the specified account to access the
        specified dataset(s).

        :param list dataset_ids: One ore more dataset ids to get access to.
        :returns: A namedtuple containing the AWS keys and session token.
        - **Sample**

        .. code-block:: python

                s3_access_keys = client.get_s3_access_keys_for_dataset(dataset_id1, dataset_id2)
                # print(s3_access_keys)
                # access_key(access_key_id='39D19A440AFE452B9', secret_access_key='F426A93CDECE45C9BFF8F4F19DA5CB81', session_token='C0CC405803F244CA99999')

        """
        payload = {"datasetIds": list(dataset_ids)}

        response = self.client.session.post(
            self.urls.access_keys, json=payload
        )

        return siren_to_entity(response.to_siren())

    def get_dataset(self, id=None, name=None, package_id=None, package_name=None):
        """
        Retrieves a dataset.

        :param str id: The id of the dataset.
        :param str name: The name of the dataset.
        :param str package_id: The id of the package to which this dataset belongs.
                            Either this or package name is required if dataset is being looked up by name.
        :param str package_name: The name of the package to which this dataset belongs.
                            Either this or package id is required if dataset is being looked up by name.

        :returns: The dataset.

        - **Sample**

        .. code-block:: python

                # Look up by dataset id
                dataset = client.get_dataset('my_dataset_id')
                # or equivalent
                dataset = client.get_dataset(id='my_dataset_id')

                # Look up by dataset name

                # If package id is known
                dataset = client.get_dataset(name='my_dataset', package_id='my_package_id')

                # if package name is known
                dataset = client.get_dataset(name='my_dataset', package_name='my_package')
        """
        if name and (package_name or package_id):
            warnings.warn(
                'Getting a dataset by name, and package name or package ID'
                'will be deprecated in future. Slugs will replace this.',
                PendingDeprecationWarning
            )

            id = self._get_dataset_id_by_name(
                name=name,
                package_id=package_id,
                package_name=package_name
            )

        response = self.client.session.get(
            self.urls.v2_instance.format(id=id)
        )

        return DatasetModel(response.json()['data'], client=self.client)

    def _get_dataset_id_by_name(self, **kwargs):
        response = self.client.session.get(self.urls.index, params=kwargs)
        # Getting dataset by name and id needs to implemented in new API
        dataset_v1 = response.to_siren()
        return dataset_v1.datasetId

    def register_dataset(self, builder : DatasetBuilder):
        """
        Submit a request to create a new dataset under a specified package in the Data Catalogue.

        :param dli.client.builders.DatasetBuilder builder: An instance of DatasetBuilder. This builder object sets sensible defaults and exposes
                                                           helper methods on how to configure its storage options.

        :returns: A newly created Dataset.

        - **Sample**

        .. code-block:: python

                # Please refer to builder docs for examples on
                # how to create an instance of DatasetBuilder.

                dataset = client.register_dataset(builder)
        """
        fields={
            'data': ('data', json.dumps(builder.to_json_api()), 'application/json'),
        }

        if 'sample_data' in builder._data:
            fields['sample_data'] = (
                builder._data['sample_data'].name,
                builder._data['sample_data'],
                # Mimetyppe is ignored
                'text/plain'
            )

        mp_encoder = MultipartEncoder(fields=fields)
        result = self.client.session.post(
            self.urls.v2_index, data=mp_encoder,
            headers={'Content-Type': mp_encoder.content_type}
        )
        return DatasetModel(result.json()['data'], client=self)

    def edit_dataset(
        self,
        dataset_id,
        location_builder=None,
        **kwargs
    ):
        """
        Updates information on a dataset, returning the updated instance.
        If keyword argument is not specified field keeps its old value.
        Optional enum and text type fields can be unset by passing ``None``.

        :param str dataset_id: Id of the dataset being updated.
        :param dli.client.builders.DatasetLocationBuilder location_builder: Optional. An instance of DatasetLocationBuilder. This builder object exposes
                                                                            helper methods to configure dataset storage options.

        Keyword arguments:

        :keyword str name: Optional. A descriptive name of a dataset. It should be unique within the package.
        :keyword str description: Optional. A short description of a package.
        :keyword str content_type: Optional. A way for the data steward to classify the type of data in the dataset
                                (e.g. pricing).
        :keyword str data_format: Optional. The format of the data: `CSV`, `IMAGE`, `JSON`, `PARQUET`, `TXT`, `XML`, `Other`.
        :keyword str publishing_frequency: Optional. The internal on which data is published. Possible values are: `Hourly`,
                                        `Daily`, `Weekday`, `Weekly`, `Monthly`, `Quarterly`, `Yearly`, `Not Specified`.
        :keyword list[str] keywords: Optional. User-defined list of keywords that can be used to find this dataset through
                                    the search interface.
        :keyword str naming_convention: Optional. Key for how to read the dataset name.
        :keyword str documentation: Optional. Documentation about this dataset in markdown format.
        :keyword list[str] taxonomy: Optional. A list of segments to be used for a taxonomy,
                                    the Data-<< Organization >>-<< topic >> prefix will be applied by the catalogue  For
                                    a taxonomy of Data-IHS Markit-Financial Markets-Credit-CDS, you would provide
                                    `taxonomy=["Credit", "CDS"]`
        :keyword str load_type: Optional. Whether each datafile in this dataset should be considered as a full version
                                of a dataset or a delta or increment. Accepted types are `Full Load`, `Incremental Load`

        :returns: Updated Dataset.

        - **Sample**

        .. code-block:: python

                # e.g. update dataset description
                updated_dataset = client.edit_dataset(
                    "my-dataset-id",
                    description="Updated my dataset description"
                )

                # update dataset location. Please note that this is only allowed if the dataset has no datafiles registered.
                builder = DatasetLocationBuilder().with_external_storage("external-storage-location")
                updated_dataset = client.edit_dataset(
                    "my-dataset-id",
                    location_builder=builder
                )

                # update dataset taxonomy
                updated_dataset = client.edit_dataset(
                    "my-dataset-id",
                    taxonomy=["Credit", "CDS"]
                )

        """
        payload = dict(kwargs)

        if location_builder:
            payload.update(**location_builder._dliv2())

        payload = {
            'data': {
                'attributes': payload
            }
        }

        response = self.client.session.patch(
            self.urls.v2_instance.format(id=dataset_id), json=payload
        )

        return DatasetModel(response.json()['data'], client=self)

    def delete_dataset(self, dataset_id):
        """
        Marks a particular dataset (and all its datafiles) as deleted.
        This dataset will no longer be accessible by consumers.

        :param str dataset_id: The id of the dataset to be deleted.

        :returns: None

        - **Sample**

        .. code-block:: python

                client.delete_dataset(dataset_id)

        """
        self.client.session.delete(
            self.urls.v2_instance.format(id=dataset_id)
        )

    def get_datafiles(self, dataset_id, name_contains=None, as_of_date_start=None, as_of_date_end=None, count=100):
        """
        Returns a list of all datafiles registered under a dataset.

        :param str dataset_id: The id of the dataset.
        :param str name_contains: Optional. Look up only those datafiles for the dataset where name contains this string.
        :param str as_of_date_start: Optional. Datafiles having data_as_of date greater than or equal to this date. This must be specified in YYYY-MM-DD format.
        :param str as_of_date_end: Optional. Datafiles having data_as_of date less than or equal to this date. This must be specified in YYYY-MM-DD format.
        :param int count: Optional count of datafiles to be returned. Defaults to 100.

        :returns: List of all datafiles registered under the dataset.

        - **Sample**

        .. code-block:: python

                datafiles = client.get_datafiles(
                    dataset_id,
                    name_contains='My Test Data',
                    as_of_date_start='2018-10-11',
                    as_of_date_end='2018-10-15',
                    count=10
                )
        """
        ensure_count_is_valid(count)

        params = {
            'name': name_contains,
            'as_of_date_start': as_of_date_start,
            'as_of_date_end': as_of_date_end,
            'page_size': count
        }

        return self.client.session.get(
            self.urls.datafiles.format(id=dataset_id), params=params
        ).to_many_siren('datafile')

    def get_latest_datafile(self, dataset_id):
        """
        Fetches datafile metadata of latest datafile in the dataset.

        :param str dataset_id: The id of the dataset.

        :returns: The datafile.

        - **Sample**

        .. code-block:: python

                datafile = client.get_latest_datafile(dataset_id)
        """
        datafile = self.client.session.get(
            self.urls.latest_datafile.format(id=dataset_id)
        ).to_siren()

        return siren_to_entity(datafile)


class Dictionary(SirenComponent):

    class urls:
        schemas_many = '/__api/datasets/{id}/schemas/'
        schema_instance = '/__api/datasets/{id}/schema/'
        schema_instance_version = '/__api/datasets/{id}/schema/{version}'

        # V2 API
        dictionary_index =  '/__api_v2/dictionaries/'
        dictionary_instance = '/__api_v2/dictionaries/{id}/'
        dictionary_by_dataset = '/__api_v2/datasets/{id}/dictionaries/'
        dictionary_by_dataset_lastest = '/__api_v2/datasets/{id}/current_dictionary/'

    def _register_schema(self, dataset_id, payload):
        response = self.client.session.post(
            self.urls.dictionary_index, json={'data': {'attributes': payload}}
        )

        return SchemaModel(response.json()['data'])

    def register_dictionary(
        self,
        dataset_id,
        version,
        valid_as_of,
        fields,
        **kwargs,
    ):
        """
        Registers dictionary metadata for a dataset.

        :param str dataset_id: Id of the dataset for the dictionary.
        :param str version: A user assigned version name/number. It should be unique within the dataset.
        :param str valid_as_of: The date as of which the dictionary is active.
                               Expected format is YYYY-MM-DD.
        :param list[dict] fields: Non empty list of `Field` as described below.
        :param str type: Optional. Type of the dictionary. Defaults to `StructType`.
        :param list[dict] partitions: Optional. Non empty list of `Partition` as described below.
        :param str description: Optional. Description for the dictionary.

        .. code-block:: python

                # Field: Spark compatible
                {
                    "name": "field_a", 			# name of the column.
                    "type": "String", 			# string representation of the type of the column (might be another StructType if it is a nested type).
                    "nullable": True,  			# defaulted to True - A boolean indicating whether the field is nullable or not.
                    "metadata": None			# optional dictionary with metadata for this column.
                }

                # Partition:
                {
                    "name": "key1",
                    "type": "String"
                }

        :returns: The registered dictionary

        - **Sample**

        .. code-block:: python

                my_dictionary_fields = [
                            {
                                'name': 'field_1',
                                'type': 'String',
                                'nullable': False
                            },
                            {
                                'name': 'field_2',
                                'type': 'Double',
                                'nullable': False
                            },
                            {
                                'name': 'field_3',
                                'type': 'Int',
                                'nullable': True,
                                'metadata': {
                                    'some_key': 'some_value'
                                }
                            },
                        ]
                my_dictionary_partitions = [
                    {
                        'name': 'field_1',
                        'type': 'String'
                    }
                ]

                my_dictionary = client.register_dictionary(
                    "my-dataset-id",
                    version='1a',
                    valid_as_of='2018-10-31',
                    fields=my_dictionary_fields,
                    type='my-dictionary-type',
                    partitions=my_dictionary_partitions,
                    description="My dictionary description"
                )
        """
        payload = {
            'dataset_id': dataset_id,
            'version': version,
            'valid_as_of': valid_as_of,
            'type': kwargs.get('type', 'StructType'),
            'fields': fields,
        }

        payload.update(**kwargs)

        response = self.client.session.post(
            self.urls.dictionary_index, json={'data': {'attributes': payload}}
        )

        return SchemaModel(response.json()['data'])

    def register_spark_schema(
        self,
        dataset_id,
        version,
        valid_as_of,
        spark_schema_json,
        **kwargs
    ):
        """
        Registers dataframe schema for the datalake `dataset` for instances where data ingest pipelines make use of spark.

        :param str dataset_id: Id of the dataset for the schema.
        :param str version: A user assigned version name/number. It should be unique within the dataset.
        :param str valid_as_of: The date as of which the schema is active.
                               Expected format is YYYY-MM-DD.
        :param dict spark_schema_json: Json schema for the spark dataframe.
        :param list[dict] partitions: Optional. Non empty list of `Partition` as described below.
        :param str description: Optional. Description for the schema.

        .. code-block:: python

                # Partition:
                {
                    "name": "key1",
                    "type": "String"
                }

        :returns: The registered schema.

        - **Sample**

        .. code-block:: python

                # my_spark_dataframe: some spark dataframe with data being published in the data lake

                my_spark_schema_json = my_spark_dataframe.schema.jsonValue()

                my_schema = client.register_spark_schema(
                    "my-dataset-id",
                    version='1a',
                    valid_as_of='2018-10-31',
                    spark_schema_json=my_spark_schema_json,
                    description="My schema description"
                )
        """
        warnings.warn(
            '''
            `register_spark_schema` is deprecated. Please migrate this
            function to register_schema. There is no longer an
            difference in functionality.

            Please migrate this:

                client.register_spark_schema(
                    '1234',
                    version='1a',
                    valid_as_of='2000-01-01',
                    spark_schema_json={}
                )

            To:

                client.register_schema(
                    '1234',
                    version='1a',
                    valid_as_of='2000-01-01',
                    **spark_schema_json
                )
            ''',
            DeprecationWarning
        )

        payload = {
            'dataset_id': dataset_id,
            'version': version,
            'valid_as_of': valid_as_of,
        }

        payload.update(spark_schema_json)
        payload.update(kwargs)

        return self.register_dictionary(**payload)

    def get_dictionary(self, dataset_id, version=None):
        """
        Looks up dictionary for a dataset by version. In case version is not specified this will fetch dictionary version having the latest valid_as_of date.
        Throws exception if no dictionary is registered for the dataset.

        :param str dataset_id: The id of the dataset under which the dictionary is registered.
        :param str version: Optional. The version of the dictionary.

        :returns: The dictionary.

        - **Sample**

        .. code-block:: python

                # Fetch dictionary version '1a'
                dictionary = client.get_dictionary('my_dataset_id', version='1a')

                # Fetch the dictionary with the latest valid_as_of date
                latest_dictionary = client.get_dictionary('my_dataset_id')

        """

        if version:
            schema_old_api = self.client.session.get(
                self.urls.schema_instance_version.format(
                    id=dataset_id,
                    version=version
                )
            ).to_siren()

            schema_id = schema_old_api.schemaId

            schema = self.client.session.get(
                self.urls.dictionary_instance.format(id=schema_id)
            )
        else:
            schema = self.client.session.get(
                self.urls.dictionary_by_dataset_lastest.format(
                    id=dataset_id,
                    version=version
                )
            )

        return SchemaModel(schema.json()['data'])

    def get_dictionaries(self, dataset_id, count=100):
        """
        Returns a list of all dictionaries registered under the dataset. The list is sorted by dictionary valid_as_of date in descending order.

        :param str dataset_id: The id of the dataset.
        :param int count: Optional count of dictionaries to be returned. Defaults to 100.

        :returns: List of all dictionaries registered under the dataset sorted by valid_as_of date in descending order.

        - **Sample**

        .. code-block:: python

                my_dictionaries = client.get_dictionaries("my_dataset_id", count=10)
        """
        response = self.client.session.get(
            self.urls.dictionary_by_dataset.format(id=dataset_id)
        )

        return [
            SchemaModel(d) for d in
            response.json()['data']
        ][:count]  # will kill this silly count stuff ASAP

    def delete_dictionary(self, dataset_id, version):
        """

        Marks a dictionary version for a dataset as deleted.

        :param str dataset_id: The id of the dataset under which the dictionary is registered.
        :param str version: The version of the dictionary.

        :returns: None

        - **Sample**

        .. code-block:: python

                # Delete dictionary version '1a'
                client.delete_dictionary(dataset_id='my_dataset_id', version='1a')

        """
        schema = self.get_dictionary(dataset_id, version)
        self.client.session.delete(
            self.urls.dictionary_instance.format(id=schema.id)
        )

    def edit_dictionary(
        self,
        dataset_id,
        version,
        new_version=None,
        **kwargs
    ):
        """
        Updates schema metadata for a dataset.
        If a field is passed as ``None`` then the field will not be updated.

        :param str dataset_id: Id of the dataset for the schema.
        :param str version: Version of the schema being updated.
        :param str new_version: Optional. New version if to be updated. This is a user assigned version name/number. It should be unique within the dataset.
        :param str valid_as_of: Optional. The date as of which the schema is active.
                               Expected format is YYYY-MM-DD.
        :param list[dict] fields: Optional. If provided, a non empty list of `Field` as described below.
        :param str type: Optional. Type of the schema.
        :param list[dict] partitions: Optional. If provided, a non empty list of `Partition` as described below.
        :param str description: Optional. Description for the schema.

        .. code-block:: python

                # Field: Spark compatible
                {
                    "name": "field_a", 			# name of the column.
                    "type": "String", 			# string representation of the type of the column (might be another StructType if it is a nested type).
                    "nullable": True,  			# defaulted to True - A boolean indicating whether the field is nullable or not.
                    "metadata": None			# optional dictionary with metadata for this column.
                }

                # Partition:
                {
                    "name": "key1",
                    "type": "String"
                }

        :returns: The updated schema.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # Updating description and valid_as_of date for my schema
                my_updated_schema = client.edit_schema(
                    "my-dataset-id",
                    '1a',
                    valid_as_of='2018-11-05',
                    description="My updated schema description"
                )
        """
        schema = self.get_dictionary(dataset_id, version)

        payload = dict(kwargs)
        if new_version:
            payload['version'] = new_version

        response = self.client.session.patch(
            self.urls.dictionary_instance.format(id=schema.id),
            json={'data': {'attributes': payload}}
        )

        return SchemaModel(response.json()['data'])

    def delete_schema(self, *args, **kwargs):
        warnings.warn(
            '.delete_schema is deprecated. Please use .delete_dictionary',
            DeprecationWarning
        )

        return self.delete_dictionary(*args, **kwargs)

    def edit_schema(self, *args, **kwargs):
        warnings.warn(
            '.edit_schema is deprecated. Please use .edit_dictionary',
            DeprecationWarning
        )

        return self.edit_dictionary(*args, **kwargs)

    def get_schema(self, *args, **kwargs):
        warnings.warn(
            '.get_schema is deprecated. Please use .get_dictionary',
            DeprecationWarning
        )
        return self.get_dictionary(*args, **kwargs)

    def get_schemas(self, *args, **kwargs):
        warnings.warn(
            '.get_schemas is deprecated. Please use .get_dictionaries',
            DeprecationWarning
        )

        return self.get_dictionaries(*args, **kwargs)

    def register_schema(self, *args, **kwargs):
        warnings.warn(
            '.register_schema is deprecated. Please use .register_dictionary',
            DeprecationWarning
        )

        return self.register_dictionary(*args, **kwargs)
