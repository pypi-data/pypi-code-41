import logging

from dli.client.components import SirenComponent
from dli.client.components.urls import autoreg_urls
from dli.siren import siren_to_entity, siren_to_dict


class AutoRegMetadata(SirenComponent):

    def set_auto_registration_metadata(
        self,
        dataset_id,
        path_template,
        name_template,
        as_of_date_template,
        active,
        sns_topic_for_s3_events,
        handle_files=False,
        has_auto_registry_failure_notifications=True
    ):
        """
        Submit a request to set up the auto registration metadata for a dataset.

        See description for each parameter, and whether they are optional or mandatory.

        :param str dataset_id: Dataset ID for which the auto registration metadata is being set up.
        :param str path_template: Path template for the files stored under the dataset.
        :param str name_template: Name template for the datafiles registered under the dataset.
        :param str as_of_date_template: As of date template for the datafiles registered under the dataset.
        :param bool active: Flag to indicate the auto registration status of the dataset
                            i.e. True => Active, False => Inactive or disabled
        :param str sns_topic_for_s3_events: Name of SNS topic where the S3 notification events are published when
                            files are added, updated or deleted from the S3 bucket for this dataset.
        :param bool handle_files: Optional. Flag to indicate whether the individual files (for e.g. parquet part files
                                    in case of a parquet dataset) are to be registered under the datafile for the dataset. Defaults to false.
        :param bool has_auto_registry_failure_notifications: Optional. Controls whether auto-registry sends email notifications on error. Defaults to true.
        :returns: Created auto registration metadata object.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # For example if the files for dataset id `xyz` are stored in the s3 bucket along
                `region=US/as_of_date=2019-02-18`

                auto_reg_metadata = client.set_auto_registration_metadata(
                    dataset_id="xyz",
                    path_template="region={{ region }}/as_of_date={{ year }}-{{ month }}-{{ day }}",
                    name_template="Datafile_name_{{ region }}_{{ year }}-{{ month }}-{{ day }}",
                    as_of_date_template="{{ year }}-{{ month }}-{{ day }}",
                    active=True,
                    sns_topic_for_s3_events='s3-notifications-sns-topic'
                )
        """
        dataset = self.get_dataset(id=dataset_id)

        fields = {
            'datasetId': dataset.dataset_id,
            'pathTemplate': path_template,
            'nameTemplate': name_template,
            'asOfDateTemplate': as_of_date_template,
            'active': active,
            'snsTopicForS3Events': sns_topic_for_s3_events,
            'handlePartFiles': handle_files,
            "hasAutoRegistryFailureNotifications": has_auto_registry_failure_notifications
        }

        payload = {k: v for k, v in fields.items() if v is not None}
        return siren_to_entity(
            self.session.post(
                autoreg_urls.autoreg_index, json=payload
            ).to_siren()
        )

    def get_auto_registration_metadata(self, dataset_id=None, auto_reg_metadata_id=None):
        """
        Fetches the auto registration metadata for a dataset.

        :param str dataset_id: Optional. The dataset id for which auto registration metadata is being fetched.
                            Either this or auto_reg_metadata_id is required for the look up
        :param str auto_reg_metadata_id: Optional. The id of the auto registration metadata.
                            Either this or dataset_id is required for the look up
        :returns: The auto registration metadata object.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # Look up by dataset id
                auto_reg_metadata = client.get_auto_registration_metadata('my_dataset_id')
                # or equivalent
                auto_reg_metadata = client.auto_reg_metadata(dataset_id='my_dataset_id')


                # If auto reg metadata id is known
                auto_reg_metadata = client.auto_reg_metadata(auto_reg_metadata_id='my_auto_reg_id')
        """

        if dataset_id and auto_reg_metadata_id:
            return siren_to_entity(
                self._get_auto_reg_metadata(
                    auto_reg_metadata_id=auto_reg_metadata_id,
                    dataset_id=dataset_id
                )
            )
        elif auto_reg_metadata_id:
            return siren_to_entity(
                self._get_auto_reg_metadata(
                    auto_reg_metadata_id=auto_reg_metadata_id
                )
            )
        elif dataset_id:
            return siren_to_entity(
                self._get_auto_reg_metadata(
                    dataset_id=dataset_id
                )
            )

        raise ValueError("Either dataset id or auto reg metadata id must be specified to look up auto registration details for the dataset")

    def _get_auto_reg_metadata(self, **kwargs):
        response = self.session.get(
            autoreg_urls.autoreg_index, params=kwargs
        )

        return response.to_siren()

    def edit_auto_registration_metadata(
        self,
        auto_reg_metadata_id,
        path_template=None,
        name_template=None,
        as_of_date_template=None,
        active=None,
        sns_topic_for_s3_events=None,
        handle_files=None,
        has_auto_registry_failure_notifications=None
    ):
        """
        Edits existing auto registration metadata for a dataset.
        Fields passed as ``None`` will retain their original value.

        :param str auto_reg_metadata_id: The id of the auto registration metadata we want to modify.
        :param str path_template: Optional. Path template for the files stored under the dataset.
        :param str name_template: Optional. Name template for the datafiles registered under the dataset.
        :param str as_of_date_template: Optional. As of date template for the datafiles registered under the dataset.
        :param bool active: Optional. Boolean flag to indicate the auto registration status of the dataset
                            i.e. True => Active, False => Inactive or disabled
        :param str sns_topic_for_s3_events: Optional. Name of SNS topic where the S3 notification events are published when
                            files are added, updated or deleted from the S3 bucket for this dataset.
        :param bool handle_files: Optional. Flag to indicate whether the individual files (for e.g. parquet part files
                                    in case of a parquet dataset) are to be registered under the datafile for the dataset.
        :param bool has_auto_registry_failure_notifications: Optional. Controls whether auto-registry sends email notifications on error.
        :returns: Updated auto registration metadata object
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # For example edit metadata to make it inactive

                updated_auto_reg_metadata = client.edit_auto_registration_metadata(
                    auto_reg_metadata_id="test-auto-reg-metadata-id",
                    active=False
                )
        """
        auto_reg_metadata = self._get_auto_reg_metadata(auto_reg_metadata_id=auto_reg_metadata_id)

        fields = {
            'datasetId': auto_reg_metadata.datasetId,
            'pathTemplate': path_template,
            'nameTemplate': name_template,
            'asOfDateTemplate': as_of_date_template,
            'active': active,
            'snsTopicForS3Events': sns_topic_for_s3_events,
            'handlePartFiles': handle_files,
            "hasAutoRegistryFailureNotifications": has_auto_registry_failure_notifications
        }

        # clean up any unknown fields, and update the entity
        auto_reg_metadata_dict = siren_to_dict(auto_reg_metadata)
        for key in list(auto_reg_metadata_dict.keys()):
            if key not in fields:
                del auto_reg_metadata_dict[key]

        payload = {k: v for k, v in fields.items() if v is not None}
        auto_reg_metadata_dict.update(payload)

        # perform the update and return the resulting entity
        response = self.session.put(
            autoreg_urls.autoreg_instance.format(id=auto_reg_metadata_id),
            json=auto_reg_metadata_dict
        )

        return siren_to_entity(response.to_siren())

    def delete_auto_registration_metadata(self, auto_reg_metadata_id):
        """
        Marks auto registration metadata as deleted.

        :param str auto_reg_metadata_id: the id for the metadata we want to delete.

        :returns: None
        - **Sample**

        .. code-block:: python

                client.delete_auto_registration_metadata(auto_reg_metadata_id)
        """
        self.session.delete(
            autoreg_urls.autoreg_instance.format(id=auto_reg_metadata_id),
        )
