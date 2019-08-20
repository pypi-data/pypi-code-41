# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class UnitResponse(Model):
    """UnitResponse.

    :param unit_id:
    :type unit_id: int
    :param unit_code:
    :type unit_code: str
    :param unit_info:
    :type unit_info: str
    :param unit_type:
    :type unit_type: ~energycap.sdk.models.UnitType
    """

    _attribute_map = {
        'unit_id': {'key': 'unitId', 'type': 'int'},
        'unit_code': {'key': 'unitCode', 'type': 'str'},
        'unit_info': {'key': 'unitInfo', 'type': 'str'},
        'unit_type': {'key': 'unitType', 'type': 'UnitType'},
    }

    def __init__(self, unit_id=None, unit_code=None, unit_info=None, unit_type=None):
        super(UnitResponse, self).__init__()
        self.unit_id = unit_id
        self.unit_code = unit_code
        self.unit_info = unit_info
        self.unit_type = unit_type
