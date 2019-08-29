from pyopencell.responses.action_status import ActionStatus
from pyopencell.responses.paging import Paging


class PagedResponse():
    paging = {}
    action_status = {}

    def __init__(self, cls, **kwargs):
        self.paging = Paging(**kwargs.get("paging"))
        self.action_status = ActionStatus(**kwargs.get("actionStatus"))

        instances = []

        for instance in kwargs[cls._name]:
            instances.append(cls.items_resource_class(**instance))

        setattr(self, cls._name, instances)
