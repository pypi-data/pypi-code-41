# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class BillsOverdueFromVendorResponse(Model):
    """BillsOverdueFromVendorResponse.

    :param account:
    :type account: ~energycap.sdk.models.AccountChild
    :param cost_center:
    :type cost_center: ~energycap.sdk.models.CostCenterChild
    :param end_date:
    :type end_date: datetime
    :param direct_cost:
    :type direct_cost: float
    :param days:
    :type days: int
    :param gap_days:
    :type gap_days: int
    :param cost_unit: The cost unit of measure
    :type cost_unit: ~energycap.sdk.models.UnitChild
    """

    _attribute_map = {
        'account': {'key': 'account', 'type': 'AccountChild'},
        'cost_center': {'key': 'costCenter', 'type': 'CostCenterChild'},
        'end_date': {'key': 'endDate', 'type': 'iso-8601'},
        'direct_cost': {'key': 'directCost', 'type': 'float'},
        'days': {'key': 'days', 'type': 'int'},
        'gap_days': {'key': 'gapDays', 'type': 'int'},
        'cost_unit': {'key': 'costUnit', 'type': 'UnitChild'},
    }

    def __init__(self, account=None, cost_center=None, end_date=None, direct_cost=None, days=None, gap_days=None, cost_unit=None):
        super(BillsOverdueFromVendorResponse, self).__init__()
        self.account = account
        self.cost_center = cost_center
        self.end_date = end_date
        self.direct_cost = direct_cost
        self.days = days
        self.gap_days = gap_days
        self.cost_unit = cost_unit
