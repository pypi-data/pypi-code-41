import math
from dataclasses import dataclass

def task_divide(data, granularity):
    l = len(data)
    if l < granularity:
        return [data]
    n = int(len(data) / granularity)
    return [data[i::n] for i in range(n)]


@dataclass(init=True, repr=True, frozen=True)
class Task:
    task_id: str
    branch_id: str
    data_type: str
    position: int
    properties: dict
    end_condition: dict


