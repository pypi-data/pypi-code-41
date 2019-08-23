from typing import List
from .CashFlow import CashFlow, CSEncoder

import json
from json import JSONEncoder

class BankStatement(object):
    def __init__(self):
        self.inflows: List[CashFlow] = []
        self.outflows: List[CashFlow] = []

    def __repr__(self):
        bs = 'BankStatement:'
            
        bs += '\n\n\t = Inflows: = \n\t'
        for cs in self.inflows:
            bs += '\n' + str(cs)
        bs += '\n\n\t = Outflows: =\n\t'
        for cs in self.outflows:
            bs += '\n' + str(cs)
        return bs

    def __del__(self):
        self.inflows = None
        self.outflows = None

    def merge(self, other):
        self.inflows.append(other.inflows)
        self.outflows.append(other.outflows)

class BSEncoder(JSONEncoder):
    def default(self, o):
        print(o)
        if isinstance(o, BankStatement):
            bs = []

            for cs in o.inflows:
                bs.append(json.dumps(cs, cls=CSEncoder))
            for cs in o.outflows:
                bs.append(json.dumps(cs, cls=CSEncoder))

            root = {}
            root['BankStatement'] = bs
            return root
        