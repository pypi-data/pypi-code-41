from enum import Enum
from datetime import datetime

from json import JSONEncoder

class CashFlowType(Enum):
    DEBIT = 1
    CREDIT = 2

class CashFlow(object):
    def __init__(self,
                name: str = 'N/A',
                flowType: CashFlowType = CashFlowType.DEBIT,
                value: float = 0.0,
                date: str = 'N/A'):
        self.name = name
        self.flowType = flowType
        self.value = value
        self.date = date

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.name.strip() == other.name.strip() and
            self.value == other.value and
            self.date == other.date
        )

    def __repr__(self):
        return 'CashFlow: \
                \n\tName: {} \
                \n\tType: {} \
                \n\tValue: {} \
                \n\tDate: {}'.format(self.name,
                                    self.flowType.name, 
                                    self.value,
                                    self.date)

class CSEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, CashFlow):
            return {'CashFlow': {
                'Name': str(o.name),
                'Value': str(o.value),
                'Date': str(o.date)
            }}