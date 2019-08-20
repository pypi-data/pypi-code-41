# coding: utf-8
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.


from oci.util import formatted_flat_dict, NONE_SENTINEL, value_allowed_none_or_none_sentinel  # noqa: F401
from oci.decorators import init_model_state_from_kwargs


@init_model_state_from_kwargs
class WaasPolicyCustomProtectionRuleSummary(object):
    """
    Summary information about a Custom Protection rule.
    """

    #: A constant which can be used with the action property of a WaasPolicyCustomProtectionRuleSummary.
    #: This constant has a value of "DETECT"
    ACTION_DETECT = "DETECT"

    #: A constant which can be used with the action property of a WaasPolicyCustomProtectionRuleSummary.
    #: This constant has a value of "BLOCK"
    ACTION_BLOCK = "BLOCK"

    def __init__(self, **kwargs):
        """
        Initializes a new WaasPolicyCustomProtectionRuleSummary object with values from keyword arguments.
        The following keyword arguments are supported (corresponding to the getters/setters of this class):

        :param id:
            The value to assign to the id property of this WaasPolicyCustomProtectionRuleSummary.
        :type id: str

        :param display_name:
            The value to assign to the display_name property of this WaasPolicyCustomProtectionRuleSummary.
        :type display_name: str

        :param action:
            The value to assign to the action property of this WaasPolicyCustomProtectionRuleSummary.
            Allowed values for this property are: "DETECT", "BLOCK", 'UNKNOWN_ENUM_VALUE'.
            Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.
        :type action: str

        :param mod_security_rule_ids:
            The value to assign to the mod_security_rule_ids property of this WaasPolicyCustomProtectionRuleSummary.
        :type mod_security_rule_ids: list[str]

        """
        self.swagger_types = {
            'id': 'str',
            'display_name': 'str',
            'action': 'str',
            'mod_security_rule_ids': 'list[str]'
        }

        self.attribute_map = {
            'id': 'id',
            'display_name': 'displayName',
            'action': 'action',
            'mod_security_rule_ids': 'modSecurityRuleIds'
        }

        self._id = None
        self._display_name = None
        self._action = None
        self._mod_security_rule_ids = None

    @property
    def id(self):
        """
        Gets the id of this WaasPolicyCustomProtectionRuleSummary.
        The `OCID`__ of the Custom Protection rule.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :return: The id of this WaasPolicyCustomProtectionRuleSummary.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this WaasPolicyCustomProtectionRuleSummary.
        The `OCID`__ of the Custom Protection rule.

        __ https://docs.cloud.oracle.com/Content/General/Concepts/identifiers.htm


        :param id: The id of this WaasPolicyCustomProtectionRuleSummary.
        :type: str
        """
        self._id = id

    @property
    def display_name(self):
        """
        Gets the display_name of this WaasPolicyCustomProtectionRuleSummary.
        The user-friendly name of the Custom Protection rule.


        :return: The display_name of this WaasPolicyCustomProtectionRuleSummary.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this WaasPolicyCustomProtectionRuleSummary.
        The user-friendly name of the Custom Protection rule.


        :param display_name: The display_name of this WaasPolicyCustomProtectionRuleSummary.
        :type: str
        """
        self._display_name = display_name

    @property
    def action(self):
        """
        Gets the action of this WaasPolicyCustomProtectionRuleSummary.
        The action to take when the Custom Protection rule is triggered.

        Allowed values for this property are: "DETECT", "BLOCK", 'UNKNOWN_ENUM_VALUE'.
        Any unrecognized values returned by a service will be mapped to 'UNKNOWN_ENUM_VALUE'.


        :return: The action of this WaasPolicyCustomProtectionRuleSummary.
        :rtype: str
        """
        return self._action

    @action.setter
    def action(self, action):
        """
        Sets the action of this WaasPolicyCustomProtectionRuleSummary.
        The action to take when the Custom Protection rule is triggered.


        :param action: The action of this WaasPolicyCustomProtectionRuleSummary.
        :type: str
        """
        allowed_values = ["DETECT", "BLOCK"]
        if not value_allowed_none_or_none_sentinel(action, allowed_values):
            action = 'UNKNOWN_ENUM_VALUE'
        self._action = action

    @property
    def mod_security_rule_ids(self):
        """
        Gets the mod_security_rule_ids of this WaasPolicyCustomProtectionRuleSummary.
        The list of the ModSecurity rule IDs that apply to this protection rule. For more information about ModSecurity's open source WAF rules, see `Mod Security's documentation`__.

        __ https://www.modsecurity.org/CRS/Documentation/index.html


        :return: The mod_security_rule_ids of this WaasPolicyCustomProtectionRuleSummary.
        :rtype: list[str]
        """
        return self._mod_security_rule_ids

    @mod_security_rule_ids.setter
    def mod_security_rule_ids(self, mod_security_rule_ids):
        """
        Sets the mod_security_rule_ids of this WaasPolicyCustomProtectionRuleSummary.
        The list of the ModSecurity rule IDs that apply to this protection rule. For more information about ModSecurity's open source WAF rules, see `Mod Security's documentation`__.

        __ https://www.modsecurity.org/CRS/Documentation/index.html


        :param mod_security_rule_ids: The mod_security_rule_ids of this WaasPolicyCustomProtectionRuleSummary.
        :type: list[str]
        """
        self._mod_security_rule_ids = mod_security_rule_ids

    def __repr__(self):
        return formatted_flat_dict(self)

    def __eq__(self, other):
        if other is None:
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
