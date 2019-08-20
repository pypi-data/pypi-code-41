# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class BillActionVoid(Model):
    """BillActionVoid.

    :param ids:  <span class='property-internal'>Cannot be Empty</span>
    :type ids: list[int]
    :param void:
    :type void: bool
    """

    _attribute_map = {
        'ids': {'key': 'ids', 'type': '[int]'},
        'void': {'key': 'void', 'type': 'bool'},
    }

    def __init__(self, ids=None, void=None):
        super(BillActionVoid, self).__init__()
        self.ids = ids
        self.void = void
