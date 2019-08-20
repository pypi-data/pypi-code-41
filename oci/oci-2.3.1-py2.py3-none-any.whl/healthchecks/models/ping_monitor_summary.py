# coding: utf-8
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class PingMonitorSummary(object):
    """
    This model contains all of the mutable and immutable summary properties for an HTTP monitor.
    """

    #: A constant which can be used with the protocol property of a PingMonitorSummary.
    #: This constant has a value of "ICMP"
    PROTOCOL_ICMP = "ICMP"

    #: A constant which can be used with the protocol property of a PingMonitorSummary.
    #: This constant has a value of "TCP"
    PROTOCOL_TCP = "TCP"

    def __init__(self, **kwargs):
        """
        Initializes a new PingMonitorSummary object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this PingMonitorSummary.
        :type id: str

        :param results_url:
            The value to assign to the results_url property of this PingMonitorSummary.
        :type results_url: str

        :param compartment_id:
            The value to assign to the compartment_id property of this PingMonitorSummary.
        :type compartment_id: str

        :param display_name:
            The value to assign to the display_name property of this PingMonitorSummary.
        :type display_name: str

        :param interval_in_seconds:
            The value to assign to the interval_in_seconds property of this PingMonitorSummary.
        :type interval_in_seconds: int

        :param is_enabled:
            The value to assign to the is_enabled property of this PingMonitorSummary.
        :type is_enabled: bool

        :param freeform_tags:
            The value to assign to the freeform_tags property of this PingMonitorSummary.
        :type freeform_tags: dict(str, str)

        :param defined_tags:
            The value to assign to the defined_tags property of this PingMonitorSummary.
        :type defined_tags: dict(str, dict(str, object))

        :param protocol:
            The value to assign to the protocol property of this PingMonitorSummary.
            Allowed values for this property are: "ICMP", "TCP", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type protocol: str

        """
        self.swagger_types = {
            'id': 'str',
            'results_url': 'str',
            'compartment_id': 'str',
            'display_name': 'str',
            'interval_in_seconds': 'int',
            'is_enabled': 'bool',
            'freeform_tags': 'dict(str, str)',
            'defined_tags': 'dict(str, dict(str, object))',
            'protocol': 'str'
        }

        self.attribute_map = {
            'id': 'id',
            'results_url': 'resultsUrl',
            'compartment_id': 'compartmentId',
            'display_name': 'displayName',
            'interval_in_seconds': 'intervalInSeconds',
            'is_enabled': 'isEnabled',
            'freeform_tags': 'freeformTags',
            'defined_tags': 'definedTags',
            'protocol': 'protocol'
        }

        self._id = None
        self._results_url = None
        self._compartment_id = None
        self._display_name = None
        self._interval_in_seconds = None
        self._is_enabled = None
        self._freeform_tags = None
        self._defined_tags = None
        self._protocol = None

    @property
    def id(self):
        """
        Gets the id of this PingMonitorSummary.
        The OCID of the resource.


        :return: The id of this PingMonitorSummary.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this PingMonitorSummary.
        The OCID of the resource.


        :param id: The id of this PingMonitorSummary.
        :type: str
        """
        self._id = id

    @property
    def results_url(self):
        """
        Gets the results_url of this PingMonitorSummary.
        A URL for fetching the probe results.


        :return: The results_url of this PingMonitorSummary.
        :rtype: str
        """
        return self._results_url

    @results_url.setter
    def results_url(self, results_url):
        """
        Sets the results_url of this PingMonitorSummary.
        A URL for fetching the probe results.


        :param results_url: The results_url of this PingMonitorSummary.
        :type: str
        """
        self._results_url = results_url

    @property
    def compartment_id(self):
        """
        Gets the compartment_id of this PingMonitorSummary.
        The OCID of the compartment.


        :return: The compartment_id of this PingMonitorSummary.
        :rtype: str
        """
        return self._compartment_id

    @compartment_id.setter
    def compartment_id(self, compartment_id):
        """
        Sets the compartment_id of this PingMonitorSummary.
        The OCID of the compartment.


        :param compartment_id: The compartment_id of this PingMonitorSummary.
        :type: str
        """
        self._compartment_id = compartment_id

    @property
    def display_name(self):
        """
        Gets the display_name of this PingMonitorSummary.
        A user-friendly and mutable name suitable for display in a user interface.


        :return: The display_name of this PingMonitorSummary.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this PingMonitorSummary.
        A user-friendly and mutable name suitable for display in a user interface.


        :param display_name: The display_name of this PingMonitorSummary.
        :type: str
        """
        self._display_name = display_name

    @property
    def interval_in_seconds(self):
        """
        Gets the interval_in_seconds of this PingMonitorSummary.
        The monitor interval in seconds. Valid values: 10, 30, and 60.


        :return: The interval_in_seconds of this PingMonitorSummary.
        :rtype: int
        """
        return self._interval_in_seconds

    @interval_in_seconds.setter
    def interval_in_seconds(self, interval_in_seconds):
        """
        Sets the interval_in_seconds of this PingMonitorSummary.
        The monitor interval in seconds. Valid values: 10, 30, and 60.


        :param interval_in_seconds: The interval_in_seconds of this PingMonitorSummary.
        :type: int
        """
        self._interval_in_seconds = interval_in_seconds

    @property
    def is_enabled(self):
        """
        Gets the is_enabled of this PingMonitorSummary.
        Enables or disables the monitor. Set to 'true' to launch monitoring.


        :return: The is_enabled of this PingMonitorSummary.
        :rtype: bool
        """
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, is_enabled):
        """
        Sets the is_enabled of this PingMonitorSummary.
        Enables or disables the monitor. Set to 'true' to launch monitoring.


        :param is_enabled: The is_enabled of this PingMonitorSummary.
        :type: bool
        """
        self._is_enabled = is_enabled

    @property
    def freeform_tags(self):
        """
        Gets the freeform_tags of this PingMonitorSummary.
        Free-form tags for this resource. Each tag is a simple key-value pair with no
        predefined name, type, or namespace.  For more information,
        see `Resource Tags`__.
        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/Content/General/Concepts/resourcetags.htm


        :return: The freeform_tags of this PingMonitorSummary.
        :rtype: dict(str, str)
        """
        return self._freeform_tags

    @freeform_tags.setter
    def freeform_tags(self, freeform_tags):
        """
        Sets the freeform_tags of this PingMonitorSummary.
        Free-form tags for this resource. Each tag is a simple key-value pair with no
        predefined name, type, or namespace.  For more information,
        see `Resource Tags`__.
        Example: `{\"Department\": \"Finance\"}`

        __ https://docs.cloud.oracle.com/Content/General/Concepts/resourcetags.htm


        :param freeform_tags: The freeform_tags of this PingMonitorSummary.
        :type: dict(str, str)
        """
        self._freeform_tags = freeform_tags

    @property
    def defined_tags(self):
        """
        Gets the defined_tags of this PingMonitorSummary.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/Content/General/Concepts/resourcetags.htm


        :return: The defined_tags of this PingMonitorSummary.
        :rtype: dict(str, dict(str, object))
        """
        return self._defined_tags

    @defined_tags.setter
    def defined_tags(self, defined_tags):
        """
        Sets the defined_tags of this PingMonitorSummary.
        Defined tags for this resource. Each key is predefined and scoped to a namespace.
        For more information, see `Resource Tags`__.
        Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`

        __ https://docs.cloud.oracle.com/Content/General/Concepts/resourcetags.htm


        :param defined_tags: The defined_tags of this PingMonitorSummary.
        :type: dict(str, dict(str, object))
        """
        self._defined_tags = defined_tags

    @property
    def protocol(self):
        """
        Gets the protocol of this PingMonitorSummary.
        Allowed values for this property are: "ICMP", "TCP", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The protocol of this PingMonitorSummary.
        :rtype: str
        """
        return self._protocol

    @protocol.setter
    def protocol(self, protocol):
        """
        Sets the protocol of this PingMonitorSummary.

        :param protocol: The protocol of this PingMonitorSummary.
        :type: str
        """
        allowed_values = ["ICMP", "TCP"]
        if not value_allowed_none_or_none_sentinel(protocol, allowed_values):
            protocol = 'UNKNOWN_ENUM_VALUE'
        self._protocol = protocol

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
