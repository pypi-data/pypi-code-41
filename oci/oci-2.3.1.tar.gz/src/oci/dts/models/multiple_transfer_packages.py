# coding: utf-8
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class MultipleTransferPackages(object):
    """
    MultipleTransferPackages model.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new MultipleTransferPackages object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param transfer_package_objects:
            The value to assign to the transfer_package_objects property of this MultipleTransferPackages.
        :type transfer_package_objects: list[TransferPackageSummary]

        """
        self.swagger_types = {
            'transfer_package_objects': 'list[TransferPackageSummary]'
        }

        self.attribute_map = {
            'transfer_package_objects': 'transferPackageObjects'
        }

        self._transfer_package_objects = None

    @property
    def transfer_package_objects(self):
        """
        Gets the transfer_package_objects of this MultipleTransferPackages.
        List of TransferPackage summary's


        :return: The transfer_package_objects of this MultipleTransferPackages.
        :rtype: list[TransferPackageSummary]
        """
        return self._transfer_package_objects

    @transfer_package_objects.setter
    def transfer_package_objects(self, transfer_package_objects):
        """
        Sets the transfer_package_objects of this MultipleTransferPackages.
        List of TransferPackage summary's


        :param transfer_package_objects: The transfer_package_objects of this MultipleTransferPackages.
        :type: list[TransferPackageSummary]
        """
        self._transfer_package_objects = transfer_package_objects

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
