from enum import unique
import uuid

from arps.core.simulator.resource import Resource
from arps.core.resource_category import ResourceCategory, ValueType


@unique
class DummyCategory(ResourceCategory):
    ResourceA = (uuid.uuid1(), (0, 100), ValueType.numerical,
                 lambda value: int(value))
    ResourceB = (uuid.uuid1(), ('ON', 'OFF'), ValueType.descriptive)
    Comm = (uuid.uuid1(), (0, float('inf')), ValueType.numerical,
            lambda value: int(value))
    Any = (uuid.uuid1(), None, ValueType.complex)

class ResourceA(Resource):

    def __init__(self, *, environment_identifier, identifier, value=None):
        super().__init__(environment_identifier=environment_identifier,
                         identifier=identifier, value=value, category=DummyCategory.ResourceA)

    def _affect_resource(self, epoch):
        if not self._affected_resource:
            return

        new_value = 'ON' if self.value > 30 else 'OFF'
        if self._affected_resource.value == new_value:
            return

        self._affected_resource.value = (new_value,
                                         epoch,
                                         self.identifier,
                                         Resource.EvtType.rsc_indirect)

class ResourceB(Resource):

    def __init__(self, *, environment_identifier, identifier, value=None):
        super().__init__(environment_identifier=environment_identifier,
                         identifier=identifier, value=value, category=DummyCategory.ResourceB)



class ReceivedMessagesResource(Resource):

    def __init__(self, *, environment_identifier, identifier):
        super().__init__(environment_identifier=environment_identifier,
                         identifier=identifier, value=0,
                         category=DummyCategory.Comm)
