# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class PlaceDigestSavingsYearlyResponseResults(Model):
    """PlaceDigestSavingsYearlyResponseResults.

    :param year: Year
    :type year: str
    :param batcc_total_cost: BATCC (Baseline Adjusted to Current Conditions)
     Total Cost
    :type batcc_total_cost: float
    :param total_cost: Total Cost
    :type total_cost: float
    :param savings_total_cost: Savings Total Cost = BATCCTotalCost - TotalCost
    :type savings_total_cost: float
    :param batcc_global_use: BATCC (Baseline Adjusted to Current Conditions)
     Global Use
    :type batcc_global_use: float
    :param global_use: GlobalUse
    :type global_use: float
    :param savings_global_use: Savings Global Use = BATCCGlobalUse - GlobalUse
    :type savings_global_use: float
    """

    _attribute_map = {
        'year': {'key': 'year', 'type': 'str'},
        'batcc_total_cost': {'key': 'batccTotalCost', 'type': 'float'},
        'total_cost': {'key': 'totalCost', 'type': 'float'},
        'savings_total_cost': {'key': 'savingsTotalCost', 'type': 'float'},
        'batcc_global_use': {'key': 'batccGlobalUse', 'type': 'float'},
        'global_use': {'key': 'globalUse', 'type': 'float'},
        'savings_global_use': {'key': 'savingsGlobalUse', 'type': 'float'},
    }

    def __init__(self, year=None, batcc_total_cost=None, total_cost=None, savings_total_cost=None, batcc_global_use=None, global_use=None, savings_global_use=None):
        super(PlaceDigestSavingsYearlyResponseResults, self).__init__()
        self.year = year
        self.batcc_total_cost = batcc_total_cost
        self.total_cost = total_cost
        self.savings_total_cost = savings_total_cost
        self.batcc_global_use = batcc_global_use
        self.global_use = global_use
        self.savings_global_use = savings_global_use
